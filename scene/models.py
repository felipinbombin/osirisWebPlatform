# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models


class OverwriteStorage(FileSystemStorage):

    # This method is actually defined in Storage
    def get_available_name(self, name, max_length):
      if self.exists(name):
          os.remove(os.path.join(settings.MEDIA_ROOT, name))
      return name # simply returns the name passed

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
    currentStep = models.IntegerField('Paso actual', default=0)
    step1Template = models.FileField(upload_to='step1Template/', null=True, storage=OverwriteStorage())
    step1File = models.FileField(upload_to='step1File/', null=True, storage=OverwriteStorage())
    step3Template = models.FileField(upload_to='step3Template/', null=True, storage=OverwriteStorage())
    step3File = models.FileField(upload_to='step3File/', null=True, storage=OverwriteStorage())
    step5Template = models.FileField(upload_to='step5Template/', null=True, storage=OverwriteStorage())
    step5File = models.FileField(upload_to='step5File/', null=True, storage=OverwriteStorage())
    step6Template = models.FileField(upload_to='step5Template/', null=True, storage=OverwriteStorage())
    step6File = models.FileField(upload_to='step5File/', null=True, storage=OverwriteStorage())
    #######################################################
    # GLOBAL CONDITION
    #######################################################
    averageMassOfAPassanger = models.FloatField(null=True)
    ''' unit: Kg '''
    annualTemperatureAverage = models.FloatField(null=True)
    ''' unit: °C '''

    class Meta:
        verbose_name = 'escenario'
        verbose_name_plural = 'escenarios'
        unique_together = ('user', 'name',)

    def __str__(self):
        return self.name

class MetroLine(models.Model):
    ''' metro line '''
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    externalId = models.UUIDField(null=False, unique=True)
    ''' used to track record in wizard form, this way i know if is new record or previous '''
    isOld = models.BooleanField(default=False)
    ''' used when topological variables are updated '''
    name = models.CharField(max_length=100)
    #######################################################
    # CONSUMPTION                                         
    #######################################################
    usableEnergyContent = models.FloatField(null=True)
    ''' unit:  '''
    chargingEfficiency = models.FloatField(null=True)
    ''' unit:  '''
    dischargingEfficiency = models.FloatField(null=True)
    ''' unit:  '''
    peakPower = models.FloatField(null=True)
    ''' unit:  '''
    maximumEnergySavingPossiblePerHour = models.FloatField(null=True)
    ''' unit:  '''
    energySavingMode = models.FloatField(null=True)
    ''' unit:  '''
    powerLimitToFeed = models.FloatField(null=True)
    ''' unit:  '''

    class Meta:
        unique_together = ('scene', 'name',)

    def getDict(self):
        ''' dict '''
        dict = {'id': self.externalId, 'name': self.name, 'stations': [], 'depots': []}

        for station in self.metrostation_set.all().order_by('id'):
            dict['stations'].append(station.getDict())

        for depot in self.metrodepot_set.all().order_by('id'):
            dict['depots'].append(depot.getDict())

        return dict


class MetroStation(models.Model):
    ''' metro station'''
    metroLine = models.ForeignKey(MetroLine, on_delete=models.CASCADE)
    externalId = models.UUIDField(null=False, unique=True)
    ''' uses to track record in wizard form, this way i know if is new record or previous '''
    isOld = models.BooleanField(default=False)
    ''' used when topological variables are updated '''
    name = models.CharField(max_length=100)
    length = models.FloatField(null=True)
    ''' length of the stations. Unit: meters '''
    secondLevelAverageHeight = models.FloatField(null=True)
    ''' unit: meters '''
    secondLevelFloorSurface = models.FloatField(null=True)
    ''' unit: square meters '''
    platformSection = models.FloatField(null=True)
    ''' unit: square meters '''
    platformAveragePerimeter = models.FloatField(null=True)
    ''' unit: meters '''
    #######################################################
    # CONSUMPTION                                         
    #######################################################
    minAuxConsumption = models.FloatField(null=True)
    ''' unit:  '''
    maxAuxConsumption = models.FloatField(null=True)
    ''' unit:  '''
    minHVACConsumption = models.FloatField(null=True)
    ''' unit:  '''
    maxHVACConsumption = models.FloatField(null=True)
    ''' unit:  '''
    tau = models.FloatField(null=True)
    ''' unit:  '''

    class Meta:
        unique_together = ('metroLine', 'name',)

    def getDict(self):
        ''' dict structure '''
        dict = {'id': self.externalId, 'name': self.name, 'lineName': self.metroLine.name}

        return dict


class MetroDepot(models.Model):
    ''' train depot '''
    metroLine = models.ForeignKey(MetroLine, on_delete=models.CASCADE)
    externalId = models.UUIDField(null=False, unique=True)
    ''' uses to track record in wizard form, this way i know if is new record or previous '''
    isOld = models.BooleanField(default=False)
    ''' used when topological variables are updated '''
    name = models.CharField(max_length=100)
    #######################################################
    # CONSUMPTION                                         
    #######################################################
    auxConsumption = models.FloatField(null=True)
    ''' unit:  '''
    ventilationConsumption = models.FloatField(null=True)
    ''' unit:  '''
    dcConsumption = models.FloatField(null=True)
    ''' unit:  '''

    class Meta:
        unique_together = ('metroLine', 'name',)

    def getDict(self):
        ''' dict '''
        dict = {'id': self.externalId, 'name': self.name}

        return dict
   

class MetroConnection(models.Model):
    ''' connection between metro stations fo different metro lines '''
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    externalId = models.UUIDField(null=False, unique=True)
    ''' used to track record in wizard form, this way i know if is new record or previous '''
    isOld = models.BooleanField(default=False)
    ''' used when topological variables are updated '''
    name = models.CharField(max_length=100)
    stations = models.ManyToManyField(MetroStation, through='MetroConnectionStation')
    avgHeight = models.FloatField(null=True)
    ''' unit: meters '''
    avgSurface = models.FloatField(null=True)
    ''' unit: square meters '''
    #######################################################
    # CONSUMPTION                                         
    #######################################################
    consumption = models.FloatField(null=True)
    ''' unit: Watts '''

    class meta:
        unique_together = ('scene', 'name',)

    def getDict(self):
        ''' dict '''
        dict = {'id': self.externalId, 'name': self.name, 'avgHeight': self.avgHeight, 'avgSurface': self.avgSurface,
                'consumption': self.consumption, 'stations': []}

        for connectionStation in self.metroconnectionstation_set.all().order_by('id'):
            dict['stations'].append(connectionStation.getDict())

        return dict

class MetroConnectionStation(models.Model):
    ''' bridge between MetroStation and MetroConnection models '''
    metroStation = models.ForeignKey(MetroStation)
    metroConnection = models.ForeignKey(MetroConnection)
    isOld = models.BooleanField(default=False)
    ''' used when topological variables are updated '''
    externalId = models.UUIDField(null=False, unique=True)
    ''' used to track record in wizard form, this way i know if is new record or previous '''

    def getDict(self):
        ''' dict '''
        dict = {'id': self.externalId, 'station': self.metroStation.getDict()}

        return dict

class MetroTrack(models.Model):
    ''' connection between metro stations '''
    metroLine = models.ForeignKey(MetroLine, on_delete=models.CASCADE)
    isOld = models.BooleanField(default=False)
    ''' used when topological variables are updated '''
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
    auxiliariesConsumption = models.FloatField(null=True)
    ''' unit:  '''
    ventilationConsumption = models.FloatField(null=True)
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
    isOld = models.BooleanField(default=False)
    ''' used when topological variables are updated '''
    externalId = models.UUIDField(null=False, unique=True)
    ''' used to track record in wizard form, this way i know if is new record or previous '''

    name = models.CharField(max_length=100)
    start = models.TimeField()
    end = models.TimeField()
    #######################################################
    # AMBIENT CONDITION
    #######################################################
    temperature = models.FloatField()
    ''' unit: °C '''
    humidity = models.FloatField()
    ''' unit: % '''
    co2Concentration = models.FloatField()
    ''' unit: ppm '''
    solarRadiation = models.FloatField()
    ''' unit: W/m2 '''
    sunElevationAngle = models.FloatField()
    ''' unit: ° '''

    def getDict(self):
        ''' dict '''
        dict = {}
        dict['id'] = self.externalId
        dict['name'] = self.name
        dict['start'] = self.start
        dict['end'] = self.end
        dict['temperature'] = self.temperature
        dict['humidity'] = self.humidity
        dict['co2Concentration'] = self.co2Concentration
        dict['solarRadiation'] = self.solarRadiation
        dict['sunElevationAngle'] = self.sunElevationAngle

        return dict


class SystemicParams(models.Model):
    ''' global systemic params '''
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    #######################################################
    # TRAIN FORCES
    #######################################################
    mass = models.FloatField(null=True)
    inercialMass = models.FloatField(null=True)
    maxAccelerationAllowed = models.FloatField(null=True)
    maxStartingForceAllowed = models.FloatField(null=True)
    maxBrakingForceAllowed = models.FloatField(null=True)
    speedOfMotorRegimeChange = models.FloatField(null=True)
    maxPower = models.FloatField(null=True)
    maxSpeedAllowed = models.FloatField(null=True)

    davisParameterA = models.FloatField(null=True)
    davisParameterB = models.FloatField(null=True)
    davisParameterC = models.FloatField(null=True)
    davisParameterD = models.FloatField(null=True)
    davisParameterE = models.FloatField(null=True)

    #######################################################
    # TRAIN TRACTION
    #######################################################
    tractionSystemEfficiency = models.FloatField(null=True)
    brakingSystemEfficiency = models.FloatField(null=True)
    electricalBrakeTreshold = models.FloatField(null=True)
    electroMechanicalBrakeThreshold = models.FloatField(null=True)

    #######################################################
    # TRAIN STRUCTURE
    #######################################################
    length = models.FloatField(null=True)
    numberOfCars = models.FloatField(null=True)
    carWidth = models.FloatField(null=True)
    carHeight = models.FloatField(null=True)
    vehicleWallThickness = models.FloatField(null=True)
    heatConductivityOfTheVehicleWall = models.FloatField(null=True)
    cabinVolumeFactor = models.FloatField(null=True)
    trainPassengerCapacity = models.FloatField(null=True)

    point1Tin = models.FloatField(null=True)
    point2Tin = models.FloatField(null=True)
    point3Tin = models.FloatField(null=True)
    point4Tin = models.FloatField(null=True)
    point5Tin = models.FloatField(null=True)
    point1Tout = models.FloatField(null=True)
    point2Tout = models.FloatField(null=True)
    point3Tout = models.FloatField(null=True)
    point4Tout = models.FloatField(null=True)
    point5Tout = models.FloatField(null=True)

    hrsExtraPower = models.FloatField(null=True)
    onBoardEnergyStorageSystem = models.FloatField(null=True)
    storageCapacityWeighting = models.FloatField(null=True)

    #######################################################
    # TRAIN CMM TRACTION MODEL
    #######################################################
    obessChargeEfficiency = models.FloatField(null=True)
    obessDischargeEfficiency = models.FloatField(null=True)
    obessUsableEnergyContent = models.FloatField(null=True)
    maxDischargePower = models.FloatField(null=True)
    maxEnergySavingPossiblePerHour = models.FloatField(null=True)
    powerLimitToFeed = models.FloatField(null=True)

    #######################################################
    # TRAIN ENERGY
    #######################################################
    hvacConsumption = models.FloatField(null=True)
    auxiliariesConsumption = models.FloatField(null=True)
    trainsTerminalResistance = models.FloatField(null=True)
    voltageDCTrainsTerminals = models.FloatField(null=True)

    def getDict(self):
        ''' dict '''
        dict = {}

        # TRAIN FORCES
        dict['mass'] = self.mass
        dict['inercialMass'] = self.inercialMass
        dict['maxAccelerationAllowed'] = self.maxAccelerationAllowed
        dict['maxStartingForceAllowed'] = self.maxStartingForceAllowed
        dict['maxBrakingForceAllowed'] = self.maxBrakingForceAllowed
        dict['speedOfMotorRegimeChange'] = self.speedOfMotorRegimeChange
        dict['maxPower'] = self.maxPower
        dict['maxSpeedAllowed'] = self.maxSpeedAllowed

        dict['davisParameterA'] = self.davisParameterA
        dict['davisParameterB'] = self.davisParameterB
        dict['davisParameterC'] = self.davisParameterC
        dict['davisParameterD'] = self.davisParameterD
        dict['davisParameterE'] = self.davisParameterE

        # TRAIN TRACTION
        dict['tractionSystemEfficiency'] = self.tractionSystemEfficiency
        dict['brakingSystemEfficiency'] = self.brakingSystemEfficiency
        dict['electricalBrakeTreshold'] = self.electricalBrakeTreshold
        dict['electroMechanicalBrakeThreshold'] = self.electroMechanicalBrakeThreshold

        # TRAIN STRUCTURE
        dict['length'] = self.length
        dict['numberOfCars'] = self.numberOfCars
        dict['carWidth'] = self.carWidth
        dict['carHeight'] = self.carHeight
        dict['vehicleWallThickness'] = self.vehicleWallThickness
        dict['heatConductivityOfTheVehicleWall'] = self.heatConductivityOfTheVehicleWall
        dict['cabinVolumeFactor'] = self.cabinVolumeFactor
        dict['trainPassengerCapacity'] = self.trainPassengerCapacity

        dict['point1Tin'] = self.point1Tin
        dict['point2Tin'] = self.point2Tin
        dict['point3Tin'] = self.point3Tin
        dict['point4Tin'] = self.point4Tin
        dict['point5Tin'] = self.point5Tin
        dict['point1Tout'] = self.point1Tout
        dict['point2Tout'] = self.point2Tout
        dict['point3Tout'] = self.point3Tout
        dict['point4Tout'] = self.point4Tout
        dict['point5Tout'] = self.point5Tout

        dict['hrsExtraPower'] = self.hrsExtraPower
        dict['onBoardEnergyStorageSystem'] = self.onBoardEnergyStorageSystem
        dict['storageCapacityWeighting'] = self.storageCapacityWeighting

        # TRAIN CMM TRACTION
        dict['obessChargeEfficiency'] = self.obessChargeEfficiency
        dict['obessDischargeEfficiency'] = self.obessDischargeEfficiency
        dict['obessUsableEnergyContent'] = self.obessUsableEnergyContent
        dict['maxDischargePower'] = self.maxDischargePower
        dict['maxEnergySavingPossiblePerHour'] = self.maxEnergySavingPossiblePerHour
        dict['powerLimitToFeed'] = self.powerLimitToFeed

        # TRAIN ENERGY
        dict['hvacConsumption'] = self.hvacConsumption
        dict['auxiliariesConsumption'] = self.auxiliariesConsumption
        dict['trainsTerminalResistance'] = self.trainsTerminalResistance
        dict['voltageDCTrainsTerminals'] = self.voltageDCTrainsTerminals

        return dict
