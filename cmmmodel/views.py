# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction, IntegrityError

from django.http import Http404
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.conf import settings

from scene.models import Scene
from scene.statusResponse import Status as sts

from scene.sceneExceptions import OsirisException
from cmmmodel.models import ModelExecutionHistory, Model

import paramiko
import os

class Run(View):
    """ run model on cmm cluster """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Run, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """  """
        scene_id = int(request.POST.get("sceneId"))
        model_id = int(request.POST.get("modelId"))
        next_model_ids = [int(id) for id in request.POST.getlist("nextModelIds[]")]

        key_path = os.path.join(settings.KEY_DIR, 'ssh_key')

        response = {}
        try:
            sceneObj = Scene.objects.get(user=request.user, id=scene_id)
            print(scene_id, model_id, next_model_ids)

            # create ssh connection
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            k = paramiko.RSAKey.from_private_key_file(key_path)
            client.connect(hostname='leftraru.nlhpc.cl', username="fhernandez", pkey=k)

            responseScript = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saveJobResponse.py')
            command = "sbatch osiris/speed.sh {} {}".format(settings.SERVER_IP, responseScript)

            stdin, stdout, stderr = client.exec_command(command)

            for line in stdout:
                print("job number:", int(line.strip('\n').split(" ")[3]))

            client.close()

            sts.getJsonStatus(sts.OK, response)
        except Scene.DoesNotExist:
            sts.getJsonStatus(sts.SCENE_DOES_NOT_EXISTS_ERROR, response)
        #except:
        #    Http404()

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

        sceneObj = Scene.objects.prefetch_related("metroline_set__metrostation_set",
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
