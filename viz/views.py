# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View

from itertools import groupby

from scene.models import Scene, MetroLineMetric, OperationPeriodForMetroStation
from scene.statusResponse import Status
from cmmmodel.models import ModelExecutionHistory, Model
from viz.models import ModelAnswer


class SpeedModelViz(View):
    """ wizard form: first  """
    def __init__(self):
        super(SpeedModelViz, self).__init__()
        self.context = {}
        self.template = "viz/speed.html"

    def get(self, request, sceneId):
        try:
            scene_obj = Scene.objects.prefetch_related("metroline_set", "metroline_set__metrostation_set").\
                get(user=request.user, id=sceneId)

        except:
            raise Http404

        self.context["scene"] = scene_obj
        self.context["metro_lines"] = [metro_line_obj.name for metro_line_obj in
                                       scene_obj.metroline_set.all().order_by("id")]
        self.context["metro_stations"] = [metro_station_obj.name for metro_station_obj in
                                          scene_obj.metroline_set.all().order_by("id")[0].metrostation_set.all().order_by("id")]
        self.context["metro_stations2"] = [metro_station_obj.name for metro_station_obj in
                                          scene_obj.metroline_set.all().order_by("id")[0].metrostation_set.all().order_by("-id")]
        self.context["op_periods"] = [{"value": op_period_obj.name, "item": "{} ({} - {})".format(op_period_obj.name,op_period_obj.start,op_period_obj.end)} for op_period_obj in
                                       scene_obj.operationperiod_set.all().order_by("id")]
        self.context["table_titles"] = ["Sección", "Tiempo (seg)"]
        self.context["execution_obj"] = ModelExecutionHistory.objects.filter(scene=scene_obj, model_id=Model.SPEED_MODEL_ID).order_by("-id").first()

        return render(request, self.template, self.context)


class SpeedModelVizData(View):
    """ data for charts  """

    def get_dwell_time(self, operation_period_name, metro_line_name, direction, scene_id):
        """ get station list of dwell time """
        station_list = OperationPeriodForMetroStation.objects.filter(operationPeriod__scene_id=scene_id,
                                                                     operationPeriod__name=operation_period_name,
                                                                     metroStation__metroLine__name=metro_line_name,
                                                                     direction=direction,
                                                                     metric=OperationPeriodForMetroStation.DWELL_TIME).\
            order_by("metroStation_id").values_list("metroStation__name", "value")

        answer = {}
        for station in station_list:
            answer[station[0]] = station[1]
        return answer

    def get_model_data(self, execution_obj, metro_line_name, metro_tracks, direction, operation_period_name, attributes):
        """ get data have gotten from execution instance """

        answer = ModelAnswer.objects.prefetch_related("metroTrack__endStation", "metroTrack__startStation").\
            filter(execution=execution_obj, attributeName__in=attributes, metroTrack__externalId__in=metro_tracks).\
            values_list("operationPeriod__name", "metroLine__name", "direction",
                        "metroTrack__startStation__name", "metroTrack__endStation__name", "attributeName", "value").\
            order_by("operationPeriod__id", "metroLine__id", "direction", "metroTrack__id", "attributeName",
                     "order")

        if direction is not None:
            direction = MetroLineMetric.GOING if direction == "g" else MetroLineMetric.REVERSE
            answer = answer.filter(direction=direction)
        if operation_period_name is not None:
            answer = answer.filter(operationPeriod__name=operation_period_name)
        if metro_line_name is not None:
            answer = answer.filter(metroLine__name=metro_line_name)

        # groups = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(list))))
        groups = []
        for key, group in groupby(answer, lambda row : "{}_-_{}_-_{}_-_{}_-_{}".format(row[0], row[1], row[2], row[3], row[4])):
            attr1, attr2, attr3, attr4, attr5 = key.split("_-_")
            # group by track
            groupElement = {
                "direction": attr3,
                "startStation": attr4,
                "endStation": attr5,
                "attributes": {}
            }
            for key2, group2 in groupby(group, lambda row: row[5]):
                #groups[attr1][attr2][attr3][attr4].append({"name": key2, "value": [v[5] for v in group2]})
                groupElement["attributes"][key2] = [v[6] for v in group2]
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
        metro_tracks = request.GET.getlist("tracks[]", [])

        scene_id = int(sceneId)
        execution_obj = ModelExecutionHistory.objects.filter(scene_id=scene_id, model_id=1).order_by("-id").first()

        response = {
            "dwellTime": self.get_dwell_time(operation_period_name, metro_line_name, direction, scene_id)
        }
        if execution_obj is None:
            Status.getJsonStatus(Status.LAST_MODEL_ANSWER_DATA_DOES_NOT_EXISTS_ERROR, response)
        elif execution_obj.status != ModelExecutionHistory.OK:
            Status.getJsonStatus(Status.LAST_MODEL_FINISHED_BADLY_ERROR, response)
        else:
            response["answer"] = self.get_model_data(execution_obj, metro_line_name, metro_tracks, direction,
                                                     operation_period_name, attributes)

        return JsonResponse(response, safe=False)