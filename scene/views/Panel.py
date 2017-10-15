# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View

from scene.models import Scene
from scene.statusResponse import Status
from scene.views.SceneData import GetSceneData

from cmmmodel.views import Status as ModelStatus
from cmmmodel.models import ModelExecutionHistory

import pickle
import datetime
import numpy as np
import json


class ScenePanel(View):
    """ wizard form: first """

    def __init__(self):
        super(ScenePanel, self).__init__()
        self.context = {}
        self.template = "scene/scenePanel.html"

    def get(self, request, scene_id):

        # try:
        scene_obj = Scene.objects.get(user=request.user, id=scene_id)
        self.context["scene"] = scene_obj
        self.context["data"] = GetSceneData().get_data(request, scene_id)
        self.context["barWidth"] = int(float(scene_obj.currentStep) / 7 * 100)
        if scene_obj.status == Scene.INCOMPLETE:
            status_label = "FALTA COMPLETAR PASO {}".format(scene_obj.currentStep + 1)
        else:
            status_label = "COMPLETADO"
        self.context["status_label"] = status_label

        self.context["models"] = ModelStatus().resume_status(scene_obj)
        # except:
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

    def get(self, request, scene_id):
        """ return inputModel of step 1 """

        scene_id = int(scene_id)
        scene = Scene.objects.prefetch_related("metroline_set__metrostation_set",
                                               "metroline_set__metrodepot_set",
                                               "metroline_set__metrotrack_set__startStation",
                                               "metroline_set__metrotrack_set__endStation"). \
            get(user=request.user, id=scene_id)

        lines = []
        for line in scene.metroline_set.all():
            lines.append(line.get_dict())

        connections_dict = []
        for connection in scene.metroconnection_set.all():
            connections_dict.append(connection.get_dict())

        response = {"lines": lines, "connections": connections_dict}

        Status.getJsonStatus(Status.OK, response)

        return JsonResponse(response, safe=False)


class InputModelData(View):
    """ get input model inputModel. For debug purpose """

    def __init__(self):
        super(InputModelData, self).__init__()
        self.context = {}

    def get(self, request, scene_id):
        """ return inputModel to run models """

        scene_id = int(scene_id)
        execution = ModelExecutionHistory.objects.order_by("-start", sceneId=scene_id).first()
        with open(execution.answer.path, mode="rb") as answer_file:
            answer = pickle.load(answer_file)

            class NumpyEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, np.integer):
                        return int(obj)
                    elif isinstance(obj, np.floating):
                        return float(obj)
                    elif isinstance(obj, np.ndarray):
                        return obj.tolist()
                    elif isinstance(obj, datetime.time):
                        return str(obj)
                    else:
                        return super(NumpyEncoder, self).default(obj)

            answer = json.dumps(answer, ensure_ascii=False, cls=NumpyEncoder)
            answer = json.loads(answer)
        """
        a = json.dumps(response["inputModel"]["top"], ensure_ascii=False, cls=MyEncoder)
        b = json.dumps(response["inputModel"]["sist"], ensure_ascii=False, cls=MyEncoder)
        c = json.dumps(response["inputModel"]["oper"], ensure_ascii=False, cls=MyEncoder)
        print(a)
        print(b)
        print(c)
        """

        response = {"answer": answer}
        Status.getJsonStatus(Status.OK, response)

        return JsonResponse(response, safe=False)
