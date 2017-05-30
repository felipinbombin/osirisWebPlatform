# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import Scene

# Register your models here.
class SceneAdmin(admin.ModelAdmin):
    #date_hierarchy = 'timeCreation'
    #fields = ('name',)
    fieldsets = (
        (None, {'fields': ('name',)}),
    )
    list_filter = []
    list_display = ('name', 'timeCreation', 'metroLineQuantity', 'status')

    #def save_model(self, request, obj, form, change):

    


admin.site.register(Scene, SceneAdmin)
