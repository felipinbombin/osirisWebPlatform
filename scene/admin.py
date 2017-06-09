# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils import timezone
from django.shortcuts import redirect
from models import Scene

# Register your models here.
class SceneAdmin(admin.ModelAdmin):
    #date_hierarchy = 'timeCreation'
    #fields = ('name',)
    fieldsets = (
        (None, {'fields': ('name',)}),
    )
    list_filter = []
    list_display = ('name', 'timeCreation', 'status')

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.timeCreation = timezone.now()

        super(SceneAdmin, self).save_model(request, obj, form, change)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        
        return super(SceneAdmin, self).add_view(request, form_url, extra_context)

    def response_add(self, request, obj, post_url_continue=None):
        url = '/admin/scene/wizard/{}'.format(obj.id)
        return redirect(url)
        return super(SceneAdmin, self).response_add(request, ibj, post_url_continue)

admin.site.register(Scene, SceneAdmin)
