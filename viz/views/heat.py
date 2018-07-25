# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django.utils.translation import ugettext as _

from collections import OrderedDict

from itertools import groupby

from scene.models import Scene
from scene.statusResponse import Status

from cmmmodel.models import ModelExecutionHistory, CMMModel
from cmmmodel.transform.processThermalData import ProcessThermalData

from viz.models import ModelAnswer, HeatModelTableAnswer


class ThermalModelViz(View):

    def __init__(self):
        super(ThermalModelViz, self).__init__()
        self.context = {}
        self.template = "viz/heat.html"

    def get(self, request, scene_id):
        try:
            scene_obj = Scene.objects.prefetch_related("metroline_set__metrostation_set"). \
                get(user=request.user, id=scene_id)
        except Scene.DoesNotExist:
            raise Http404

        charts = []
        for key in ProcessThermalData.dictionary_group.keys():
            charts.append({
                "value": key,
                "item": _(ProcessThermalData.dictionary_group[key])
            })
        lines = []
        for line_obj in scene_obj.metroline_set.all().order_by("id"):
            lines.append({
                "value": line_obj.id,
                "item": line_obj.name
            })
        self.context["charts"] = charts
        self.context["lines"] = lines
        self.context["execution_obj"] = ModelExecutionHistory.objects.filter(scene=scene_obj,
                                                                             model_id=CMMModel.THERMAL_MODEL_ID). \
            order_by("-id").first()

        return render(request, self.template, self.context)


class ThermalModelVizData(View):
    """ data for charts  """

    def get_model_data(self, execution_obj, prefix, line_id):
        """ get data have gotten from execution instance """
        translated_prefix = ProcessThermalData.dictionary_group[prefix]
        groups = []

        if prefix.startswith('average'):
            answer = HeatModelTableAnswer.objects.filter(execution=execution_obj, attributeName=translated_prefix,
                                                         metroStation__metroLine_id=line_id). \
                values_list('group', 'operationPeriod__name', 'metroStation__name', 'value'). \
                order_by('group', 'operationPeriod', 'metroStation')

            metro_stations = OrderedDict()
            for key, group in groupby(answer, lambda row: row[0]):
                # group by key
                group_element = {
                    "group": _(key),
                    "opPeriods": []
                }
                for key2, rows in groupby(group, lambda row: row[1]):
                    values = []
                    for data in rows:
                        metro_stations[data[2]] = 1
                        values.append(data[3])
                    group_element["opPeriods"].append({
                        'name': key2,
                        'values': values,
                    })

                group_element['row'] = list(metro_stations.keys())
                groups.append(group_element)
        else:
            answer = ModelAnswer.objects. \
                filter(execution=execution_obj, attributeName=translated_prefix).values_list("order", "value"). \
                order_by("order")

            group_element = {
                "x": [],
                "y": []
            }
            for record in answer:
                group_element["x"].append(record[0])
                group_element["y"].append(record[1])
            groups.append(group_element)

        return groups

    def get(self, request, scene_id):

        # check that user is owner
        try:
            Scene.objects.get(user=request.user, id=scene_id)
        except Scene.DoesNotExist:
            raise Http404

        # attributes to retrieve
        prefix = request.GET.get("prefix", "")
        line_id = request.GET.get("lineId", "")

        scene_id = int(scene_id)
        execution_obj = ModelExecutionHistory.objects.filter(scene_id=scene_id, model_id=CMMModel.THERMAL_MODEL_ID). \
            order_by("-id").first()

        response = {}
        if execution_obj is None:
            Status.getJsonStatus(Status.LAST_MODEL_ANSWER_DATA_DOES_NOT_EXISTS_ERROR, response)
        elif execution_obj.status != ModelExecutionHistory.OK:
            Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, response)
        else:
            response["answer"] = self.get_model_data(execution_obj, prefix, line_id)

        return JsonResponse(response, safe=False)
