from django.conf.urls import url
from .views import SpeedModelViz, SpeedModelVizData
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^speed/(?P<sceneId>[0-9]+)$',
      login_required(SpeedModelViz.as_view()), name='speedModel'),
    url(r'^speed/data/(?P<sceneId>[0-9]+)$',
      login_required(SpeedModelVizData.as_view()), name='speedModelData'),
    url(r'^strong/(?P<sceneId>[0-9]+)$',
      login_required(SpeedModelViz.as_view()), name='strongModel')
]
