# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-15 17:32
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MetroConnection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('externalId', models.UUIDField(unique=True)),
                ('isOld', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=100)),
                ('avgHeight', models.FloatField(null=True)),
                ('avgSurface', models.FloatField(null=True)),
                ('consumption', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MetroConnectionStation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isOld', models.BooleanField(default=False)),
                ('externalId', models.UUIDField(unique=True)),
                ('metroConnection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene.MetroConnection')),
            ],
        ),
        migrations.CreateModel(
            name='MetroDepot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('externalId', models.UUIDField(unique=True)),
                ('isOld', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=100)),
                ('auxConsumption', models.FloatField(null=True)),
                ('ventilationConsumption', models.FloatField(null=True)),
                ('dcConsumption', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MetroLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('externalId', models.UUIDField(unique=True)),
                ('isOld', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=100)),
                ('usableEnergyContent', models.FloatField(null=True)),
                ('chargingEfficiency', models.FloatField(null=True)),
                ('dischargingEfficiency', models.FloatField(null=True)),
                ('peakPower', models.FloatField(null=True)),
                ('maximumEnergySavingPossiblePerHour', models.FloatField(null=True)),
                ('energySavingMode', models.FloatField(null=True)),
                ('powerLimitToFeed', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MetroLineMetric',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metric', models.CharField(max_length=50)),
                ('end', models.FloatField(null=True)),
                ('start', models.FloatField(null=True)),
                ('value', models.FloatField(null=True)),
                ('direction', models.CharField(max_length=50)),
                ('metroLine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene.MetroLine')),
            ],
        ),
        migrations.CreateModel(
            name='MetroStation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('externalId', models.UUIDField(unique=True)),
                ('isOld', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=100)),
                ('length', models.FloatField(null=True)),
                ('secondLevelAverageHeight', models.FloatField(null=True)),
                ('secondLevelFloorSurface', models.FloatField(null=True)),
                ('platformSection', models.FloatField(null=True)),
                ('platformAveragePermiter', models.FloatField(null=True)),
                ('minAuxConsumption', models.FloatField(null=True)),
                ('maxAuxConsumption', models.FloatField(null=True)),
                ('minHVACConsumption', models.FloatField(null=True)),
                ('maxHVACConsumption', models.FloatField(null=True)),
                ('tau', models.FloatField(null=True)),
                ('metroLine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene.MetroLine')),
            ],
        ),
        migrations.CreateModel(
            name='MetroTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('crossSection', models.FloatField(null=True)),
                ('averagePerimeter', models.FloatField(null=True)),
                ('length', models.FloatField(null=True)),
                ('auxiliariesConsumption', models.FloatField(null=True)),
                ('ventilationConsumption', models.FloatField(null=True)),
                ('endStation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='endstation', to='scene.MetroStation')),
                ('startStation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='startstation', to='scene.MetroStation')),
            ],
        ),
        migrations.CreateModel(
            name='OperationPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('start', models.TimeField()),
                ('end', models.TimeField()),
                ('temperature', models.FloatField()),
                ('humidity', models.FloatField()),
                ('co2Concentration', models.FloatField()),
                ('solarRadiation', models.FloatField()),
                ('sunElevationAngle', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Scene',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre')),
                ('timeCreation', models.DateTimeField(verbose_name='Fecha de creaci\xf3n')),
                ('status', models.CharField(choices=[('In', 'Incompleto'), ('OK', 'Completo')], default='In', max_length=2, verbose_name='Estado')),
                ('lastSuccessfullStep', models.IntegerField(default=0, verbose_name='Paso pendiente')),
                ('averageMassOfAPassanger', models.FloatField(null=True)),
                ('annualTemperatureAverage', models.FloatField(null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'escenario',
                'verbose_name_plural': 'escenarios',
            },
        ),
        migrations.AddField(
            model_name='operationperiod',
            name='scene',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene.Scene'),
        ),
        migrations.AddField(
            model_name='metroline',
            name='scene',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene.Scene'),
        ),
        migrations.AddField(
            model_name='metrodepot',
            name='metroLine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene.MetroLine'),
        ),
        migrations.AddField(
            model_name='metroconnectionstation',
            name='metroStation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene.MetroStation'),
        ),
        migrations.AddField(
            model_name='metroconnection',
            name='scene',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scene.Scene'),
        ),
        migrations.AddField(
            model_name='metroconnection',
            name='stations',
            field=models.ManyToManyField(through='scene.MetroConnectionStation', to='scene.MetroStation'),
        ),
        migrations.AlterUniqueTogether(
            name='scene',
            unique_together=set([('user', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='metrostation',
            unique_together=set([('metroLine', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='metroline',
            unique_together=set([('scene', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='metrodepot',
            unique_together=set([('metroLine', 'name')]),
        ),
    ]
