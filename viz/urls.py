from django.conf.urls import url
from viz.views.speed import SpeedModelViz, SpeedModelVizData
from viz.views.strong import StrongModelViz, StrongModelVizData
from viz.views.energy import EnergyModelViz, EnergyModelVizData
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^speed/(?P<sceneId>[0-9]+)$',
      login_required(SpeedModelViz.as_view()), name='speedModel'),
    url(r'^speed/data/(?P<sceneId>[0-9]+)$',
      login_required(SpeedModelVizData.as_view()), name='speedModelData'),
    url(r'^strong/(?P<sceneId>[0-9]+)$',
      login_required(StrongModelViz.as_view()), name='strongModel'),
    url(r'^strong/data/(?P<sceneId>[0-9]+)$',
      login_required(StrongModelVizData.as_view()), name='strongModelData'),
    url(r'^energy/(?P<sceneId>[0-9]+)$',
      login_required(EnergyModelViz.as_view()), name='energyModel'),
    url(r'^energy/data/(?P<sceneId>[0-9]+)$',
      login_required(EnergyModelVizData.as_view()), name='energyModelData'),
]
