# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import uuid

from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import JsonResponse
# Create your views here.
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from scene.forms import FirstStepForm
from scene.models import Scene, MetroConnection, MetroLine, MetroStation, MetroDepot, MetroConnectionStation
from scene.statusResponse import Status
from .Excel import Step2Excel, Step4Excel


class StepsView(View):
    ''' wizard form: first  '''
    def __init__(self):
        self.context = {}
        self.template = 'scene/wizard.html'

    def post(self, request):
        # if this is a POST request we need to process the form data

        # create a form instance and populate it with data from the request:
        form = FirstStepForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

        return render(request, self.template, {'form': form})

    def get(self, request, sceneId):

        try:
            self.context['scene'] = Scene.objects.get(user=request.user, id=sceneId)
        except:
            raise Http404

        return render(request, self.template, self.context)

class ValidationStepView(View):
    ''' validate data from step '''

    def __init__(self):
        self.context = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ValidationStepView, self).dispatch(request, *args, **kwargs)

    def processStep1(self, request, scene):
        ''' create or edit global topologic variables '''
        data = json.loads(request.body)
        response={}

        # all records all old by default
        scene.metroline_set.update(isOld=True)
        MetroStation.objects.filter(metroLine__scene=scene).update(isOld=True)
        MetroDepot.objects.filter(metroLine__scene=scene).update(isOld=True)
        MetroConnection.objects.filter(scene=scene).update(isOld=True)
        MetroConnectionStation.objects.filter(metroConnection__scene=scene).update(isOld=True)

        for line in data['lines']:
            externalId = line['id']
            name = line['name']
            if externalId:
                lineObj = MetroLine.objects.get(scene=scene, externalId=externalId)
                lineObj.name = name
                lineObj.isOld = False
                lineObj.save()
            else:
                lineObj = MetroLine.objects.create(scene=scene, name=name, externalId=uuid.uuid4())

            for station in line['stations']:
                if station['id']:
                    MetroStation.objects.filter(metroLine=lineObj, externalId=station['id']).\
                        update(name=station['name'], isOld=False)
                else:
                    MetroStation.objects.create(metroLine=lineObj, name=station['name'], externalId=uuid.uuid4())
              
            for depot in line['depots']:
                if depot['id']:
                    MetroDepot.objects.filter(metroLine=lineObj, externalId=depot['id']).\
                        update(name=depot['name'], isOld=False)
                else:
                    MetroDepot.objects.create(metroLine=lineObj, name=depot['name'], externalId=uuid.uuid4())

        for connection in data['connections']:
            # global connections
            externalId = connection['id']
            avgHeight = float(connection['avgHeight'])
            avgSurface = float(connection['avgSurface'])
            if externalId:
                connectionObj = MetroConnection.objects.prefetch_related('stations').\
                    get(scene=scene, externalId=externalId)
                connectionObj.name = connection['name']
                connectionObj.avgHeight = avgHeight
                connectionObj.avgSurface = avgSurface
                connectionObj.isOld = False
                connectionObj.save()
            else:
                connectionObj = MetroConnection.objects.create(scene=scene, name=connection['name'], 
                    avgHeight=avgHeight, avgSurface=avgSurface, externalId=uuid.uuid4())

            for connectionStation in connection['stations']:
                station = connectionStation['station']
                line = connectionStation['line']

                if station['id']:
                    stationObj = MetroStation.objects.get(metroLine__scene=scene, externalId=station['id'])
                else:
                    stationObj = MetroStation.objects.get(metroLine__name=line['name'], 
                                     metroLine__scene=scene, name=station['name'])

                if connectionStation['id']:
                    MetroConnectionStation.objects.filter(metroConnection=connectionObj, 
                        externalId=connectionStation['id']).update(metroStation=stationObj, isOld=False)
                else:
                    MetroConnectionStation.objects.create(metroConnection=connectionObj, 
                        metroStation=stationObj, externalId=uuid.uuid4())
                
        MetroLine.objects.filter(scene=scene, isOld=True).delete()
        MetroStation.objects.filter(metroLine__scene=scene, isOld=True).delete()
        MetroDepot.objects.filter(metroLine__scene=scene, isOld=True).delete()
        MetroConnection.objects.filter(scene=scene, isOld=True).delete()
        MetroConnectionStation.objects.filter(metroConnection__scene=scene, isOld=True).delete()

        # move to next step
        if scene.currentStep == 0:
            scene.currentStep = 1
            scene.save()

        step2Excel = Step2Excel(scene)
        step2Excel.createTemplateFile()

        step4Excel = Step4Excel(scene)
        step4Excel.createTemplateFile()

        Status.getJsonStatus(Status.OK, response)

        return response

    def post(self, request, stepId, sceneId):
        """ validate and update data in server """

        stepId = int(stepId)
        sceneId = int(sceneId)

        sceneObj = Scene.objects.prefetch_related('metroline_set__metrostation_set', 
                       'metroline_set__metrodepot_set').\
                       get(user=request.user, id=sceneId)
        response = {}
        if stepId == 0:
            # global topologic variables
            response = self.processStep1(request, sceneObj)
            response['status']['title'] = 'Actualización exitosa'
            response['status']['message'] = 'Estructura topológica creada exitosamente.'
        elif stepId == 1:
            # check if file was uploaded successfully
            if sceneObj.currentStep >= 1:
                Status.getJsonStatus(Status.OK, response)
                response['status']['title'] = 'Actualización exitosa'
                response['status']['message'] = 'Archivo subido exitosamente.'
            else:
                Status.getJsonStatus(Status.INVALID_STEP, response)
        elif stepId == 2:
            pass
        elif stepId == 3:
            # check if file was uploaded successfully
            if sceneObj.currentStep >= 3:
                Status.getJsonStatus(Status.OK, response)
                response['status']['title'] = 'Actualización exitosa'
                response['status']['message'] = 'Archivo subido exitosamente.'
            else:
                Status.getJsonStatus(Status.INVALID_STEP, response)
        elif stepId == 4:
            pass
        elif stepId == 5:
            # check if file was uploaded successfully
            if sceneObj.currentStep >= 5:
                Status.getJsonStatus(Status.OK, response)
                response['status']['title'] = 'Actualización exitosa'
                response['status']['message'] = 'Archivo subido exitosamente.'
                sceneObj.status = Scene.OK
                sceneObj.save()
            else:
                Status.getJsonStatus(Status.INVALID_STEP, response)
        elif stepId == 6:
            Status.getJsonStatus(Status.OK, response)
            response['status']['title'] = 'Actualización exitosa'
            response['status']['message'] = 'Archivo subido exitosamente.'


        return JsonResponse(response, safe=False)


class GetStep1DataView(View):
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

        response = {'lines': lines, 'connections': connectionsDict}

        Status.getJsonStatus(Status.OK, response)

        return JsonResponse(response, safe=False)

