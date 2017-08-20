# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction, IntegrityError

from django.http import Http404
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from scene.models import Scene
from scene.statusResponse import Status

from scene.sceneExceptions import OsirisException


class Run(View):
    """ run model on cmm cluster """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Run, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """  """
        scene_id = int(request.POST.get("sceneId"))
        model_id = int(request.POST.get("modelId"))
        next_model_ids = request.POST.getlist("nextModelIds")

        try:
            sceneObj = Scene.objects.get(user=request.user, id=scene_id)
        except:
            raise Http404()

        response = {}
        Status.getJsonStatus(Status.OK, response)

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
            Status.getJsonStatus(Status.EXCEL_ERROR, response)
            response["status"]["message"] = str(e)
        except OsirisException as e:
            response.update(e.get_status_response())

        return JsonResponse(response, safe=False)


class Status(View):
    """ Give the information of all model for scene """

    def get(self, request):

        scene_id = int(request.GET.get("sceneId"))

        scene_obj = Scene.objects.prefetch_related("model_set__modelexecutionhistory_set").\
                       get(user=request.user, id=scene_id)
        response = {
            "models": []
        }
        for model in scene_obj.model_set.all().order_by("id"):
            response["models"].append(model.getDictionary)

        return JsonResponse(response, safe=False)
