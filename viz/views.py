from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from scene.models import Scene

import json


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
