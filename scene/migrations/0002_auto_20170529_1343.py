# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-29 17:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scene', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scene',
            options={'verbose_name': 'escenario', 'verbose_name_plural': 'escenarios'},
        ),
        migrations.AlterField(
            model_name='scene',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Nombre'),
        ),
    ]
