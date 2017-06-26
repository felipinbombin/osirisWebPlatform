# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod

# Create your views here.
from django.views.generic import View
from django.http import JsonResponse
from django.conf import settings

from scene.models import Scene, MetroConnection, MetroLine, MetroStation, MetroDepot, MetroConnectionStation

from scene.statusResponse import Status

import math
import os

class UploadFile(View):
    ''' general upload file behavior '''
    __metaclass__ = ABCMeta

    def __init__(self):
        self.context = {}

    def validateFile(self, inMemoryUploadedFile, response):
        fileSizeLimit = 2*math.pow(10, 6) # 2MB

        if inMemoryUploadedFile.size > fileSizeLimit:
            Status.getJsonStatus(Status.INVALID_SIZE_FILE, response)
            response['status']['message'] = 'El archivo no puede tener un tamaño superior a 2 MB.'
        elif not inMemoryUploadedFile.name.endswith('.xlsx'):
            Status.getJsonStatus(Status.INVALID_FORMAT_FILE, response)
            response['status']['message'] = 'El archivo debe tener formato Excel.'
        else:
            Status.getJsonStatus(Status.OK, response)

        return response

    def post(self, request, sceneId):
        """ validate and update data in server """

        sceneId = int(sceneId)

        sceneObj = Scene.objects.\
                       prefetch_related('metroline_set__metrostation_set', 
                       'metroline_set__metrodepot_set').\
                       get(user=request.user, id=sceneId)

        response = {}

        if sceneObj.lastSuccessfullStep >= 1:
            inMemoryUploadedFile = request.FILES['file']
            response = self.validateFile(inMemoryUploadedFile, response)
            
            if response['status']['code'] == Status.OK:
                # process file
                response = self.processFile(sceneObj, inMemoryUploadedFile)
        else:
            Status.getJsonStatus(Status.INVALID_STEP, response)

        return JsonResponse(response, safe=False)

    def updateSuccessfulStep(self, scene, fileField, uploadedFile, newStep):
        # delete previous file
        if fileField:
            os.remove(os.path.join(settings.MEDIA_ROOT, 
                fileField.name))
        fileName = uploadedFile.name
        fileField.save(fileName, uploadedFile)

        if(scene.lastSuccessfullStep < newStep):
            scene.lastSuccessfullStep = newStep
            scene.save()

    @abstractmethod
    def processFile(self, scene, inMemoryFile):
        pass
        # validate data
        # delete previous data
        # insert new data
        # save file


class UploadTopologicFile(UploadFile):
    ''' validate data from step 4 '''

    def processFile(self, scene, inMemoryFile):
        # validate data
        # delete previous data
        # insert new data

        # save file
        self.updateSuccessfulStep(scene, scene.step2File, inMemoryFile, 2)

        response = Status.getJsonStatus(Status.OK, {})
        response['status']['message'] = 'Archivo topológico subido exitosamente.'

        return response


class UploadSystemicFile(UploadFile):
    ''' validate data from stepa 4 '''

    def processFile(self, scene, inMemoryFile):
          
        # validate data
        # delete previous data
        # insert new data

        # save file
        self.updateSuccessfulStep(scene, scene.step4File, inMemoryFile, 4)

        response = Status.getJsonStatus(Status.OK, {})
        response['status']['message'] = 'Archivo sistémico subido exitosamente.'

        return response


class UploadOperationalFile(UploadFile):
    ''' validate data from stepa 6 '''

    def processFile(self, scene, inMemoryFile):
           
        # validate data
        # delete previous data
        # insert new data

        # save file
        self.updateSuccessfulStep(scene, scene.step6File, inMemoryFile, 6)

        response = Status.getJsonStatus(Status.OK, {})
        response['status']['message'] = 'Archivo operacional subido exitosamente.'

        return response


class UploadVelocityFile(UploadFile):
    ''' validate data from stepa 7 '''

    def processFile(self, scene, inMemoryFile):
            
        # validate data
        # delete previous data
        # insert new data

        # save file
        self.updateSuccessfulStep(scene, scene.step7File, inMemoryFile, 7)

        response = Status.getJsonStatus(Status.OK, {})
        response['status']['message'] = 'Archivo de velocidades subido exitosamente.'

        return response

