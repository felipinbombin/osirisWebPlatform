# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Scene(models.Model):
    ''' group of parameter to run models '''
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
    #######################################################
    # GLOBAL CONDITION
    #######################################################
    averageMassOfAPassanger = models.FloatField(null=True)
    annualTemperatureAverage = models.FloatField(null=True)

    def metroLineQuantity(self):
        return self.metroline_set.count()
    metroLineQuantity.short_description = 'Cantidad de líneas'
    metroLineQuantity =property(metroLineQuantity)

    class Meta:
        verbose_name = 'escenario'
        verbose_name_plural = 'escenarios'

class MetroLine(models.Model):
    ''' metro line '''
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
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
 

class MetroStation(models.Model):
    ''' metro station'''
    metroLine = models.ForeignKey(MetroLine, on_delete=models.CASCADE)
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

class MetroConnection(models.Model):
    ''' connection between metro stations fo different metro lines '''
    name = models.CharField(max_length=100)
    firstStation = models.ForeignKey(MetroStation, 
        related_name= 'firststation', 
        on_delete=models.CASCADE)
    secondStation = models.ForeignKey(MetroStation, 
        related_name= 'secondstation',
        on_delete=models.CASCADE)
    averageHeight = models.FloatField(null=True);
    ''' unit: meters '''
    surface = models.FloatField(null=True);
    ''' unit: square meters '''
    #######################################################
    # CONSUMPTION                                         
    #######################################################
    consumption = models.FloatField(null=True);
    ''' unit:  '''


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
