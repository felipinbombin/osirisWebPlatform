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
        if stepId == 2:
            field = scene.step2File
        elif stepId == 4:
            field = scene.step4File
        elif stepId == 6:
            field = scene.step6File
        elif stepId == 7:
            field = scene.step7File
        else:
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
        if stepId == 2:
            field = scene.step2Template
        elif stepId == 4:
            field = scene.step4Template
        elif stepId == 6:
            field = scene.step6Template
        elif stepId == 7:
            field = scene.step7Template
        else:
            raise Http404
        
        return redirect(field.url)

