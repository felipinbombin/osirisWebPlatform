from django.conf.urls import url
from .views import StepsView, ValidationStepView, GetStep1DataView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^scene/wizard/(?P<sceneId>[0-9]+)$',
      login_required(StepsView.as_view()), name='wizard'),
    url(r'^scene/wizard/validate/(?P<stepId>[0-9]+)/(?P<sceneId>[0-9]+)$', 
      login_required(ValidationStepView.as_view()), name='validation'),
    url(r'^scene/wizard/getStep1Data/(?P<sceneId>[0-9]+)$', 
      login_required(GetStep1DataView.as_view()), name='getStep1Data'),
    
#    url(r'^$', RoutePlanner.as_view()),
]
