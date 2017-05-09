# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import Group, User

# Register your models here.
admin.site.unregister(Group)
#admin.site.unregister(User)

#class UserAdmin(models.Admin):
#    pass

#admin.site.register(User, UserAdmin)
