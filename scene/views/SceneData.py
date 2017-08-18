# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.views.generic import View

from scene.models import Scene, MetroConnection, SystemicParams, OperationPeriod
from scene.statusResponse import Status

class GetSceneData(View):
    ''' get data of scene '''

    def __init__(self):
        super(GetSceneData, self).__init__()
        self.context = {}

    def getData(self, request, sceneId):
        """ return dict object with scene data """

        sceneId = int(sceneId)
        scene = Scene.objects.prefetch_related('metroline_set__metrostation_set',
                                               'metroline_set__metrodepot_set',
                                               'metroconnection_set__stations').\
            get(user=request.user, id=sceneId)

        lines = list(map(lambda obj: obj.get_dict(), scene.metroline_set.all().order_by('id')))
        connections = list(map(lambda obj: obj.get_dict(), MetroConnection.objects.prefetch_related('stations'). \
                               filter(scene=scene)))
        systemicParams = SystemicParams.objects.get_or_create(scene=scene)[0].get_dict()
        operationPeriods = list(map(lambda obj: obj.get_dict(), OperationPeriod.objects.filter(scene=scene).order_by('id')))

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
        return response

    def get(self, request, sceneId):
        """ return data through http """

        response = self.getData(request, sceneId)
        Status.getJsonStatus(Status.OK, response)

        return JsonResponse(response, safe=False)

