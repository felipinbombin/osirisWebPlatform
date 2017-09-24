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
                                                                             "metroTrack__name",
                                                                             "operationPeriod__name", "attributeName",
                                                                             "order", "value")
        response = {}
        response["answer"] = []

        for row in answer:
            response["answer"].append(row)

        return JsonResponse(response, safe=False)