# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-13 18:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmmmodel', '0016_auto_20171004_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelexecutionhistory',
            name='downloadFile',
            field=models.FileField(null=True, upload_to='modelOutputFile/'),
        ),
    ]
