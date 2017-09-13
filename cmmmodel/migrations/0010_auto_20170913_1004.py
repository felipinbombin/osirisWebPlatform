# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-13 13:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmmmodel', '0009_auto_20170910_2044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelexecutionhistory',
            name='answer',
            field=models.FileField(null=True, upload_to=b'modelOutput/'),
        ),
        migrations.AlterField(
            model_name='modelexecutionhistory',
            name='status',
            field=models.CharField(choices=[(b'running', b'En ejecuci\xc3\xb3n'), (b'ok', b'Terminado exitosamente'), (b'error', b'Terminado con error'), (b'error to start', b'Error al iniciar'), (b'cancel', b'Cancelado por el usuario')], default=b'running', max_length=40, verbose_name=b'Estado'),
        ),
    ]
