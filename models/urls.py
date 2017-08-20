from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import Stop, Run, Status

urlpatterns = [
    url(r'^run$',
        login_required(Run.as_view()), name='run'),
    url(r'^stop$',
        login_required(Stop.as_view()), name='stop'),
    url(r'^status$',
        login_required(Status.as_view()), name='status'),
]
