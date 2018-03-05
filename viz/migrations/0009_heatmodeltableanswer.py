# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-05 04:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmmmodel', '0017_auto_20171013_1548'),
        ('scene', '0021_auto_20171129_0451'),
        ('viz', '0008_auto_20171120_0747'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeatModelTableAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direction', models.CharField(max_length=1, null=True)),
                ('attributeName', models.CharField(max_length=100)),
                ('value', models.FloatField()),
                ('execution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmmmodel.ModelExecutionHistory')),
                ('metroStation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene.MetroStation')),
            ],
        ),
    ]
