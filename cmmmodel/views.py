# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction, IntegrityError

from django.http import Http404
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.conf import settings
from django.utils import timezone

from scene.models import Scene
from scene.statusResponse import Status as sts

from scene.sceneExceptions import OsirisException
from cmmmodel.models import ModelExecutionHistory, Model, ModelExecutionQueue
from scene.views.InputModel import InputModel

import paramiko
import os


class EnqueuedModelException(Exception):
    pass


class ModelIsRunningException(Exception):
    pass

class Run(View):
    """ run model on cmm cluster """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Run, self).dispatch(request, *args, **kwargs)

    def runModel(self, user, scene_id, model_id, next_model_ids):
        """ connect to cluster server and run model """
        print(scene_id, model_id, next_model_ids)

        response = {}
        try:
            key_path = os.path.join(settings.KEY_DIR, 'ssh_key')
            model_obj = Model.objects.get(id=model_id)

            # when is called from cluster to run next model
            if user is None:
                scene_obj = Scene.objects.get(id=scene_id)
            else:
                scene_obj = Scene.objects.get(user=user, id=scene_id)

            # if model you try to run is enqueued, don´t run and notify to user
            if ModelExecutionQueue.objects.filter(modelExecutionHistory__scene=scene_obj, model_id=model_id).exists():
                raise EnqueuedModelException
            elif ModelExecutionHistory.objects.filter(scene=scene_obj, model_id=model_id,
                                                      status=ModelExecutionHistory.RUNNING).exists():
                raise ModelIsRunningException

            # create ssh connection
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            k = paramiko.RSAKey.from_private_key_file(key_path)
            client.connect(hostname=settings.CLUSTER_URL, username=settings.CLUSTER_USER, pkey=k)

            # run model
            input = InputModel(scene_id, model_id).get_input()
            responseScript = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saveJobResponse.py')
            command = "sbatch osiris/{} {} {} {}".format(model_obj.clusterFile, settings.SERVER_IP, responseScript,
                                                         settings.PYTHON_COMMAND, input)
            stdin, stdout, stderr = client.exec_command(command)

            job_number = None
            # save job number
            for line in stdout:
                job_number = int(line.strip('\n').split(" ")[3])

            if job_number == None:
                status = ModelExecutionHistory.ERROR_TO_START
            else:
                status = ModelExecutionHistory.RUNNING

            meh = ModelExecutionHistory.objects.create(scene=scene_obj, model=model_obj, start=timezone.now(),
                                                 status=status, jobNumber=job_number, error=stderr.read())
            print("hola", job_number, command, meh, stderr.read())
            for model_id in next_model_ids:
                ModelExecutionQueue.objects.create(modelExecutionHistory=meh, model_id=model_id)
            # close ssh connection
            client.close()

            sts.getJsonStatus(sts.OK, response)
        except Scene.DoesNotExist:
            sts.getJsonStatus(sts.SCENE_DOES_NOT_EXISTS_ERROR, response)
        except EnqueuedModelException:
            sts.getJsonStatus(sts.ENQUEUED_MODEL_ERROR, response)
        except ModelIsRunningException:
            sts.getJsonStatus(sts.MODEL_IS_RUNNING_ERROR, response)
        #except:
        #    Http404()

        return response

    def post(self, request):
        """  """
        scene_id = int(request.POST.get("sceneId"))
        model_id = int(request.POST.get("modelId"))
        next_model_ids = [int(id) for id in request.POST.getlist("nextModelIds[]")]

        response = self.runModel(request.user, scene_id, model_id, next_model_ids)

        return JsonResponse(response, safe=False)


class Stop(View):
    """ Stop execution of a model on cmm cluster """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Stop, self).dispatch(request, *args, **kwargs)

    def post(self, request, stepId, sceneId):
        """ validate and update data in server """

        stepId = int(stepId)
        sceneId = int(sceneId)

        scene_obj = Scene.objects.prefetch_related("metroline_set__metrostation_set",
                       "metroline_set__metrodepot_set", "operationperiod_set").\
                       get(user=request.user, id=sceneId)
        response = {}
        try:
            with transaction.atomic():
                pass
        except IntegrityError as e:
            sts.getJsonStatus(sts.EXCEL_ERROR, response)
            response["status"]["message"] = str(e)
        except OsirisException as e:
            response.update(e.get_status_response())

        return JsonResponse(response, safe=False)


class Status(View):
    """ Give the information of all model for scene """

    def resume_status(self, scene_obj):
        """  """
        model_list = Model.objects.all().order_by("id")
        model_status_list = []
        for model in model_list:
            model_status = model.get_dictionary()
            model_instance = ModelExecutionHistory.objects.filter(scene=scene_obj, model=model). \
                order_by("-start").first()
            if scene_obj.currentStep < 5:
                status = "disabled"
            elif model_instance is not None:
                if model_instance.status == ModelExecutionHistory.RUNNING:
                    status = "running"
                else:
                    status = "available"
                # check its queue
                model_status["lastExecutionInfo"] = model_instance.get_dictionary()
            else:
                status = "available"

            model_status["status"] = status
            model_status_list.append(model_status)

        return model_status_list

    def get(self, request):

        scene_id = int(request.GET.get("sceneId"))
        scene_obj = Scene.objects.get(user=request.user, id=scene_id)

        return JsonResponse(self.resume_status(scene_obj), safe=False)
