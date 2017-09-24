from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View

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
            self.context["scene"] = Scene.objects.get(user=request.user, id=sceneId)
        except:
            raise Http404

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
            order_by("metroLine__name", "direction", "metroTrack__name", "operationPeriod__name", "attributeName", "order")
        from itertools import groupby
        from collections import defaultdict
        groups = defaultdict(defaultdict(dict))
        for key, group in groupby(answer, lambda row : "{}_-_{}_-_{}_-_{}".format(row[0], row[1], row[2], row[3])):
            group = list(group)
            line, direction, op, attr = key.split("_-_")
            # group by track
            for key2, group2 in groupby(group, lambda row: row[4]):
                groups[line][direction][op][attr][key2] = list(group2)
                print(key, key2, len(list(group2)))

        response = {}
        response["answer"] = groups

        for row in answer:
            response["answer"].append(row)

        return JsonResponse(response, safe=False)