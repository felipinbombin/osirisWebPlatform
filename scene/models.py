# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

import uuid

# Create your models here.
class Scene(models.Model):
    ''' group of parameter to run models '''
    #######################################################
    # INTERNAL VARIABLES
    #######################################################
    name = models.CharField('Nombre', max_length=100)
    timeCreation = models.DateTimeField('Fecha de creación', null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    INCOMPLETE = 'In'
    OK = 'OK' 
    STATUS = (
        (INCOMPLETE, 'Incompleto'),
        (OK, 'Completo'),
    )
    status = models.CharField('Estado', max_length=2, choices=STATUS, default=INCOMPLETE)
    lastSuccessfullStep = models.IntegerField('Paso pendiente', default=0)
    #######################################################
    # GLOBAL CONDITION
    #######################################################
    averageMassOfAPassanger = models.FloatField(null=True)
    annualTemperatureAverage = models.FloatField(null=True)

    class Meta:
        verbose_name = 'escenario'
        verbose_name_plural = 'escenarios'

    def __str__(self):
        return self.name

class MetroLine(models.Model):
    ''' metro line '''
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    externalId = models.UUIDField(default=uuid.uuid4());
    ''' uses to track record in wizard form, this way i know if is new record or previous '''
    name = models.CharField(max_length=100)
    #######################################################
    # CONSUMPTION                                         
    #######################################################
    usableEnergyContent = models.FloatField(null=True);
    ''' unit:  '''
    chargingEfficiency = models.FloatField(null=True);
    ''' unit:  '''
    dischargingEfficiency = models.FloatField(null=True);
    ''' unit:  '''
    peakPower = models.FloatField(null=True);
    ''' unit:  '''
    maximumEnergySavingPossiblePerHour = models.FloatField(null=True);
    ''' unit:  '''
    energySavingMode = models.FloatField(null=True);
    ''' unit:  '''
    powerLimitToFeed = models.FloatField(null=True);
    ''' unit:  '''

    def getDict(self):
        ''' dict '''
        dict = {}
        dict['id'] = self.externalId
        dict['name'] = self.name
        dict['stations'] = []

        for station in self.stations:
            dict['stations'].append(station.getDict())

        return dict


class MetroStation(models.Model):
    ''' metro station'''
    metroLine = models.ForeignKey(MetroLine, on_delete=models.CASCADE)
    externalId = models.UUIDField(default=uuid.uuid4());
    ''' uses to track record in wizard form, this way i know if is new record or previous '''
    name = models.CharField(max_length=100)
    length = models.FloatField(null=True)
    ''' length of the stations. Unit: meters '''
    secondLevelAverageHeight = models.FloatField(null=True)
    ''' unit: meters '''
    secondLevelFloorSurface = models.FloatField(null=True)
    ''' unit: square meters '''
    platformSection = models.FloatField(null=True)
    ''' unit: square meters '''
    platformAveragePermiter = models.FloatField(null=True)
    ''' unit: meters '''
    #######################################################
    # CONSUMPTION                                         
    #######################################################
    minAuxConsumption = models.FloatField(null=True);
    ''' unit:  '''
    maxAuxConsumption = models.FloatField(null=True);
    ''' unit:  '''
    minHVACConsumption = models.FloatField(null=True);
    ''' unit:  '''
    maxHVACConsumption = models.FloatField(null=True);
    ''' unit:  '''
    tau = models.FloatField(null=True);
    ''' unit:  '''

    def getDict(self):
        ''' dict structure '''
        dict = {}
        dict['id'] = self.externalId
        dict['name'] = self.name

        return dict


class MetroDepot(models.Model):
    ''' train depot '''
    metroLine = models.ForeignKey(MetroLine, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    #######################################################
    # CONSUMPTION                                         
    #######################################################
    auxConsumption = models.FloatField(null=True);
    ''' unit:  '''
    ventilationConsumption = models.FloatField(null=True);
    ''' unit:  '''
    dcConsumption = models.FloatField(null=True);
    ''' unit:  '''
    

class MetroConnection(models.Model):
    ''' connection between metro stations fo different metro lines '''
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    externalId = models.UUIDField(default=uuid.uuid4());
    ''' uses to track record in wizard form, this way i know if is new record or previous '''
    name = models.CharField(max_length=100)
    stations = models.ManyToManyField(MetroStation)
    avgHeight = models.FloatField(null=True);
    ''' unit: meters '''
    avgSurface = models.FloatField(null=True);
    ''' unit: square meters '''
    #######################################################
    # CONSUMPTION                                         
    #######################################################
    consumption = models.FloatField(null=True);
    ''' unit:  '''

    def getDict(self):
        ''' dict '''
        dict = {}
        dict['id'] = self.externalId
        dict['name'] = self.name
        dict['avgHeight'] = self.avgHeight
        dict['avgSurface'] = self.avgSurface
        dict['stations'] = []

        for station in self.stations:
            dict['stations'].append(station.getDict())

        return dict

class MetroTrack(models.Model):
    ''' connection between metro stations '''
    name = models.CharField(max_length=100)
    startStation = models.ForeignKey(MetroStation, 
        related_name= 'startstation', 
        on_delete=models.CASCADE)
    endStation = models.ForeignKey(MetroStation, 
        related_name= 'endstation', 
        on_delete=models.CASCADE)
    crossSection = models.FloatField(null=True)
    ''' unit: square meters '''
    averagePerimeter = models.FloatField(null=True)
    ''' unit: meters '''
    length = models.FloatField(null=True)
    ''' length of the stations. Unit: meters '''
    #######################################################
    # CONSUMPTION                                         
    #######################################################
    auxiliariesConsumption = models.FloatField(null=True);
    ''' unit:  '''
    ventilationConsumption = models.FloatField(null=True);
    ''' unit:  '''


class MetroLineMetric(models.Model):
    ''' metric defined by chunk '''
    metroLine = models.ForeignKey(MetroLine, on_delete=models.CASCADE)
    metric = models.CharField(max_length=50)
    end = models.FloatField(null=True)
    start = models.FloatField(null=True)
    value = models.FloatField(null=True)
    direction = models.CharField(max_length=50)
    ''' example: s0-sN|sN-s0  '''

    
class OperationPeriod(models.Model):
    ''' operation period '''
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    start = models.TimeField()
    end = models.TimeField()
    #######################################################
    # AMBIENT CONDITION
    #######################################################
    temperature = models.FloatField()
    ''' unit:  '''
    humidity = models.FloatField()
    ''' unit:  '''
    co2Concentration = models.FloatField()
    ''' unit:  '''
    solarRadiation = models.FloatField()
    ''' unit:  '''
    sunElevationAngle = models.FloatField()
    ''' unit:  '''
