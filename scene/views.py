# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import Http404
from django.http import JsonResponse

from .models import Scene

from .forms import FirstStepForm, SecondStepForm, ThirdStepForm, FourthStepForm, FithStepForm, SixthStepForm

import json

class StepsView(View):
    ''' wizard form: first  '''
    def __init__(self):
        self.context = {}
        self.template = 'scene/wizard.html'

    def post(self, request):
        # if this is a POST request we need to process the form data

        # create a form instance and populate it with data from the request:
        form = FirstStepForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

        return render(request, self.template, {'form': form})

    def get(self, request, sceneId):

        try:
            self.context['scene'] = Scene.objects.get(user=request.user, id=sceneId)
        except:
            raise Http404

        return render(request, self.template, self.context)

class ValidationStepView(View):
    ''' validate data from step '''

    def __init__(self):
        self.context = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ValidationStepView, self).dispatch(request, *args, **kwargs)

    def post(self, request, stepId, sceneId):
        """ validate and update data in server """

        print '==============='
        print request.POST
        print '==============='
        if stepId == 1:
           # global topologic variables
           data = request.POST.get('data')
           data = json.loads(data)
           scene = Scene.objects.get(user=request.user, id=sceneId)


        response = {}
        return JsonResponse(response, safe=False)




