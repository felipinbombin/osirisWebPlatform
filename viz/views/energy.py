# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View

from itertools import groupby

from scene.models import Scene, MetroLineMetric
from scene.statusResponse import Status
from cmmmodel.models import ModelExecutionHistory, Model
from viz.models import ModelAnswer


class EnergyModelViz(View):
    """ wizard form: first  """

    def __init__(self):
        super(EnergyModelViz, self).__init__()
        self.context = {}
        self.template = "viz/energy.html"

    def get(self, request, sceneId):
        try:
            scene_obj = Scene.objects.prefetch_related("metroline_set__metrostation_set"). \
                get(user=request.user, id=sceneId)
        except:
            raise Http404

        charts = [
            "Total - Consumptions",
            "Total - Energy Breakdown",
            "Trains - Consumption",
            "Trains - Energy Breakdown",
            "Tracks - Consumption",
            "Tracks - Energy Breakdown",
            "Stations - Consumption",
            "Stations - Energy Breakdown",
            "Depots - Consumption",
            "Depots - Energy Breakdown",
        ]
        self.context["charts"] = [{"value": index,
                                   "item": name} for index, name in enumerate(charts)]

        self.context["execution_obj"] = ModelExecutionHistory.objects.filter(scene=scene_obj,
                                                                             model_id=Model.ENERGY_MODEL_ID).order_by(
            "-id").first()

        return render(request, self.template, self.context)


class EnergyModelVizData(View):
    """ data for charts  """

    def get_model_data(self, execution_obj, prefix):
        """ get data have gotten from execution instance """

        answer = ModelAnswer.objects.prefetch_related(). \
            filter(execution=execution_obj, attributeName__startswith=prefix).values_list("attributeName", "value"). \
            order_by("attributeName", "order")

        groups = []
        for key, group in groupby(answer, lambda row: "{}".format(row[0].split("_")[0])):
            # group by key
            groupElement = {
                "prefix": key,
                "attributes": {}
            }
            for key2, value in group:
                groupElement["attributes"][key2.split("_")[1]] = value
            groups.append(groupElement)

        return groups

    def get(self, request, sceneId):

        # check that user is owner
        try:
            Scene.objects.get(user=request.user, id=sceneId)
        except:
            raise Http404

        # attributes to retrieve
        prefix = request.GET.get("prefix", "")

        scene_id = int(sceneId)
        execution_obj = ModelExecutionHistory.objects.filter(scene_id=scene_id, model_id=Model.ENERGY_MODEL_ID). \
            order_by("-id").first()

        response = {}
        if execution_obj is None:
            Status.getJsonStatus(Status.LAST_MODEL_ANSWER_DATA_DOES_NOT_EXISTS_ERROR, response)
        elif execution_obj.status != ModelExecutionHistory.OK:
            Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, response)
        else:
            response["answer"] = self.get_model_data(execution_obj, prefix)

        return JsonResponse(response, safe=False)
