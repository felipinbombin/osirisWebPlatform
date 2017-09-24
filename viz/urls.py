from django.conf.urls import url
from .views import SpeedModelViz, SpeedModelVizData
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^viz/speed/(?P<sceneId>[0-9]+)$',
      login_required(SpeedModelViz.as_view()), name='speedModel'),
    url(r'^viz/speed/data/(?P<sceneId>[0-9]+)$',
      login_required(SpeedModelVizData.as_view()), name='speedModelData'),
    url(r'^viz/strong/(?P<sceneId>[0-9]+)$',
      login_required(SpeedModelViz.as_view()), name='strongModel')
]
