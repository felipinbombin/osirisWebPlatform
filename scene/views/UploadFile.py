# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math
import os
from abc import ABCMeta, abstractmethod

from django.conf import settings
from django.http import JsonResponse
from django.db import transaction, IntegrityError
from django.views.generic import View

from scene.models import Scene
from scene.statusResponse import Status

from .ExcelReader import Step1ExcelReader, Step3ExcelReader, Step5ExcelReader, Step6ExcelReader

MESSAGE = {
    "FILE_TOO_BIG": "El archivo no puede tener un tamaño superior a 2 MB.",
    "FILE_WRONG_FORMAT": "El archivo debe tener formato Excel.",
    "FILE_STEP1_UPLOADED_SUCCESSFULLY": "Archivo topológico subido exitosamente.",
    "FILE_STEP3_UPLOADED_SUCCESSFULLY": "Archivo sistémico subido exitosamente.",
    "FILE_STEP5_UPLOADED_SUCCESSFULLY": "Archivo operacional subido exitosamente.",
    "FILE_STEP6_UPLOADED_SUCCESSFULLY": "Archivo de velocidades subido exitosamente.",
}


class UploadFile(View):
    """ general upload file behavior """
    __metaclass__ = ABCMeta

    def __init__(self):
        self.context = {}

    def validateFile(self, inMemoryUploadedFile, response):
        fileSizeLimit = 2*math.pow(10, 6) # 2MB

        if inMemoryUploadedFile.size > fileSizeLimit:
            Status.getJsonStatus(Status.INVALID_SIZE_FILE, response)
            response['status']['message'] = MESSAGE["FILE_TOO_BIG"]
        elif not inMemoryUploadedFile.name.endswith('.xlsx'):
            Status.getJsonStatus(Status.INVALID_FORMAT_FILE, response)
            response['status']['message'] = MESSAGE["FILE_WRONG_FORMAT"]
        else:
            Status.getJsonStatus(Status.OK, response)

        return response

    def post(self, request, sceneId):
        """ validate and update data in server """

        sceneId = int(sceneId)

        sceneObj = Scene.objects.\
            prefetch_related('metroline_set__metrostation_set',
                             'metroline_set__metrodepot_set',
                             'metroline_set__metrotrack_set',
                             'operationperiod_set').\
            get(user=request.user, id=sceneId)

        response = {}

        if sceneObj.currentStep > 0:
            inMemoryUploadedFile = request.FILES['file']

            try:
                with transaction.atomic():
                    response = self.validateFile(inMemoryUploadedFile, response)

                    if response['status']['code'] == Status.OK:
                        # process file
                        response = self.processFile(sceneObj, inMemoryUploadedFile)
            except Exception as e:
                Status.getJsonStatus(Status.EXCEL_ERROR, response)
                response['status']['message'] = str(e)
        else:
            Status.getJsonStatus(Status.INVALID_STEP, response)

        return JsonResponse(response, safe=False)

    def updateCurrentStep(self, scene, fileField, uploadedFile, newStep):
        # delete previous file
        if fileField:
            os.remove(os.path.join(settings.MEDIA_ROOT, 
                fileField.name))
        fileName = uploadedFile.name
        fileField.save(fileName, uploadedFile)

        if scene.currentStep < newStep:
            scene.currentStep = newStep
            scene.save()

    @abstractmethod
    def processFile(self, scene, inMemoryFile):
        pass
        # validate data
        # delete previous data
        # insert new data
        # save file


class UploadTopologicFile(UploadFile):
    """ validate data from step 1 """

    def processFile(self, scene, inMemoryFile):
        # validate, update and insert new data
        Step1ExcelReader(scene).processFile(inMemoryFile)

        # save file
        self.updateCurrentStep(scene, scene.step1File, inMemoryFile, 2)

        response = Status.getJsonStatus(Status.OK, {})
        response['status']['message'] = MESSAGE["FILE_STEP1_UPLOADED_SUCCESSFULLY"]

        return response


class UploadSystemicFile(UploadFile):
    """ validate data from stepa 3 """

    def processFile(self, scene, inMemoryFile):
        # validate, update and insert new data
        Step3ExcelReader(scene).processFile(inMemoryFile)

        # save file
        self.updateCurrentStep(scene, scene.step3File, inMemoryFile, 4)

        response = Status.getJsonStatus(Status.OK, {})
        response['status']['message'] = MESSAGE["FILE_STEP3_UPLOADED_SUCCESSFULLY"]

        return response


class UploadOperationalFile(UploadFile):
    """ validate data from stepa 5 """

    def processFile(self, scene, inMemoryFile):
        # validate, update and insert new data
        Step5ExcelReader(scene).processFile(inMemoryFile)
        # save file
        self.updateCurrentStep(scene, scene.step5File, inMemoryFile, 6)

        response = Status.getJsonStatus(Status.OK, {})
        response['status']['message'] = MESSAGE["FILE_STEP5_UPLOADED_SUCCESSFULLY"]
        
        return response


class UploadSpeedFile(UploadFile):
    """ validate data from step 6 """

    def processFile(self, scene, inMemoryFile):
        # validate, update and insert new data
        Step6ExcelReader(scene).processFile(inMemoryFile)
        # save file
        self.updateCurrentStep(scene, scene.step6File, inMemoryFile, 6)

        response = Status.getJsonStatus(Status.OK, {})
        response['status']['message'] = MESSAGE["FILE_STEP6_UPLOADED_SUCCESSFULLY"]

        return response
