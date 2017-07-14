# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from abc import ABCMeta, abstractmethod
from StringIO import StringIO
from django.core.files.base import ContentFile

import ExcelWriter
from ..models import MetroTrack, MetroLineMetric, OperationPeriodForMetroLine, OperationPeriodForMetroStation, OperationPeriodForMetroTrack

import xlrd


class ExcelReader(object):
    ''' to manage excel files '''
    __metaclass__ = ABCMeta

    def __init__(self, scene):

        scene.refresh_from_db()
        self.scene = scene

    @abstractmethod
    def processFile(self, inMemoryFile):
        pass


class Step1ExcelReader(ExcelReader):
    ''' read excel file uploaded on step 2 '''

    def __init__(self, scene):
        super(self.__class__, self).__init__(scene)

    def processFile(self, inMemoryFile):
        ''' read excel file and retrieve data '''
        workbook = xlrd.open_workbook(file_contents=inMemoryFile.read())

        # all metro track records are old
        MetroTrack.objects.filter(metroLine__scene=self.scene).update(isOld=True)

        for line in self.scene.metroline_set.all().order_by('id'):
            stations = line.metrostation_set.all().order_by('id')

            worksheet = workbook.sheet_by_name(line.name)

            firstRow = 3
            currentRow = firstRow
            for index, station in enumerate(stations):
                length = worksheet.cell_value(currentRow, 1)
                platformSection = worksheet.cell_value(currentRow, 2)
                platformAveragePerimeter = worksheet.cell_value(currentRow, 3)
                secondLevelAverageHeight = worksheet.cell_value(currentRow, 4)
                secondLevelFloorSurface = worksheet.cell_value(currentRow, 5)

                station.length = length
                station.platformSection = platformSection
                station.platformAveragePerimeter = platformAveragePerimeter
                station.secondLevelAverageHeight = secondLevelAverageHeight
                station.secondLevelFloorSurface = secondLevelFloorSurface
                station.save()

                # create tracks
                if index < len(stations)-1:
                    nextStation = stations[index+1]
                    name = station.name + "-" + nextStation.name
                    metroTrack, created = MetroTrack.objects.get_or_create(metroLine=line, name=name,
                                                                           defaults={"startStation":station,
                                                                                     "endStation":nextStation})
                    if not created:
                        metroTrack.startStation = station
                        metroTrack.endStation = nextStation
                    metroTrack.length = worksheet.cell_value(currentRow, 8)
                    metroTrack.crossSection = worksheet.cell_value(currentRow, 9)
                    metroTrack.averagePerimeter = worksheet.cell_value(currentRow, 10)
                    metroTrack.isOld = False
                    metroTrack.save()

                currentRow += 1

            firstRow = 3 + len(stations) + ExcelWriter.SEPARATION_HEIGHT + 3

            # delete previous metrics
            MetroLineMetric.objects.filter(metroLine=line).delete()
            metrics = [
                MetroLineMetric.SLOPE,
                MetroLineMetric.CURVE_RADIUS,
                MetroLineMetric.SPEED_LIMIT,
                MetroLineMetric.GROUND
            ]
            row = firstRow
            previousCType = None
            currentArray = 0
            while row < worksheet.nrows:
                cType = worksheet.cell(row, 0).ctype
                # dict of ctype
                # 0: empty string u''
                # 1: a Unicode string
                # 2: float
                if cType == 0 and previousCType is not None:
                    previousCType = cType
                elif cType == 1 and previousCType != 1:
                    currentArray += 1
                    previousCType = cType
                elif cType == 2:
                    previousCType = None
                    if currentArray == 3:
                        MetroLineMetric.objects.create(metroLine=line,
                                                       metric=metrics[currentArray],
                                                       start=worksheet.cell_value(row, 0),
                                                       end=worksheet.cell_value(row, 1),
                                                       value=worksheet.cell_value(row, 2),
                                                       direction=None)
                    else:
                        MetroLineMetric.objects.create(metroLine=line,
                                                       metric=metrics[currentArray],
                                                       start=worksheet.cell_value(row, 0),
                                                       end=worksheet.cell_value(row, 1),
                                                       value=worksheet.cell_value(row, 2),
                                                       direction=MetroLineMetric.GOING)
                        MetroLineMetric.objects.create(metroLine=line,
                                                       metric=metrics[currentArray],
                                                       start=worksheet.cell_value(row, 3),
                                                       end=worksheet.cell_value(row, 4),
                                                       value=worksheet.cell_value(row, 5),
                                                       direction=MetroLineMetric.REVERSE)
                row += 1

        MetroTrack.objects.filter(metroLine__scene=self.scene, isOld=True).delete()

class Step3ExcelReader(ExcelReader):
    ''' read excel file uploaded in step 3 '''

    def __init__(self, scene):
        super(self.__class__, self).__init__(scene)

    def processFile(self, inMemoryFile):
        ''' read excel file and retrieve data '''
        workbook = xlrd.open_workbook(file_contents=inMemoryFile.read())

        for line in self.scene.metroline_set.all().order_by('id'):
            stations = line.metrostation_set.all().order_by('id')
            depots = line.metrodepot_set.all().order_by('id')

            worksheet = workbook.sheet_by_name(line.name)

            firstRow = 3
            currentRow = firstRow
            for index, station in enumerate(stations):
                station.minAuxConsumption = worksheet.cell_value(currentRow, 1)
                station.maxAuxConsumption = worksheet.cell_value(currentRow, 2)
                station.minHVACConsumption = worksheet.cell_value(currentRow, 3)
                station.maxHVACConsumption = worksheet.cell_value(currentRow, 4)
                station.tau = worksheet.cell_value(currentRow, 5)
                station.save()

                # create tracks
                if index < len(stations)-1:
                    nextStation = stations[index+1]
                    name = station.name + "-" + nextStation.name
                    metroTrack = MetroTrack.objects.get(metroLine=line, name=name)
                    metroTrack.auxiliariesConsumption = worksheet.cell_value(currentRow, 8)
                    metroTrack.ventilationConsumption = worksheet.cell_value(currentRow, 9)
                    metroTrack.save()

                currentRow += 1

            currentRow = firstRow
            for depot in depots:
                depot.auxConsumption = worksheet.cell_value(currentRow, 12) 
                depot.ventilationConsumption = worksheet.cell_value(currentRow, 13)
                depot.dcConsumption = worksheet.cell_value(currentRow, 14)
                depot.save()

            currentRow = 3 + len(stations) + ExcelWriter.SEPARATION_HEIGHT + 1

            line.usableEnergyContent = worksheet.cell_value(currentRow, 1)
            currentRow += 1
            line.chargingEfficiency = worksheet.cell_value(currentRow, 1)
            currentRow += 1
            line.dischargingEfficiency = worksheet.cell_value(currentRow, 1)
            currentRow += 1
            line.peakPower = worksheet.cell_value(currentRow, 1)
            currentRow += 1
            line.maximumEnergySavingPossiblePerHour = worksheet.cell_value(currentRow, 1)
            currentRow += 1
            line.energySavingMode = worksheet.cell_value(currentRow, 1)
            currentRow += 1
            line.powerLimitToFeed = worksheet.cell_value(currentRow, 1)
            line.save()


class Step5ExcelReader(ExcelReader):
    ''' create excel file for step 5 '''

    def __init__(self, scene):
        super(self.__class__, self).__init__(scene)

    def processFile(self, inMemoryFile):
        ''' read excel file and retrieve data '''
        workbook = xlrd.open_workbook(file_contents=inMemoryFile.read())

        # delete previous data of the line
        OperationPeriodForMetroLine.objects.filter(metroLine__scene=self.scene).delete()
        OperationPeriodForMetroStation.objects.filter(
            metroStation__metroLine__scene=self.scene).delete()
        OperationPeriodForMetroTrack.objects.filter(
            metroTrack__metroLine__scene=self.scene).delete()

        periods = self.scene.operationperiod_set.all().order_by('id')

        for line in self.scene.metroline_set.all().order_by('id'):
            stations = line.metrostation_set.all().order_by('id')
            tracks = line.metrotrack_set.all().order_by('id')

            worksheet = workbook.sheet_by_name(line.name)

            firstRow = 3
            currentRow = firstRow
            currentColumn = 1

            for station in stations:
                for period in periods:
                    OperationPeriodForMetroStation.objects.create(
                        operationPeriod=period,
                        metroStation=station,
                        metric=OperationPeriodForMetroStation.PASSENGERS_IN_STATION,
                        value=worksheet.cell_value(currentRow, currentColumn),
                        direction=MetroLineMetric.GOING)
                    OperationPeriodForMetroStation.objects.create(
                        operationPeriod=period,
                        metroStation=station,
                        metric=OperationPeriodForMetroStation.PASSENGERS_IN_STATION,
                        value=worksheet.cell_value(currentRow, currentColumn + 3),
                        direction=MetroLineMetric.REVERSE)
                    currentColumn += 1
                currentRow += 1
                currentColumn = 1

            currentRow += ExcelWriter.SEPARATION_HEIGHT + 3
            currentColumn = 1

            for track in tracks:
                for period in periods:
                    OperationPeriodForMetroTrack.objects.create(
                        operationPeriod=period,
                        metroTrack=track,
                        metric=OperationPeriodForMetroTrack.PASSENGERS_TRAVELING_BETWEEN_STATION,
                        value=worksheet.cell_value(currentRow, currentColumn),
                        direction=MetroLineMetric.GOING)
                    OperationPeriodForMetroTrack.objects.create(
                        operationPeriod=period,
                        metroTrack=track,
                        metric=OperationPeriodForMetroTrack.PASSENGERS_TRAVELING_BETWEEN_STATION,
                        value=worksheet.cell_value(currentRow, currentColumn + 3),
                        direction=MetroLineMetric.REVERSE)
                    currentColumn += 1
                currentRow += 1
                currentColumn = 1

            currentRow += ExcelWriter.SEPARATION_HEIGHT + 3
            currentColumn = 1

            for track in tracks:
                for period in periods:
                    OperationPeriodForMetroTrack.objects.create(
                        operationPeriod=period,
                        metroTrack=track,
                        metric=OperationPeriodForMetroTrack.MAX_TRAVEL_TIME_BETWEEN_STATION,
                        value=worksheet.cell_value(currentRow, currentColumn),
                        direction=MetroLineMetric.GOING)
                    OperationPeriodForMetroTrack.objects.create(
                        operationPeriod=period,
                        metroTrack=track,
                        metric=OperationPeriodForMetroTrack.MAX_TRAVEL_TIME_BETWEEN_STATION,
                        value=worksheet.cell_value(currentRow, currentColumn + 3),
                        direction=MetroLineMetric.REVERSE)
                    currentColumn += 1
                currentRow += 1
                currentColumn = 1

            currentRow += ExcelWriter.SEPARATION_HEIGHT + 3
            currentColumn = 1

            for station in stations:
                for period in periods:
                    OperationPeriodForMetroStation.objects.create(
                        operationPeriod=period,
                        metroStation=station,
                        metric=OperationPeriodForMetroStation.DWELL_TIME,
                        value=worksheet.cell_value(currentRow, currentColumn),
                        direction=MetroLineMetric.GOING)
                    OperationPeriodForMetroStation.objects.create(
                        operationPeriod=period,
                        metroStation=station,
                        metric=OperationPeriodForMetroStation.DWELL_TIME,
                        value=worksheet.cell_value(currentRow, currentColumn + 3),
                        direction=MetroLineMetric.REVERSE)
                    currentColumn += 1
                currentRow += 1
                currentColumn = 1

            currentRow += ExcelWriter.SEPARATION_HEIGHT + 3
            currentColumn = 1

            for period in periods:
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.FREQUENCY,
                    value=worksheet.cell_value(currentRow, currentColumn),
                    direction=MetroLineMetric.GOING)
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.FREQUENCY,
                    value=worksheet.cell_value(currentRow, currentColumn + 3),
                    direction=MetroLineMetric.REVERSE)
                currentColumn += 1
            currentRow += 1

            currentRow += ExcelWriter.SEPARATION_HEIGHT + 3
            currentColumn = 1

            previousRow = currentRow
            for period in periods:
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.PERC_DC_DISTRIBUTION_LOSSES,
                    value=worksheet.cell_value(currentRow, currentColumn),
                    direction=MetroLineMetric.GOING)
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.PERC_DC_DISTRIBUTION_LOSSES,
                    value=worksheet.cell_value(currentRow, currentColumn + 3),
                    direction=MetroLineMetric.REVERSE)
                currentRow += 1
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.PERC_AC_SUBSTATION_LOSSES_FEED_ENTIRE_SYSTEM,
                    value=worksheet.cell_value(currentRow, currentColumn),
                    direction=MetroLineMetric.GOING)
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.PERC_AC_SUBSTATION_LOSSES_FEED_ENTIRE_SYSTEM,
                    value=worksheet.cell_value(currentRow, currentColumn + 3),
                    direction=MetroLineMetric.REVERSE)
                currentRow += 1
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.PERC_AC_SUBSTATION_LOSSES_FEED_AC_ELEMENTS,
                    value=worksheet.cell_value(currentRow, currentColumn),
                    direction=MetroLineMetric.GOING)
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.PERC_AC_SUBSTATION_LOSSES_FEED_AC_ELEMENTS,
                    value=worksheet.cell_value(currentRow, currentColumn + 3),
                    direction=MetroLineMetric.REVERSE)
                currentRow += 1
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.PERC_DC_SUBSTATION_LOSSES,
                    value=worksheet.cell_value(currentRow, currentColumn),
                    direction=MetroLineMetric.GOING)
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.PERC_DC_SUBSTATION_LOSSES,
                    value=worksheet.cell_value(currentRow, currentColumn + 3),
                    direction=MetroLineMetric.REVERSE)

                currentColumn += 1
                currentRow = previousRow

            currentRow += 4 + ExcelWriter.SEPARATION_HEIGHT + 2
            currentColumn = 1
            
            for period in periods:
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.RECEPTIVITY,
                    value=worksheet.cell_value(currentRow, currentColumn),
                    direction=None)
                currentColumn += 1
           
            currentRow += ExcelWriter.SEPARATION_HEIGHT + 3
            currentColumn = 1

            for station in stations:
                for period in periods:
                    OperationPeriodForMetroStation.objects.create(
                        operationPeriod=period,
                        metroStation=station,
                        metric=OperationPeriodForMetroStation.VENTILATION_FLOW,
                        value=worksheet.cell_value(currentRow, currentColumn),
                        direction=None)
                    currentColumn += 1
                    # TODO: check if period is need or not
                    break
                currentRow += 1
                currentColumn = 1


