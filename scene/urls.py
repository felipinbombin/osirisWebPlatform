from django.conf.urls import url
from .views import FirstStepView

urlpatterns = [
    url(r'^scene/scene/step1/(?P<sceneId>[0-9]+)$', FirstStepView.as_view()),
#    url(r'^$', RoutePlanner.as_view()),
]
