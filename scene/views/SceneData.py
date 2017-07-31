# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
# Create your views here.
from django.views.generic import View

from scene.models import Scene, MetroConnection, SystemicParams, OperationPeriod
from scene.statusResponse import Status

class GetSceneData(View):
    ''' get data of scene '''

    def __init__(self):
        self.context = {}

    def get(self, request, sceneId):
        """ return data of step 1 """

        sceneId = int(sceneId)
        scene = Scene.objects.prefetch_related('metroline_set__metrostation_set', 'metroline_set__metrodepot_set').\
            get(user=request.user, id=sceneId)

        lines = list(map(lambda obj: obj.getDict(), scene.metroline_set.all().order_by('id')))
        connections = list(map(lambda obj: obj.getDict(), MetroConnection.objects.prefetch_related('stations').\
                               filter(scene=scene)))
        systemicParams = SystemicParams.objects.get_or_create(scene=scene)[0].getDict()
        operationPeriods = list(map(lambda obj: obj.getDict(), OperationPeriod.objects.filter(scene=scene).order_by('id')))

        operation = {
            'averageMassOfAPassanger': scene.averageMassOfAPassanger,
            'annualTemperatureAverage': scene.annualTemperatureAverage,
            'periods': operationPeriods
        }

        response = {'lines': lines,
                    'connections': connections,
                    'systemicParams': systemicParams,
                    'operation': operation,
                    'currentStep': scene.currentStep,
                    'name': scene.name}

        Status.getJsonStatus(Status.OK, response)

        return JsonResponse(response, safe=False)

