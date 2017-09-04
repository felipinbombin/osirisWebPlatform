# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import ModelExecutionHistory, ModelExecutionQueue, Model, PossibleQueue

admin.site.register(Model)
admin.site.register(ModelExecutionHistory)
admin.site.register(ModelExecutionQueue)
admin.site.register(PossibleQueue)
