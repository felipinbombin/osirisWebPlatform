# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-28 08:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmmmodel', '0014_auto_20170928_0530'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelexecutionhistory',
            name='check_answer',
            field=models.IntegerField(default=0, verbose_name=''),
        ),
    ]
