from django.conf.urls import url
from viz.views.speed import SpeedModelViz, SpeedModelVizData
from viz.views.strong import StrongModelViz, StrongModelVizData
from viz.views.energy import EnergyModelViz, EnergyModelVizData
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^speed/(?P<scene_id>[0-9]+)$',
      login_required(SpeedModelViz.as_view()), name='speedModel'),
    url(r'^speed/data/(?P<scene_id>[0-9]+)$',
      login_required(SpeedModelVizData.as_view()), name='speedModelData'),
    url(r'^strong/(?P<scene_id>[0-9]+)$',
      login_required(StrongModelViz.as_view()), name='strongModel'),
    url(r'^strong/data/(?P<scene_id>[0-9]+)$',
      login_required(StrongModelVizData.as_view()), name='strongModelData'),
    url(r'^energy/(?P<scene_id>[0-9]+)$',
      login_required(EnergyModelViz.as_view()), name='energyModel'),
    url(r'^energy/data/(?P<scene_id>[0-9]+)$',
      login_required(EnergyModelVizData.as_view()), name='energyModelData'),
]
