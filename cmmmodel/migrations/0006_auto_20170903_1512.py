# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-03 18:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmmmodel', '0005_auto_20170903_1457'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelexecutionhistory',
            name='error',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='modelexecutionhistory',
            name='status',
            field=models.CharField(choices=[('running', 'En ejecución'), ('ok', 'Terminado exitosamente'), ('error', 'Terminado con error'), ('error to start', 'Error al iniciar'), ('cancel', 'Cancelado por el usuario')], default='running', max_length=40, verbose_name='Estado'),
        ),
    ]
