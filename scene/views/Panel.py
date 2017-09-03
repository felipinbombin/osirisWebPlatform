# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View

from scene.models import Scene
from scene.statusResponse import Status
from scene.views.SceneData import GetSceneData
from scene.views.InputModel import speed_input_model, serialize_input

from cmmmodel.views import Status as ModelStatus

import numpy as np
import datetime


class ScenePanel(View):
    """ wizard form: first """

    def __init__(self):
        super(ScenePanel, self).__init__()
        self.context = {}
        self.template = "scene/scenePanel.html"

    def get(self, request, sceneId):

        #try:
        scene_obj = Scene.objects.get(user=request.user, id=sceneId)
        self.context["scene"] = scene_obj
        self.context["data"] = GetSceneData().getData(request, sceneId)
        self.context["barWidth"] = int(float(scene_obj.currentStep) / 7 * 100)
        if scene_obj.currentStep < 6:
            status_label = "FALTA COMPLETAR PASO {}".format(scene_obj.currentStep + 1)
        else:
            status_label = "COMPLETADO"
        self.context["status_label"] = status_label

        self.context["models"] = ModelStatus().resume_status(scene_obj)
        #except:
        #    raise Http404

        return render(request, self.template, self.context)


class ChangeSceneName(View):
    """ view to change scene name """

    def __init__(self):
        super(ChangeSceneName, self).__init__()
        self.context = {}

    def post(self, request, scene_id):
        response = {}
        try:
            scene_obj = Scene.objects.get(user=request.user, id=int(scene_id))
            new_name = request.POST.get("new_name")

            if new_name is not None and new_name != "":
                scene_obj.name = new_name
                scene_obj.save()
                Status.getJsonStatus(Status.SUCCESS_NEW_NAME, response)
            else:
                Status.getJsonStatus(Status.INVALID_SCENE_NAME_ERROR, response)

        except Scene.DoesNotExist:
            Status.getJsonStatus(Status.USER_NOT_LOGGED_ERROR, response)

        return JsonResponse(response, safe=False)


class DeleteScene(View):
    """ view to change scene name """

    def __init__(self):
        super(DeleteScene, self).__init__()
        self.context = {}

    def post(self, request, scene_id):

        response = {}
        try:
            with transaction.atomic():
                scene_obj = Scene.objects.get(user=request.user, id=int(scene_id))
                scene_obj.delete()
                Status.getJsonStatus(Status.OK, response)
        except Scene.DoesNotExist:
            Status.getJsonStatus(Status.USER_NOT_LOGGED_ERROR, response)
        except:
            Status.getJsonStatus(Status.GENERIC_ERROR, response)
            response["status"]["message"] = u"No se pudo eliminar el escenario"

        return JsonResponse(response, safe=False)


class ScenePanelData(View):
    """ get inputModel of scene """

    def __init__(self):
        super(ScenePanelData, self).__init__()
        self.context = {}

    def get(self, request, sceneId):
        """ return inputModel of step 1 """

        sceneId = int(sceneId)
        scene = Scene.objects.prefetch_related("metroline_set__metrostation_set",
                                               "metroline_set__metrodepot_set",
                                               "metroconnection_set__stations"). \
            get(user=request.user, id=sceneId)

        lines = []
        for line in scene.metroline_set.all():
            lines.append(line.get_dict())

        connectionsDict = []
        for connection in scene.connection_set.all():
            connectionsDict.append(connection.get_dict())

        response = {"lines": lines, "connections": connectionsDict}

        Status.getJsonStatus(Status.OK, response)

        return JsonResponse(response, safe=False)


class InputModelData(View):
    """ get input model inputModel """

    def __init__(self):
        super(InputModelData, self).__init__()
        self.context = {}

    def get(self, request, sceneId):
        """ return inputModel to run models """

        sceneId = int(sceneId)
        inputModel = speed_input_model(request.user, sceneId)

        response = {"inputModel": inputModel}
        Status.getJsonStatus(Status.OK, response)

        response = serialize_input(response)

        return JsonResponse(response, safe=False)
