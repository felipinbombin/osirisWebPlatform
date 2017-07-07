# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from django.shortcuts import redirect
from django.views.generic import View
from django.http import Http404

from scene.models import Scene


class DownloadStepFile(View):
    ''' link to download the most recent file uploaded by user in step 2,4,6 or 7 '''
    def get(self, request, stepId, sceneId):
        try:
            scene = Scene.objects.get(user=request.user, id=sceneId)
        except:
            raise Http404
        
        field = None
        stepId = int(stepId)
        if stepId == 1:
            field = scene.step1File
        elif stepId == 3:
            field = scene.step3File
        elif stepId == 5:
            field = scene.step5File
        elif stepId == 6:
            field = scene.step6File
        else:
            raise Http404

        if field == '':
            raise Http404

        return redirect(field.url)


class DownloadStepTemplate(View):
    ''' link to download the most recent file uploaded by user in step 2,4,6 or 7 '''
    def get(self, request, stepId, sceneId):
        try:
            scene = Scene.objects.get(user=request.user, id=sceneId)
        except:
            raise Http404
        
        field = None
        stepId = int(stepId)
        if stepId == 1:
            field = scene.step1Template
        elif stepId == 3:
            field = scene.step3Template
        elif stepId == 5:
            field = scene.step5Template
        elif stepId == 6:
            field = scene.step6Template
        else:
            raise Http404
        
        return redirect(field.url)

