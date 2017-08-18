from django.conf.urls import url
from .views.defaults import StepsView, ValidationStepView
from .views.SceneData import GetSceneData
from .views.Panel import ScenePanel, ScenePanelData, InputModelData, ChangeSceneName, DeleteScene
from .views.UploadFile import UploadTopologicFile, UploadSystemicFile, UploadOperationalFile, UploadSpeedFile
from .views.DownloadFile import DownloadStepFile, DownloadStepTemplate
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^scene/panel/(?P<sceneId>[0-9]+)$',
      login_required(ScenePanel.as_view()), name='panel'),
    url(r'^scene/panel/data/(?P<sceneId>[0-9]+)$',
      login_required(ScenePanelData.as_view()), name='panelData'),
    url(r'^scene/panel/data/inputModel/(?P<sceneId>[0-9]+)$',
      login_required(InputModelData.as_view()), name='inputModelData'),
    url(r'^scene/panel/changeName/(?P<scene_id>[0-9]+)$',
      login_required(ChangeSceneName.as_view()), name='changeSceneName'),
    url(r'^scene/panel/delete/(?P<scene_id>[0-9]+)$',
      login_required(DeleteScene.as_view()), name='deleteScene'),

    url(r'^scene/wizard/(?P<sceneId>[0-9]+)$',
      login_required(StepsView.as_view()), name='wizard'),
    url(r'^scene/wizard/validate/(?P<stepId>[0-9]+)/(?P<sceneId>[0-9]+)$', 
      login_required(ValidationStepView.as_view()), name='validation'),

    # get data for scene id
    url(r'^scene/wizard/getSceneData/(?P<sceneId>[0-9]+)$',
      login_required(GetSceneData.as_view()), name='getSceneData'),

    # step 1
    url(r'^scene/wizard/uploadTopologicFile/(?P<sceneId>[0-9]+)$', 
      login_required(UploadTopologicFile.as_view()), name='uploadTopologicFile'),
    # step 3
    url(r'^scene/wizard/uploadSystemicFile/(?P<sceneId>[0-9]+)$', 
      login_required(UploadSystemicFile.as_view()), name='uploadSystemicFile'),
    # step 5
    url(r'^scene/wizard/uploadOperationalFile/(?P<sceneId>[0-9]+)$', 
      login_required(UploadOperationalFile.as_view()), name='uploadOperationalFile'),
    # step 6
    url(r'^scene/wizard/uploadSpeedFile/(?P<sceneId>[0-9]+)$',
      login_required(UploadSpeedFile.as_view()), name='uploadSpeedFile'),

    # for steps 1,3,5 and 6
    url(r'^scene/wizard/downloadStepFile/(?P<stepId>[0-9]+)/(?P<sceneId>[0-9]+)$', 
      login_required(DownloadStepFile.as_view()), name='downloadStepFile'),
    # for steps 1,3,5 and 6
    url(r'^scene/wizard/downloadStepTemplate/(?P<stepId>[0-9]+)/(?P<sceneId>[0-9]+)$', 
      login_required(DownloadStepTemplate.as_view()), name='downloadStepTemplate')
]
