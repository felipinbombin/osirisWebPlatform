from django.conf.urls import url
from viz.views.speed import SpeedModelViz, SpeedModelVizData
from viz.views.force import ForceModelViz, ForceModelVizData
from viz.views.energy import EnergyModelViz, EnergyModelVizData
from viz.views.heat import ThermalModelViz, ThermalModelVizData
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^speed/(?P<scene_id>[0-9]+)$',
      login_required(SpeedModelViz.as_view()), name='speedModel'),
    url(r'^speed/data/(?P<scene_id>[0-9]+)$',
      login_required(SpeedModelVizData.as_view()), name='speedModelData'),
    url(r'^force/(?P<scene_id>[0-9]+)$',
      login_required(ForceModelViz.as_view()), name='forceModel'),
    url(r'^force/data/(?P<scene_id>[0-9]+)$',
      login_required(ForceModelVizData.as_view()), name='forceModelData'),
    url(r'^energy/(?P<scene_id>[0-9]+)$',
      login_required(EnergyModelViz.as_view()), name='energyModel'),
    url(r'^energy/data/(?P<scene_id>[0-9]+)$',
      login_required(EnergyModelVizData.as_view()), name='energyModelData'),
    url(r'^heat/(?P<scene_id>[0-9]+)$',
      login_required(ThermalModelViz.as_view()), name='thermalModel'),
    url(r'^heat/data/(?P<scene_id>[0-9]+)$',
      login_required(ThermalModelVizData.as_view()), name='thermalModelData'),
]
