from django.conf.urls import url
from .views import FirstStepView

urlpatterns = [
    url(r'^$', FirstStepView.as_view()),
#    url(r'^$', RoutePlanner.as_view()),
]
