# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import Http404
from django.http import JsonResponse
from django.conf import settings

from scene.models import Scene, MetroConnection, MetroLine, MetroStation, MetroDepot, MetroConnectionStation

from scene.statusResponse import Status


class ScenePanel(View):
    ''' wizard form: first  '''
    def __init__(self):
        self.context = {}
        self.template = 'scene/sceneView.html'

    def get(self, request, sceneId):

        try:
            self.context['scene'] = Scene.objects.get(user=request.user, 
                id=sceneId)
        except:
            raise Http404

        return render(request, self.template, self.context)


class ScenePanelData(View):
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
        for line in scene.metroline_set.all():
            lines.append(line.getDict())
        
        connectionsDict = []
        for connection in connections:
            connectionsDict.append(connection.getDict())

        response = {}
        response['lines'] = lines
        response['connections'] = connectionsDict

        Status.getJsonStatus(Status.OK, response)

        return JsonResponse(response, safe=False)

