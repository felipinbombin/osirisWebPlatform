# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.http import JsonResponse
# Create your views here.
from django.shortcuts import render
from django.views.generic import View

from scene.models import Scene, MetroConnection
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
        scene = Scene.objects.prefetch_related('metroline_set__metrostation_set', 'metroline_set__metrodepot_set', 'metroconnection_set__stations').\
            get(user=request.user, id=sceneId)

        lines = []
        for line in scene.metroline_set.all():
            lines.append(line.getDict())
        
        connectionsDict = []
        for connection in scene.connection_set.all():
            connectionsDict.append(connection.getDict())

        response = {'lines': lines, 'connections': connectionsDict}

        Status.getJsonStatus(Status.OK, response)

        return JsonResponse(response, safe=False)

class InputModelData(View):
    ''' get input model data '''

    def __init__(self):
        self.context = {}

    def get(self, request, sceneId):
        """ return data to run models """

        sceneId = int(sceneId)
        scene = Scene.objects.prefetch_related('metroline_set__metrostation_set', 'metroline_set__metrodepot_set', 'metroconnection_set').\
            get(user=request.user, id=sceneId)

        inputModel = {'oper':{},'top':{},'sist':{}}

        inputModel['top']['nLines'] = len(scene.metroline_set.all())
        inputModel['top']['nConnections'] = len(scene.metroconnection_set.all())

        inputModel['top']['nStations'] = []
        inputModel['top']['nDepots'] = []
        for line in scene.metroline_set.all().order_by('id'):
            inputModel['top']['nStations'].append(len(line.metrostation_set.all()))
            inputModel['top']['nDepots'].append(len(line.metrodepot_set.all()))

        response = {'inputModel': inputModel}

        Status.getJsonStatus(Status.OK, response)

        return JsonResponse(response, safe=False)

