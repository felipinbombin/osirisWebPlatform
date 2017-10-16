# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from scene.models import Scene
from scene.statusResponse import Status as StatusResponse

from cmmmodel.models import ModelExecutionHistory, Model
from cmmmodel.clusterConnection import run_task, cancel_task, EnqueuedModelException, ModelIsRunningException, \
    IncompleteSceneException, ModelInputDoesNotExistException


class Run(View):
    """ run model on cmm cluster """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Run, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """  """
        scene_id = int(request.POST.get("scene_id"))
        model_id = int(request.POST.get("model_id"))
        next_model_ids = [int(next_model_id) for next_model_id in request.POST.getlist("nextModelIds[]")]

        response = {}
        try:
            scene_obj = Scene.objects.get(user=request.user, id=scene_id)
            run_task(scene_obj, model_id, next_model_ids)

            response["models"] = Status().resume_status(scene_obj)
            StatusResponse.getJsonStatus(StatusResponse.OK, response)
        except Scene.DoesNotExist:
            StatusResponse.getJsonStatus(StatusResponse.SCENE_DOES_NOT_EXIST_ERROR, response)
        except ModelInputDoesNotExistException:
            StatusResponse.getJsonStatus(StatusResponse.MODEL_INPUT_DOES_NOT_EXIST_ERROR, response)
        except EnqueuedModelException:
            StatusResponse.getJsonStatus(StatusResponse.ENQUEUED_MODEL_ERROR, response)
        except ModelIsRunningException:
            StatusResponse.getJsonStatus(StatusResponse.MODEL_IS_RUNNING_ERROR, response)
        except IncompleteSceneException:
            StatusResponse.getJsonStatus(StatusResponse.INCOMPLETE_SCENE_ERROR, response)
        except Exception as e:
            StatusResponse.getJsonStatus(StatusResponse.GENERIC_ERROR, response)
            response["status"]["message"] = str(e)

        return JsonResponse(response, safe=False)


class Stop(View):
    """ Stop execution of a model on cmm cluster """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Stop, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """ validate and update data in server """
        scene_id = int(request.POST.get("scene_id"))
        model_id = int(request.POST.get("model_id"))

        response = {}
        try:
            with transaction.atomic():
                scene_obj = Scene.objects.get(user=request.user, id=scene_id)
                cancel_task(scene_obj, model_id)
                response["models"] = Status().resume_status(scene_obj)
                StatusResponse.getJsonStatus(StatusResponse.OK, response)
        except ModelExecutionHistory.DoesNotExist:
            StatusResponse.getJsonStatus(StatusResponse.MODEL_EXECUTION_DOES_NOT_EXIST_ERROR, response)
        except IntegrityError as e:
            StatusResponse.getJsonStatus(StatusResponse.GENERIC_ERROR, response)
            response["status"]["message"] = str(e)

        return JsonResponse(response, safe=False)


class Status(View):
    """ Give the information of all model for scene """
    DISABLED = "disabled"
    RUNNING = "running"
    AVAILABLE = "available"

    def resume_status(self, scene_obj):
        """  """
        model_list = Model.objects.all().order_by("id")
        model_status_list = []
        for model in model_list:
            model_status = model.get_dictionary()
            model_instance = ModelExecutionHistory.objects.filter(scene=scene_obj, model=model). \
                order_by("-start").first()
            if scene_obj.status == Scene.INCOMPLETE:
                status = self.DISABLED
            elif model_instance is not None:
                if model_instance.status == ModelExecutionHistory.RUNNING:
                    status = self.RUNNING
                else:
                    status = self.AVAILABLE
                # check its queue
                model_status["lastExecutionInfo"] = model_instance.get_dictionary()
            else:
                status = self.AVAILABLE

            model_status["status"] = status
            model_status_list.append(model_status)

        return model_status_list

    def get(self, request):

        scene_id = int(request.GET.get("scene_id"))
        scene_obj = Scene.objects.get(user=request.user, id=scene_id)

        return JsonResponse(self.resume_status(scene_obj), safe=False)
