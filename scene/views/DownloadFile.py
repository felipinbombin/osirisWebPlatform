# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from django.shortcuts import redirect
from django.views.generic import View
from django.http import Http404

from scene.models import Scene


class DownloadStepFile(View):
    """ link to download the most recent file uploaded by user in step 2,4,6 or 7 """

    def get(self, request, step_id, scene_id):
        try:
            scene = Scene.objects.get(user=request.user, id=scene_id)
        except:
            raise Http404

        step_id = int(step_id)
        if step_id == 1:
            field = scene.step1File
        elif step_id == 3:
            field = scene.step3File
        elif step_id == 5:
            field = scene.step5File
        elif step_id == 6:
            field = scene.step6File
        else:
            raise Http404

        if field == "":
            raise Http404

        return redirect(field.url)


class DownloadStepTemplate(View):
    """ link to download the most recent file uploaded by user in step 2,4,6 or 7 """

    def get(self, request, step_id, scene_id):
        try:
            scene = Scene.objects.get(user=request.user, id=scene_id)
        except:
            raise Http404

        step_id = int(step_id)
        if step_id == 1:
            field = scene.step1Template
        elif step_id == 3:
            field = scene.step3Template
        elif step_id == 5:
            field = scene.step5Template
        elif step_id == 6:
            field = scene.step6Template
        else:
            raise Http404

        return redirect(field.url)
