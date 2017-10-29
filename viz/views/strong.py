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


class StrongModelViz(View):
    """ wizard form: first  """

    def __init__(self):
        super(StrongModelViz, self).__init__()
        self.context = {}
        self.template = "viz/strong.html"

    def get(self, request, sceneId):
        try:
            scene_obj = Scene.objects.prefetch_related("metroline_set__metrostation_set"). \
                get(user=request.user, id=sceneId)
        except:
            raise Http404

        self.context["scene"] = scene_obj
        self.context["metro_lines"] = [metro_line_obj.name for metro_line_obj in
                                       scene_obj.metroline_set.all().order_by("id")]
        self.context["directions"] = [scene_obj.metroline_set.all().order_by("id")[0].get_name(direction) for direction
                                      in [MetroLineMetric.GOING, MetroLineMetric.REVERSE]]
        self.context["op_periods"] = [{"value": op_period_obj.name,
                                       "item": "{} ({} - {})".format(op_period_obj.name, op_period_obj.start,
                                                                     op_period_obj.end)} for op_period_obj in
                                      scene_obj.operationperiod_set.all().order_by("id")]
        self.context["execution_obj"] = ModelExecutionHistory.objects.filter(scene=scene_obj,
                                                                             model_id=Model.STRONG_MODEL_ID).order_by(
            "-id").first()

        return render(request, self.template, self.context)


class StrongModelVizData(View):
    """ data for charts  """

    def get_model_data(self, execution_obj, metro_line_name, direction, operation_period_name, attributes):
        """ get data have gotten from execution instance """

        answer = ModelAnswer.objects.prefetch_related("metroTrack__endStation", "metroTrack__startStation"). \
            filter(execution=execution_obj, attributeName__in=attributes). \
            values_list("operationPeriod__name", "metroLine__name", "direction", "attributeName", "value"). \
            order_by("operationPeriod__id", "metroLine__id", "direction", "metroTrack__id", "attributeName",
                     "order")

        if direction is not None:
            direction = MetroLineMetric.GOING if direction == "g" else MetroLineMetric.REVERSE
            answer = answer.filter(direction=direction)
        if operation_period_name is not None:
            answer = answer.filter(operationPeriod__name=operation_period_name)
        if metro_line_name is not None:
            answer = answer.filter(metroLine__name=metro_line_name)

        groups = []
        for key, group in groupby(answer, lambda row: "{}_-_{}_-_{}".format(row[0], row[1], row[2])):
            attr1, attr2, attr3 = key.split("_-_")
            # group by track
            groupElement = {
                "direction": attr3,
                "attributes": {}
            }
            for key2, group2 in groupby(group, lambda row: row[3]):
                groupElement["attributes"][key2] = [v[4] for v in group2]
            groups.append(groupElement)

        if direction == MetroLineMetric.REVERSE:
            groups.reverse()

        return groups

    def get(self, request, sceneId):

        # check that user is owner
        try:
            Scene.objects.get(user=request.user, id=sceneId)
        except:
            raise Http404

        # attributes to retrieve
        attributes = request.GET.getlist("attributes[]", [])
        direction = request.GET.get("direction", None)
        operation_period_name = request.GET.get("operationPeriod", None)
        metro_line_name = request.GET.get("metroLineName", None)

        scene_id = int(sceneId)
        execution_obj = ModelExecutionHistory.objects.filter(scene_id=scene_id, model_id=Model.STRONG_MODEL_ID). \
            order_by("-id").first()

        response = {}
        if execution_obj is None:
            Status.getJsonStatus(Status.LAST_MODEL_ANSWER_DATA_DOES_NOT_EXISTS_ERROR, response)
        elif execution_obj.status != ModelExecutionHistory.OK:
            Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, response)
        else:
            response["answer"] = self.get_model_data(execution_obj, metro_line_name, direction,
                                                     operation_period_name, attributes)

        return JsonResponse(response, safe=False)
