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
from django.conf import settings

from scene.models import Scene, MetroConnection, MetroLine, MetroStation, MetroDepot, MetroConnectionStation

from scene.statusResponse import Status

import math

class UploadTopologicFileView(View):
    ''' validate data from step '''

    def __init__(self):
        self.context = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UploadTopologicFileView, self).dispatch(request, *args, **kwargs)

    def validateFile(self, inMemoryUploadedFile, response):
        fileSizeLimit = 2*math.pow(1, 6) # 2MB
        isValid = True

        if inMemoryUploadedFile.size > fileSizeLimit:
            Status.getJsonStatus(Status.INVALID_SIZE_FILE, response)
            isValid = False
            response['status']['message'] = 'El archivo no puede tener un tamaño superior a 2 MB.'
        elif inMemoryUploadedFile.name.endsWith('.xlsx'):
            Status.getJsonStatus(Status.INVALID_FORMAT_FILE, response)
            isValid = False
            response['status']['message'] = 'El archivo no puede tener un tamaño superior a 2 MB.'
        else:
            Status.getJsonStatus(Status.OK, response)

        return isValid, response
     
    def post(self, request, sceneId):
        """ validate and update data in server """

        sceneId = int(sceneId)

        sceneObj = Scene.objects.prefetch_related('metroline_set__metrostation_set', 
                       'metroline_set__metrodepot_set').\
                       get(user=request.user, id=sceneId)

        response = {}

        if sceneObj.lastSuccessfullStep >= 1:
            inMemoryUploadedFile = request.FILES['file']
            isValid, response = self.validateFile(inMemoryUploadedFile, response)
            if isValid:
                # proces file
                pass
        else:
            Status.getJsonStatus(Status.INVALID_STEP, response)

        return JsonResponse(response, safe=False)

