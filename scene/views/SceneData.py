# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.views.generic import View

from scene.models import Scene, MetroConnection, SystemicParams, OperationPeriod
from scene.statusResponse import Status


class GetSceneData(View):
    """ get data of scene """

    def __init__(self):
        super(GetSceneData, self).__init__()
        self.context = {}

    def get_data(self, request, scene_id):
        """ return dict object with scene data """

        scene_id = int(scene_id)
        scene = Scene.objects.prefetch_related("metroline_set__metrostation_set",
                                               "metroline_set__metrodepot_set",
                                               "metroconnection_set__stations"). \
            get(user=request.user, id=scene_id)

        lines = list(map(lambda obj: obj.get_dict(), scene.metroline_set.all().order_by("id")))
        connections = list(map(lambda obj: obj.get_dict(), MetroConnection.objects.prefetch_related("stations"). \
                               filter(scene=scene)))
        systemic_params = SystemicParams.objects.get_or_create(scene=scene)[0].get_dict()
        operation_periods = list(
            map(lambda obj: obj.get_dict(), OperationPeriod.objects.filter(scene=scene).order_by("id")))

        operation = {
            "averageMassOfAPassanger": scene.averageMassOfAPassanger,
            "annualTemperatureAverage": scene.annualTemperatureAverage,
            "periods": operation_periods
        }

        response = {"lines": lines,
                    "connections": connections,
                    "systemicParams": systemic_params,
                    "operation": operation,
                    "currentStep": scene.currentStep,
                    "name": scene.name}
        return response

    def get(self, request, scene_id):
        """ return data through http """

        response = self.get_data(request, scene_id)
        Status.getJsonStatus(Status.OK, response)

        return JsonResponse(response, safe=False)
