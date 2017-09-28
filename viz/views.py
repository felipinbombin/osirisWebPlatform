from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View

from itertools import groupby
from collections import defaultdict

from scene.models import Scene
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
        self.context["op_periods"] = ["{} ({} - {})".format(op_period_obj.name,op_period_obj.start,op_period_obj.end) for op_period_obj in
                                       scene_obj.operationperiod_set.all().order_by("id")]
        self.context["chart_type"] = ["Velocidad vs Tiempo", "Velocidad vs Distancia"]

        return render(request, self.template, self.context)


class SpeedModelVizData(View):
    """ data for charts  """

    def get(self, request, sceneId):

        # check that user is owner
        try:
            Scene.objects.get(user=request.user, id=sceneId)
        except:
            raise Http404

        scene_id = int(sceneId)
        execution = ModelExecutionHistory.objects.filter(scene_id=scene_id, model_id=1).order_by("-id").first()
        answer = ModelAnswer.objects.filter(execution=execution).values_list("metroLine__name", "direction",
                                                                        "operationPeriod__name", "attributeName",
                                                                        "metroTrack__name", "value").\
            order_by("metroLine__name", "direction", "metroTrack__id", "operationPeriod__start", "attributeName", "order")

        groups = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(list))))
        for key, group in groupby(answer, lambda row : "{}_-_{}_-_{}_-_{}".format(row[0], row[1], row[2], row[3])):
            line, direction, op, attr = key.split("_-_")
            # group by track
            for key2, group2 in groupby(group, lambda row: row[4]):
                groups[line][direction][op][attr].append({key2: [v[5] for v in group2]})

        response = {}
        response["answer"] = groups

        return JsonResponse(response, safe=False)