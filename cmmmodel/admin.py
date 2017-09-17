# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import ModelExecutionHistory, ModelExecutionQueue, Model, PossibleQueue


class CMMModelAdmin(admin.ModelAdmin):
    fields = ('name', 'clusterExecutionId')
    list_display = ('name', 'clusterExecutionId')


class ModelExecutionHistoryAdmin(admin.ModelAdmin):
    fields = ('scene', 'model', 'start', 'end', 'status', 'jobNumber', 'externalId')
    list_display = ('scene', 'model', 'start', 'end', 'status', 'jobNumber', 'externalId')


admin.site.register(Model, CMMModelAdmin)
admin.site.register(ModelExecutionHistory, ModelExecutionHistoryAdmin)
admin.site.register(ModelExecutionQueue)
admin.site.register(PossibleQueue)
