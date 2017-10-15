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
        super(StepsView, self).__init__()
        self.context = {}
        self.template = "scene/wizard.html"

    def get(self, request, scene_id):
        try:
            self.context["scene"] = Scene.objects.get(user=request.user, id=scene_id)
        except:
            raise Http404

        return render(request, self.template, self.context)


class ValidationStepView(View):
    """ validate data from step """

    def __init__(self):
        super(ValidationStepView, self).__init__()
        self.context = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ValidationStepView, self).dispatch(request, *args, **kwargs)

    def post(self, request, step_id, scene_id):
        """ validate and update data in server """

        step_id = int(step_id)
        scene_id = int(scene_id)

        scene_obj = Scene.objects.prefetch_related("metroline_set__metrostation_set",
                                                   "metroline_set__metrodepot_set", "operationperiod_set"). \
            get(user=request.user, id=scene_id)
        response = {}
        try:
            with transaction.atomic():
                if step_id == 0:
                    # global topologic variables
                    data = json.loads(request.body.decode("UTF-8"))

                    step0_saver = Step0Saver(scene_obj)
                    step0_saver.save(data)

                    response = Status.getJsonStatus(Status.OK, response)
                    response["status"]["title"] = u"Actualización exitosa"
                    response["status"]["message"] = u"Estructura topológica creada exitosamente."

                elif step_id == 1:
                    # check if file was uploaded successfully
                    if scene_obj.currentStep >= 1:
                        Status.getJsonStatus(Status.OK, response)
                        response["status"]["title"] = u"Actualización exitosa"
                        response["status"]["message"] = u"Archivo subido exitosamente."
                    else:
                        Status.getJsonStatus(Status.INVALID_STEP_ERROR, response)
                elif step_id == 2:
                    # global systemic variables
                    data = json.loads(request.body.decode("utf-8"))

                    step2_saver = Step2Saver(scene_obj)
                    step2_saver.save(data)

                    response = Status.getJsonStatus(Status.OK, response)
                    response["status"]["title"] = u"Actualización exitosa"
                    response["status"]["message"] = u"Variables sistemicas guardadas exitosamente."

                elif step_id == 3:
                    # check if file was uploaded successfully
                    if scene_obj.currentStep >= 3:
                        Status.getJsonStatus(Status.OK, response)
                        response["status"]["title"] = u"Actualización exitosa"
                        response["status"]["message"] = u"Archivo subido exitosamente."
                    else:
                        Status.getJsonStatus(Status.INVALID_STEP_ERROR, response)
                elif step_id == 4:
                    # global operational variables
                    data = json.loads(request.body.decode("utf-8"))

                    step4_saver = Step4Saver(scene_obj)
                    step4_saver.save(data)

                    response = Status.getJsonStatus(Status.OK, response)
                    response["status"]["title"] = u"Actualización exitosa"
                    response["status"]["message"] = u"Los datos han sido guardados"

                elif step_id == 5:
                    # check if file was uploaded successfully
                    if scene_obj.currentStep >= 5:
                        Status.getJsonStatus(Status.OK, response)
                        response["status"]["title"] = u"Actualización exitosa"
                        response["status"]["message"] = u"Archivo subido exitosamente."
                        scene_obj.status = Scene.OK
                        scene_obj.save()
                    else:
                        Status.getJsonStatus(Status.INVALID_STEP_ERROR, response)
                elif step_id == 6:
                    Status.getJsonStatus(Status.OK, response)
                    response["status"]["title"] = u"Actualización exitosa"
                    response["status"]["message"] = u"Archivo subido exitosamente."
        except IntegrityError as e:
            Status.getJsonStatus(Status.EXCEL_ERROR, response)
            response["status"]["message"] = str(e)
        except OsirisException as e:
            response.update(e.get_status_response())

        return JsonResponse(response, safe=False)
