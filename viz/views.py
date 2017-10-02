from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View

from itertools import groupby
from collections import defaultdict

from scene.models import Scene, MetroLineMetric
from cmmmodel.models import ModelExecutionHistory
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
        self.context["chart_type"] = [{"item": "Velocidad", "value": 1},
                                      {"item": "Velocidad vs Distancia", "value": 2}]

        return render(request, self.template, self.context)


class SpeedModelVizData(View):
    """ data for charts  """

    def get(self, request, sceneId):

        # check that user is owner
        try:
            Scene.objects.get(user=request.user, id=sceneId)
        except:
            raise Http404

        # attributes to retrieve
        attributes = request.GET.getlist("attributes[]", [])
        direction = request.GET.get("direction", None)

        scene_id = int(sceneId)
        execution = ModelExecutionHistory.objects.filter(scene_id=scene_id, model_id=1).order_by("-id").first()
        answer = ModelAnswer.objects.filter(execution=execution).filter(attributeName__in=attributes).\
            values_list("attributeName", "operationPeriod__name", "metroLine__name", "direction", "metroTrack__name",
                        "order", "value").\
            order_by("attributeName", "operationPeriod__name", "metroLine__name", "direction", "metroTrack__name",
                     "order")
        if direction is not None:
            direction = MetroLineMetric.GOING if direction == "g" else MetroLineMetric.REVERSE
            answer = answer.filter(direction=direction)

        groups = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(list))))
        for key, group in groupby(answer, lambda row : "{}_-_{}_-_{}_-_{}".format(row[0], row[1], row[2], row[3])):
            attr1, attr2, attr3, attr4 = key.split("_-_")
            # group by track
            for key2, group2 in groupby(group, lambda row: row[4]):
                groups[attr1][attr2][attr3][attr4].append({"name": key2, "value": [v[5] for v in group2]})

        response = {
            "answer": groups
        }

        response["answer"] = {
            "H2": {
                "L1": {
                    "Distance": {
                        "g": [{"name": "S1-S2", "value": [1,2,3]}, {"name": "S2-S3", "value": [4,5,6]}]
                    }
                },
                "L2": {
                    "Distance": {
                        "g": [{"name":"S3-S4", "value": [7,8,9]}, {"name":"S4-S5", "value": [10,11,12]}]
                    }
                }
            }
        }
        return JsonResponse(response, safe=False)