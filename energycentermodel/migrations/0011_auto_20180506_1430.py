# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-06 17:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('energycentermodel', '0010_auto_20180506_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atributos_ser',
            name='Vdc',
            field=models.IntegerField(),
        ),
    ]
