# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction, IntegrityError

from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from scene.models import Scene
from scene.statusResponse import Status
from .StepSaver import Step0Saver, Step2Saver, Step4Saver

from scene.sceneExceptions import OsirisException

import json

class StepsView(View):
    """ wizard form: first  """
    def __init__(self):
        self.context = {}
        self.template = "scene/wizard.html"

    def get(self, request, sceneId):
        try:
            self.context["scene"] = Scene.objects.get(user=request.user, id=sceneId)
        except:
            raise Http404

        return render(request, self.template, self.context)


class ValidationStepView(View):
    """ validate data from step """

    def __init__(self):
        self.context = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ValidationStepView, self).dispatch(request, *args, **kwargs)

    def post(self, request, stepId, sceneId):
        """ validate and update data in server """

        stepId = int(stepId)
        sceneId = int(sceneId)

        sceneObj = Scene.objects.prefetch_related("metroline_set__metrostation_set", 
                       "metroline_set__metrodepot_set", "operationperiod_set").\
                       get(user=request.user, id=sceneId)
        response = {}
        try:
            with transaction.atomic():
                if stepId == 0:
                    # global topologic variables
                    data = json.loads(request.body.decode("UTF-8"))

                    step0Saver = Step0Saver(sceneObj)
                    step0Saver.save(data)

                    response = Status.getJsonStatus(Status.OK, response)
                    response["status"]["title"] = u"Actualización exitosa"
                    response["status"]["message"] = u"Estructura topológica creada exitosamente."

                elif stepId == 1:
                    # check if file was uploaded successfully
                    if sceneObj.currentStep >= 1:
                        Status.getJsonStatus(Status.OK, response)
                        response["status"]["title"] = u"Actualización exitosa"
                        response["status"]["message"] = u"Archivo subido exitosamente."
                    else:
                        Status.getJsonStatus(Status.INVALID_STEP_ERROR, response)
                elif stepId == 2:
                    # global systemic variables
                    data = json.loads(request.body.decode("utf-8"))

                    step2Saver = Step2Saver(sceneObj)
                    step2Saver.save(data)

                    response = Status.getJsonStatus(Status.OK, response)
                    response["status"]["title"] = u"Actualización exitosa"
                    response["status"]["message"] = u"Variables sistemicas guardadas exitosamente."

                elif stepId == 3:
                    # check if file was uploaded successfully
                    if sceneObj.currentStep >= 3:
                        Status.getJsonStatus(Status.OK, response)
                        response["status"]["title"] = u"Actualización exitosa"
                        response["status"]["message"] = u"Archivo subido exitosamente."
                    else:
                        Status.getJsonStatus(Status.INVALID_STEP_ERROR, response)
                elif stepId == 4:
                    # global operational variables
                    data = json.loads(request.body.decode("utf-8"))

                    step4Saver = Step4Saver(sceneObj)
                    step4Saver.save(data)

                    response = Status.getJsonStatus(Status.OK, response)
                    response["status"]["title"] = u"Actualización exitosa"
                    response["status"]["message"] = u"Los datos han sido guardados"

                elif stepId == 5:
                    # check if file was uploaded successfully
                    if sceneObj.currentStep >= 5:
                        Status.getJsonStatus(Status.OK, response)
                        response["status"]["title"] = u"Actualización exitosa"
                        response["status"]["message"] = u"Archivo subido exitosamente."
                        sceneObj.status = Scene.OK
                        sceneObj.save()
                    else:
                        Status.getJsonStatus(Status.INVALID_STEP_ERROR, response)
                elif stepId == 6:
                    Status.getJsonStatus(Status.OK, response)
                    response["status"]["title"] = u"Actualización exitosa"
                    response["status"]["message"] = u"Archivo subido exitosamente."
        except IntegrityError as e:
            Status.getJsonStatus(Status.EXCEL_ERROR, response)
            response["status"]["message"] = str(e)
        except OsirisException as e:
            response.update(e.get_status_response())

        return JsonResponse(response, safe=False)
