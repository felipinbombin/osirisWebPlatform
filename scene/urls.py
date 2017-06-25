from django.conf.urls import url
from .views.defaults import StepsView, ValidationStepView, GetStep1DataView
from .views.Panel import ScenePanel, ScenePanelData
from .views.UploadFile import UploadTopologicFileView
from .views.DownloadFile import DownloadStepFile, DownloadStepTemplate
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^scene/panel/(?P<sceneId>[0-9]+)$',
      login_required(ScenePanel.as_view()), name='panel'),
    url(r'^scene/panel/data/(?P<sceneId>[0-9]+)$',
      login_required(ScenePanelData.as_view()), name='panelData'),
    url(r'^scene/wizard/(?P<sceneId>[0-9]+)$',
      login_required(StepsView.as_view()), name='wizard'),
    url(r'^scene/wizard/validate/(?P<stepId>[0-9]+)/(?P<sceneId>[0-9]+)$', 
      login_required(ValidationStepView.as_view()), name='validation'),
    url(r'^scene/wizard/getStep1Data/(?P<sceneId>[0-9]+)$', 
      login_required(GetStep1DataView.as_view()), name='getStep1Data'),
    url(r'^scene/wizard/uploadTopologicFile/(?P<sceneId>[0-9]+)$', 
      login_required(UploadTopologicFileView.as_view()), name='uploadTopologicFile'),
    url(r'^scene/wizard/downloadStepFile/(?P<stepId>[0-9]+)/(?P<sceneId>[0-9]+)$', 
      login_required(DownloadStepFile.as_view()), name='downloadStepFile'),
    url(r'^scene/wizard/downloadStepTemplate/(?P<stepId>[0-9]+)/(?P<sceneId>[0-9]+)$', 
      login_required(DownloadStepTemplate.as_view()), name='downloadStepTemplate'),
]
