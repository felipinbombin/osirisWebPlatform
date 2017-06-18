# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from django.shortcuts import redirect
from django.views.generic import View
from django.http import Http404

from scene.models import Scene

class DownloadStep2FileView(View):
    ''' link to downlaod the most recent file uploaded by user in step 2  '''

    def __init__(self):
        self.context = {}

    def get(self, request, sceneId):

        try:
            scene = Scene.objects.get(user=request.user, 
                id=sceneId)
        except:
            raise Http404

        return redirect(scene.step2File.url)

