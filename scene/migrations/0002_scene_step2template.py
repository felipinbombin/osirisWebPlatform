# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-15 23:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scene', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='scene',
            name='step2Template',
            field=models.FileField(null=True, upload_to='step2Template/'),
        ),
    ]
