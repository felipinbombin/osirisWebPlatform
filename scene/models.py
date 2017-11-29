# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models

import os
import uuid


class OverwriteStorage(FileSystemStorage):
    # This method is actually defined in Storage
    def get_available_name(self, name, max_length):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name  # simply returns the name passed


class Scene(models.Model):
    """ group of parameter to run models """
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
    timeStampStep1File = models.DateTimeField(null=True)
    step3Template = models.FileField(upload_to='step3Template/', null=True, storage=OverwriteStorage())
    step3File = models.FileField(upload_to='step3File/', null=True, storage=OverwriteStorage())
    timeStampStep3File = models.DateTimeField(null=True)
    step5Template = models.FileField(upload_to='step5Template/', null=True, storage=OverwriteStorage())
    step5File = models.FileField(upload_to='step5File/', null=True, storage=OverwriteStorage())
    timeStampStep5File = models.DateTimeField(null=True)
    step6Template = models.FileField(upload_to='step6Template/', null=True, storage=OverwriteStorage())
    step6File = models.FileField(upload_to='step6File/', null=True, storage=OverwriteStorage())
    timeStampStep6File = models.DateTimeField(null=True)
    #######################################################
    # GLOBAL CONDITION
    #######################################################
    averageMassOfAPassanger = models.FloatField(null=True)
    """ unit: Kg """
    annualTemperatureAverage = models.FloatField(null=True)
    """ unit: °C """

    class Meta:
        verbose_name = 'escenario'
        verbose_name_plural = 'escenarios'
        unique_together = ('user', 'name',)

    def __str__(self):
        return self.name


class MetroLineMetric(models.Model):
    """ metric defined by chunk """
    metroLine = models.ForeignKey("MetroLine", on_delete=models.CASCADE)
    # metric
    SLOPE = 'S'
    CURVE_RADIUS = 'CR'
    SPEED_LIMIT = 'SL'
    GROUND = 'G'
    METRIC_CHOICES = (
        (SLOPE, ''),
        (CURVE_RADIUS, ''),
        (SPEED_LIMIT, ''),
        (GROUND, '')
    )
    metric = models.CharField(max_length=50, choices=METRIC_CHOICES)
    end = models.FloatField(null=True)
    start = models.FloatField(null=True)
    value = models.FloatField(null=True)
    GOING = 'g'
    REVERSE = 'r'
    DIRECTION_CHOICES = (
        (GOING, ''),
        (REVERSE, '')
    )
    direction = models.CharField(max_length=50, null=True, choices=DIRECTION_CHOICES)
    """ example: s0-sN|sN-s0  """


class MetroLine(models.Model):
    """ metro line """
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    externalId = models.UUIDField(null=False, unique=True)
    """ used to track record in wizard form, this way i know if is new record or previous """
    isOld = models.BooleanField(default=False)
    """ used when topological variables are updated """
    name = models.CharField(max_length=100)
    #######################################################
    # CONSUMPTION                                         
    #######################################################
    usableEnergyContent = models.FloatField(null=True)
    """ unit: W """
    chargingEfficiency = models.FloatField(null=True)
    """ unit: % """
    dischargingEfficiency = models.FloatField(null=True)
    """ unit: % """
    peakPower = models.FloatField(null=True)
    """ unit: W """
    maximumEnergySavingPossiblePerHour = models.FloatField(null=True)
    """ unit: W """
    energySavingMode = models.FloatField(null=True)
    """ unit: Boolean """
    powerLimitToFeed = models.FloatField(null=True)
    """ unit: W """

    class Meta:
        unique_together = ('scene', 'name',)

    def get_direction_name(self, direction=MetroLineMetric.GOING):
        """ return line name based on direction param """
        metro_stations = list(self.metrostation_set.all().order_by("id"))
        if direction == MetroLineMetric.GOING:
            return "{}-{}".format(metro_stations[0].name, metro_stations[-1].name)
        else:
            # is reverse
            return "{}-{}".format(metro_stations[-1].name, metro_stations[0].name)

    def get_dict(self):
        """ dict """
        line_dict = {
            'id': self.externalId,
            'name': self.name,
            'stations': [],
            'depots': [],
            'tracks': [],
             "directionNames": {
                 MetroLineMetric.GOING: self.get_direction_name(),
                 MetroLineMetric.REVERSE: self.get_direction_name(MetroLineMetric.REVERSE)
            }
        }

        for station in self.metrostation_set.all().order_by('id'):
            line_dict['stations'].append(station.get_dict())

        for depot in self.metrodepot_set.all().order_by('id'):
            line_dict['depots'].append(depot.get_dict())

        for track in self.metrotrack_set.all().order_by('id'):
            line_dict['tracks'].append(track.get_dict())

        return line_dict


class MetroStation(models.Model):
    """ metro station"""
    metroLine = models.ForeignKey(MetroLine, on_delete=models.CASCADE)
    externalId = models.UUIDField(null=False, unique=True)
    """ uses to track record in wizard form, this way i know if is new record or previous """
    isOld = models.BooleanField(default=False)
    """ used when topological variables are updated """
    name = models.CharField(max_length=100)
    length = models.FloatField(null=True)
    """ length of the stations. Unit: meters """
    secondLevelAverageHeight = models.FloatField(null=True)
    """ unit: meters """
    secondLevelFloorSurface = models.FloatField(null=True)
    """ unit: square meters """
    platformSection = models.FloatField(null=True)
    """ unit: square meters """
    platformAveragePerimeter = models.FloatField(null=True)
    """ unit: meters """
    #######################################################
    # CONSUMPTION                                         
    #######################################################
    minAuxConsumption = models.FloatField(null=True)
    """ unit: W """
    maxAuxConsumption = models.FloatField(null=True)
    """ unit: W """
    minHVACConsumption = models.FloatField(null=True)
    """ unit: W """
    maxHVACConsumption = models.FloatField(null=True)
    """ unit: W """
    tau = models.FloatField(null=True)
    """ unit: none """

    class Meta:
        unique_together = ('metroLine', 'name',)

    def get_dict(self):
        """ dict structure """
        station_dict = {'id': self.externalId, 'name': self.name, 'lineName': self.metroLine.name}

        return station_dict


class MetroDepot(models.Model):
    """ train depot """
    metroLine = models.ForeignKey(MetroLine, on_delete=models.CASCADE)
    externalId = models.UUIDField(null=False, unique=True)
    """ uses to track record in wizard form, this way i know if is new record or previous """
    isOld = models.BooleanField(default=False)
    """ used when topological variables are updated """
    name = models.CharField(max_length=100)
    #######################################################
    # CONSUMPTION                                         
    #######################################################
    auxConsumption = models.FloatField(null=True)
    """ unit: W """
    ventilationConsumption = models.FloatField(null=True)
    """ unit: W """
    dcConsumption = models.FloatField(null=True)
    """ unit: W """

    class Meta:
        unique_together = ('metroLine', 'name',)

    def get_dict(self):
        """ dict """
        depot_dict = {'id': self.externalId, 'name': self.name}

        return depot_dict


class MetroConnection(models.Model):
    """ connection between metro stations fo different metro lines """
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    externalId = models.UUIDField(null=False, unique=True)
    """ used to track record in wizard form, this way i know if is new record or previous """
    isOld = models.BooleanField(default=False)
    """ used when topological variables are updated """
    name = models.CharField(max_length=100)
    stations = models.ManyToManyField(MetroStation, through='MetroConnectionStation')
    avgHeight = models.FloatField(null=True)
    """ unit: meters """
    avgSurface = models.FloatField(null=True)
    """ unit: square meters """
    #######################################################
    # CONSUMPTION                                         
    #######################################################
    consumption = models.FloatField(null=True)
    """ unit: Watts """

    class Meta:
        unique_together = ('scene', 'name',)

    def get_dict(self):
        """ dict """
        conn_dict = {'id': self.externalId, 'name': self.name, 'avgHeight': self.avgHeight,
                     'avgSurface': self.avgSurface, 'consumption': self.consumption, 'stations': []}

        for connectionStation in self.metroconnectionstation_set.all().order_by('id'):
            conn_dict['stations'].append(connectionStation.get_dict())

        return conn_dict


class MetroConnectionStation(models.Model):
    """ bridge between MetroStation and MetroConnection models """
    metroStation = models.ForeignKey(MetroStation)
    metroConnection = models.ForeignKey(MetroConnection)
    isOld = models.BooleanField(default=False)
    """ used when topological variables are updated """
    externalId = models.UUIDField(null=False, unique=True)
    """ used to track record in wizard form, this way i know if is new record or previous """

    def get_dict(self):
        """ dict """
        conn_dict = {'id': self.externalId, 'station': self.metroStation.get_dict()}

        return conn_dict


class MetroTrack(models.Model):
    """ connection between metro stations """
    metroLine = models.ForeignKey(MetroLine, on_delete=models.CASCADE)
    isOld = models.BooleanField(default=False)
    """ used when topological variables are updated """
    externalId = models.UUIDField(null=False, unique=True, default=uuid.uuid4)
    """ used to track record in wizard form, this way i know if is new record or previous """
    name = models.CharField(max_length=100)
    startStation = models.ForeignKey(MetroStation,
                                     related_name='startstation',
                                     on_delete=models.CASCADE)
    endStation = models.ForeignKey(MetroStation,
                                   related_name='endstation',
                                   on_delete=models.CASCADE)
    crossSection = models.FloatField(null=True)
    """ unit: square meters """
    averagePerimeter = models.FloatField(null=True)
    """ unit: meters """
    length = models.FloatField(null=True)
    """ length of the stations. Unit: meters """
    #######################################################
    # CONSUMPTION
    #######################################################
    auxiliariesConsumption = models.FloatField(null=True)
    """ unit: W """
    ventilationConsumption = models.FloatField(null=True)
    """ unit: W """

    def get_name(self, direction=MetroLineMetric.GOING):
        """ return track name based on direction param """
        if direction == MetroLineMetric.GOING:
            return "{}-{}".format(self.startStation.name, self.endStation.name)
        else:
            # is reverse
            return "{}-{}".format(self.endStation.name, self.startStation.name)

    def get_dict(self):
        """  """
        track_dict = {
            "name": self.name,
            "startStation": self.startStation.name,
            "endStation": self.endStation.name,
            "id": self.externalId
        }
        return track_dict


class OperationPeriod(models.Model):
    """ operation period """
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    isOld = models.BooleanField(default=False)
    """ used when topological variables are updated """
    externalId = models.UUIDField(null=False, unique=True)
    """ used to track record in wizard form, this way i know if is new record or previous """

    name = models.CharField(max_length=100)
    start = models.TimeField()
    end = models.TimeField()
    #######################################################
    # AMBIENT CONDITION
    #######################################################
    temperature = models.FloatField()
    """ unit: °C """
    humidity = models.FloatField()
    """ unit: % """
    co2Concentration = models.FloatField()
    """ unit: ppm """
    solarRadiation = models.FloatField()
    """ unit: W/m2 """
    sunElevationAngle = models.FloatField()
    """ unit: ° """

    def get_dict(self):
        """ dict """
        op_dict = {}
        op_dict['id'] = self.externalId
        op_dict['name'] = self.name
        op_dict['start'] = self.start
        op_dict['end'] = self.end
        op_dict['temperature'] = self.temperature
        op_dict['humidity'] = self.humidity
        op_dict['co2Concentration'] = self.co2Concentration
        op_dict['solarRadiation'] = self.solarRadiation
        op_dict['sunElevationAngle'] = self.sunElevationAngle

        return op_dict


class OperationPeriodForMetroLine(models.Model):
    """ bridge between OperationPeriod and MetroLine models """
    operationPeriod = models.ForeignKey(OperationPeriod)
    metroLine = models.ForeignKey(MetroLine)
    FREQUENCY = 'frequency'
    RECEPTIVITY = 'receptivity'
    PERC_DC_DISTRIBUTION_LOSSES = 'percentageDCDistributionLosses'
    PERC_AC_SUBSTATION_LOSSES_FEED_ENTIRE_SYSTEM = 'PercentageACSubstationLossesFeedEntireSystem'
    PERC_AC_SUBSTATION_LOSSES_FEED_AC_ELEMENTS = 'PercentageACSubstationLossesFeedACElements)'
    PERC_DC_SUBSTATION_LOSSES = 'PercentageDCSubstationLosses'
    METRIC_CHOICES = (
        (FREQUENCY, 'trains/hour'),
        (RECEPTIVITY, '%'),
        (PERC_DC_DISTRIBUTION_LOSSES, '%'),
        (PERC_AC_SUBSTATION_LOSSES_FEED_ENTIRE_SYSTEM, ''),
        (PERC_AC_SUBSTATION_LOSSES_FEED_ENTIRE_SYSTEM, ''),
        (PERC_DC_SUBSTATION_LOSSES, ''),
    )
    metric = models.CharField(max_length=50, null=True,
                              choices=METRIC_CHOICES)
    value = models.FloatField(null=True)
    """ unit: depends of metric """
    direction = models.CharField(max_length=50, null=True,
                                 choices=MetroLineMetric.DIRECTION_CHOICES)

    def get_dict(self):
        """ dict """
        op_dict = {'metric': self.metric, 'value': self.value, 'direction': self.direction}

        return op_dict


class OperationPeriodForMetroStation(models.Model):
    """ bridge between OperationPeriod and MetroStation models """
    operationPeriod = models.ForeignKey(OperationPeriod)
    metroStation = models.ForeignKey(MetroStation)
    VENTILATION_FLOW = 'ventilationFlow'
    DWELL_TIME = 'dwellTime'
    PASSENGERS_IN_STATION = 'PassengersInStations'
    METRIC_CHOICES = (
        (VENTILATION_FLOW, 'm^3/s'),
        (DWELL_TIME, 'seg'),
        (PASSENGERS_IN_STATION, '')
    )
    metric = models.CharField(max_length=50, null=True, choices=METRIC_CHOICES)
    value = models.FloatField(null=True)
    """ unit: depends of metric """
    direction = models.CharField(max_length=50, null=True,
                                 choices=MetroLineMetric.DIRECTION_CHOICES)

    def get_dict(self):
        """ dict """
        op_dict = {'metric': self.metric, 'value': self.value, 'direction': self.direction}

        return op_dict


class OperationPeriodForMetroTrack(models.Model):
    """ bridge between OperationPeriod and MetroTrack models """
    operationPeriod = models.ForeignKey(OperationPeriod)
    metroTrack = models.ForeignKey(MetroTrack)
    PASSENGERS_TRAVELING_BETWEEN_STATION = 'PassengersTravelingBetweenStations'
    MAX_TRAVEL_TIME_BETWEEN_STATION = 'MaxTravelTimeBetweenStations'
    METRIC_CHOICES = (
        (PASSENGERS_TRAVELING_BETWEEN_STATION, ''),
        (MAX_TRAVEL_TIME_BETWEEN_STATION, 'seg')
    )
    metric = models.CharField(max_length=50, null=True, choices=METRIC_CHOICES)
    value = models.FloatField(null=True)
    """ unit: depends of metric """
    direction = models.CharField(max_length=50, null=True,
                                 choices=MetroLineMetric.DIRECTION_CHOICES)

    def get_dict(self):
        """ dict """
        op_dict = {'metric': self.metric, 'value': self.value, 'direction': self.direction}

        return op_dict


class SystemicParams(models.Model):
    """ global systemic params """
    """
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    group = models.CharField(max_length=30, null=False)
    order = models.IntegerFi(null=False)
    modelName = models.CharField(max_length=50, null=False)
    value = models.FloatField(null=True)
    unit = models.FloatField(max_length=10, null=False)
    label = models.CharField(max_length=100, null=False)
    """

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

    def get_dict(self):
        """ dict """
        sys_dict = {}

        # TRAIN FORCES
        sys_dict['mass'] = self.mass
        sys_dict['inercialMass'] = self.inercialMass
        sys_dict['maxAccelerationAllowed'] = self.maxAccelerationAllowed
        sys_dict['maxStartingForceAllowed'] = self.maxStartingForceAllowed
        sys_dict['maxBrakingForceAllowed'] = self.maxBrakingForceAllowed
        sys_dict['speedOfMotorRegimeChange'] = self.speedOfMotorRegimeChange
        sys_dict['maxPower'] = self.maxPower
        sys_dict['maxSpeedAllowed'] = self.maxSpeedAllowed

        sys_dict['davisParameterA'] = self.davisParameterA
        sys_dict['davisParameterB'] = self.davisParameterB
        sys_dict['davisParameterC'] = self.davisParameterC
        sys_dict['davisParameterD'] = self.davisParameterD
        sys_dict['davisParameterE'] = self.davisParameterE

        # TRAIN TRACTION
        sys_dict['tractionSystemEfficiency'] = self.tractionSystemEfficiency
        sys_dict['brakingSystemEfficiency'] = self.brakingSystemEfficiency
        sys_dict['electricalBrakeTreshold'] = self.electricalBrakeTreshold
        sys_dict['electroMechanicalBrakeThreshold'] = self.electroMechanicalBrakeThreshold

        # TRAIN STRUCTURE
        sys_dict['length'] = self.length
        sys_dict['numberOfCars'] = self.numberOfCars
        sys_dict['carWidth'] = self.carWidth
        sys_dict['carHeight'] = self.carHeight
        sys_dict['vehicleWallThickness'] = self.vehicleWallThickness
        sys_dict['heatConductivityOfTheVehicleWall'] = self.heatConductivityOfTheVehicleWall
        sys_dict['cabinVolumeFactor'] = self.cabinVolumeFactor
        sys_dict['trainPassengerCapacity'] = self.trainPassengerCapacity

        sys_dict['point1Tin'] = self.point1Tin
        sys_dict['point2Tin'] = self.point2Tin
        sys_dict['point3Tin'] = self.point3Tin
        sys_dict['point4Tin'] = self.point4Tin
        sys_dict['point5Tin'] = self.point5Tin
        sys_dict['point1Tout'] = self.point1Tout
        sys_dict['point2Tout'] = self.point2Tout
        sys_dict['point3Tout'] = self.point3Tout
        sys_dict['point4Tout'] = self.point4Tout
        sys_dict['point5Tout'] = self.point5Tout

        sys_dict['hrsExtraPower'] = self.hrsExtraPower
        sys_dict['onBoardEnergyStorageSystem'] = self.onBoardEnergyStorageSystem
        sys_dict['storageCapacityWeighting'] = self.storageCapacityWeighting

        # TRAIN CMM TRACTION
        sys_dict['obessChargeEfficiency'] = self.obessChargeEfficiency
        sys_dict['obessDischargeEfficiency'] = self.obessDischargeEfficiency
        sys_dict['obessUsableEnergyContent'] = self.obessUsableEnergyContent
        sys_dict['maxDischargePower'] = self.maxDischargePower
        sys_dict['maxEnergySavingPossiblePerHour'] = self.maxEnergySavingPossiblePerHour
        sys_dict['powerLimitToFeed'] = self.powerLimitToFeed

        # TRAIN ENERGY
        sys_dict['hvacConsumption'] = self.hvacConsumption
        sys_dict['auxiliariesConsumption'] = self.auxiliariesConsumption
        sys_dict['trainsTerminalResistance'] = self.trainsTerminalResistance
        sys_dict['voltageDCTrainsTerminals'] = self.voltageDCTrainsTerminals

        return sys_dict
