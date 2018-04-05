# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import ModelExecutionHistory, ModelExecutionQueue, CMMModel, PossibleQueue


class CMMModelAdmin(admin.ModelAdmin):
    fields = ('name', 'clusterExecutionId')
    list_display = ('name', 'clusterExecutionId')


class ModelExecutionHistoryAdmin(admin.ModelAdmin):
    def get_username(self, obj):
        return obj.scene.user.username
    get_username.short_description = "usuario"
    fields = (('scene', 'model'), ('start', 'end'), 'status', ('jobNumber', 'externalId'), 'std_out', 'std_err', 'answer')
    list_display = ('get_username', 'scene', 'model', 'start', 'end', 'status', 'jobNumber', 'externalId')


admin.site.register(CMMModel, CMMModelAdmin)
admin.site.register(ModelExecutionHistory, ModelExecutionHistoryAdmin)
admin.site.register(ModelExecutionQueue)
admin.site.register(PossibleQueue)
