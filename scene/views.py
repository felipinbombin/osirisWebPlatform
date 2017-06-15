# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import Http404
from django.http import JsonResponse

from .models import Scene, MetroConnection, MetroLine, MetroStation, MetroDepot

from .forms import FirstStepForm, SecondStepForm, ThirdStepForm, FourthStepForm, FithStepForm, SixthStepForm

from .statusResponse import Status

import json

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

        for line in data['lines']:
            externalId = line['id']
            name = line['name']
            if externalId:
                lineObj = MetroLine.select_related('stations').filter(scene=scene, externalId=externalId)
            else:
                lineObj = MetroLine.objects.create(scene=scene, name=name)

            for station in line['stations']:
                if station['id']:
                    MetroStation.objects.filter(metroLine=lineObj, externalId=station['id']).\
                        update(name=station['name'])
                else:
                    MetroStation.objects.create(metroLine=lineObj, name=station['name'])
              
            for depot in line['depots']:
                if station['id']:
                    MetroDepot.objects.filter(metroLine=lineObj, externalId=depot[id]).\
                        update(name)
                else:
                    MetroDepot.objects.create(metroLine=lineObj, name=depot['name'])

        for connection in data['connections']:
            # global connections
            externalId = connection['id']
            name = connection['name']
            if externalId:
                connectionObj = MetroConnection.objects.prefetch_related('stations').\
                    get(scene=scene, externalId=externalId)
            else:
                connectionObj = MetroConnection.objects.create(scene=scene, name=name)

        Status.getJsonStatus(Status.OK, response)
        return response
            
    def post(self, request, stepId, sceneId):
        """ validate and update data in server """

        stepId = int(stepId)
        sceneId = int(sceneId)

        sceneObj = Scene.objects.get(user=request.user, id=sceneId)

        if stepId == 1:
           # global topologic variables
           response = self.processStep1(request, sceneObj)
        elif stepId == 2:
            # upload topologic file
            pass
            # if everything ok
            scene.status = Scene.OK
            scene.save()


        response = {}

        response['status'] = {}
        response['status']['code'] = 200
        response['status']['message'] = 'Estructura topológica creada exitosamente.'
        response['status']['type'] = 'success'
        response['status']['title'] = 'Actualización exitosa'

        return JsonResponse(response, safe=False)


class GetStep1DataView(View):
    ''' get data of step 1 '''

    def __init__(self):
        self.context = {}

    def get(self, request, sceneId):
        """ return data of step 1 """

        sceneId = int(sceneId)
        scene = Scene.objects.prefetch_related('metroline_set').get(user=request.user, id=sceneId)
        connections = MetroConnection.objects.all().prefetch_related('stations').filter(scene=scene)

        lines = []
        for line in scene.metroline_set.all():
            lines.append(line.getDict())
        
        connectionsDict = []
        for connection in connections:
            connectionsDict.append(connnection.getDict())

        response = {}
        response['lines'] = lines
        response['connections'] = connectionsDict

        Status.getJsonStatus(Status.OK, response)

        return JsonResponse(response, safe=False)
