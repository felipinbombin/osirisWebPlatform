from django.conf.urls import url
from .views import StepsView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^scene/wizard/(?P<sceneId>[0-9]+)$', login_required(StepsView.as_view()), name='wizard'),
#    url(r'^$', RoutePlanner.as_view()),
]
