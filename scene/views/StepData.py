# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
# Create your views here.
from django.views.generic import View

from scene.models import Scene, MetroConnection
from scene.statusResponse import Status

class GetStep0Data(View):
    ''' get data of step 1 '''

    def __init__(self):
        self.context = {}

    def get(self, request, sceneId):
        """ return data of step 1 """

        sceneId = int(sceneId)
        scene = Scene.objects.prefetch_related('metroline_set__metrostation_set', 'metroline_set__metrodepot_set').\
            get(user=request.user, id=sceneId)
        connections = MetroConnection.objects.prefetch_related('stations').filter(scene=scene)

        lines = []
        for line in scene.metroline_set.all().order_by('id'):
            lines.append(line.getDict())
        
        connectionsDict = []
        for connection in connections:
            connectionsDict.append(connection.getDict())

        response = {'lines': lines, 'connections': connectionsDict}

        Status.getJsonStatus(Status.OK, response)

        return JsonResponse(response, safe=False)


class GetStep2Data(View):
    ''' get data of step 3 '''

    def __init__(self):
        self.context = {}

    def get(self, request, sceneId):
        """ return data of step 3 """

        sceneId = int(sceneId)
        scene = Scene.objects.prefetch_related('metroline_set__metrostation_set', 'metroline_set__metrodepot_set'). \
            get(user=request.user, id=sceneId)
        connections = MetroConnection.objects.prefetch_related('stations').filter(scene=scene)

        lines = []
        for line in scene.metroline_set.all().order_by('id'):
            lines.append(line.getDict())

        connectionsDict = []
        for connection in connections:
            connectionsDict.append(connection.getDict())

        response = {'lines': lines, 'connections': connectionsDict}

        Status.getJsonStatus(Status.OK, response)

        return JsonResponse(response, safe=False)


class GetStep4Data(View):
    ''' get data of step 4 '''

    def __init__(self):
        self.context = {}

    def get(self, request, sceneId):
        """ return data of step 4 """

        sceneId = int(sceneId)
        scene = Scene.objects.prefetch_related('metroline_set__metrostation_set', 'metroline_set__metrodepot_set'). \
            get(user=request.user, id=sceneId)
        connections = MetroConnection.objects.prefetch_related('stations').filter(scene=scene)

        lines = []
        for line in scene.metroline_set.all().order_by('id'):
            lines.append(line.getDict())

        connectionsDict = []
        for connection in connections:
            connectionsDict.append(connection.getDict())

        response = {'lines': lines, 'connections': connectionsDict}

        Status.getJsonStatus(Status.OK, response)

        return JsonResponse(response, safe=False)
