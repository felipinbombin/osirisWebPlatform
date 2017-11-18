# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod
from django.utils import timezone

from .ExcelWriter import SEPARATION_HEIGHT
from ..models import MetroTrack, MetroLineMetric, OperationPeriodForMetroLine, OperationPeriodForMetroStation, \
    OperationPeriodForMetroTrack

import xlrd


class ExcelReader(object):
    """ to manage excel files """
    __metaclass__ = ABCMeta

    def __init__(self, scene):
        scene.refresh_from_db()
        self.scene = scene

    @abstractmethod
    def process_file(self, in_memory_file):
        pass


class Step1ExcelReader(ExcelReader):
    """ read excel file uploaded on step 2 """

    def __init__(self, scene):
        super(self.__class__, self).__init__(scene)

    def process_file(self, in_memory_file):
        """ read excel file and retrieve data """
        workbook = xlrd.open_workbook(file_contents=in_memory_file.read())

        # all metro track records are old
        MetroTrack.objects.filter(metroLine__scene=self.scene).update(isOld=True)

        for line in self.scene.metroline_set.all().order_by('id'):
            stations = line.metrostation_set.all().order_by('id')

            worksheet = workbook.sheet_by_name(line.name)

            first_row = 3
            current_row = first_row
            for index, station in enumerate(stations):
                station.length = worksheet.cell_value(current_row, 1)
                station.platformSection = worksheet.cell_value(current_row, 2)
                station.platformAveragePerimeter = worksheet.cell_value(current_row, 3)
                station.secondLevelAverageHeight = worksheet.cell_value(current_row, 4)
                station.secondLevelFloorSurface = worksheet.cell_value(current_row, 5)
                station.save()

                # create tracks
                if index < len(stations) - 1:
                    next_station = stations[index + 1]
                    name = station.name + "-" + next_station.name
                    metro_track, created = MetroTrack.objects.get_or_create(metroLine=line, name=name,
                                                                            defaults={"startStation": station,
                                                                                      "endStation": next_station})
                    if not created:
                        metro_track.startStation = station
                        metro_track.endStation = next_station
                    metro_track.length = worksheet.cell_value(current_row, 8)
                    metro_track.crossSection = worksheet.cell_value(current_row, 9)
                    metro_track.averagePerimeter = worksheet.cell_value(current_row, 10)
                    metro_track.isOld = False
                    metro_track.save()

                current_row += 1

            first_row = 3 + len(stations) + SEPARATION_HEIGHT + 3

            # delete previous metrics
            MetroLineMetric.objects.filter(metroLine=line).delete()
            metrics = [
                MetroLineMetric.SLOPE,
                MetroLineMetric.CURVE_RADIUS,
                MetroLineMetric.SPEED_LIMIT,
                MetroLineMetric.GROUND
            ]
            row = first_row
            previous_c_type = None
            current_array = 0
            while row < worksheet.nrows:
                c_type = worksheet.cell(row, 0).ctype
                # dict of ctype
                # 0: empty string u''
                # 1: a Unicode string
                # 2: float
                if c_type == 0 and previous_c_type is not None:
                    previous_c_type = c_type
                elif c_type == 1 and previous_c_type != 1:
                    current_array += 1
                    previous_c_type = c_type
                elif c_type == 2:
                    previous_c_type = None
                    if current_array == 3:
                        MetroLineMetric.objects.create(metroLine=line,
                                                       metric=metrics[current_array],
                                                       start=worksheet.cell_value(row, 0),
                                                       end=worksheet.cell_value(row, 1),
                                                       value=worksheet.cell_value(row, 2),
                                                       direction=None)
                    else:
                        MetroLineMetric.objects.create(metroLine=line,
                                                       metric=metrics[current_array],
                                                       start=worksheet.cell_value(row, 0),
                                                       end=worksheet.cell_value(row, 1),
                                                       value=worksheet.cell_value(row, 2),
                                                       direction=MetroLineMetric.GOING)
                        MetroLineMetric.objects.create(metroLine=line,
                                                       metric=metrics[current_array],
                                                       start=worksheet.cell_value(row, 3),
                                                       end=worksheet.cell_value(row, 4),
                                                       value=worksheet.cell_value(row, 5),
                                                       direction=MetroLineMetric.REVERSE)
                row += 1

        MetroTrack.objects.filter(metroLine__scene=self.scene, isOld=True).delete()
        self.scene.timeStampStep1File = timezone.now()
        self.scene.save()


class Step3ExcelReader(ExcelReader):
    """ read excel file uploaded in step 3 """

    def __init__(self, scene):
        super(self.__class__, self).__init__(scene)

    def process_file(self, in_memory_file):
        """ read excel file and retrieve data """
        workbook = xlrd.open_workbook(file_contents=in_memory_file.read())

        for line in self.scene.metroline_set.all().order_by('id'):
            stations = line.metrostation_set.all().order_by('id')
            depots = line.metrodepot_set.all().order_by('id')

            worksheet = workbook.sheet_by_name(line.name)

            first_row = 3
            current_row = first_row
            for index, station in enumerate(stations):
                station.minAuxConsumption = worksheet.cell_value(current_row, 1)
                station.maxAuxConsumption = worksheet.cell_value(current_row, 2)
                station.minHVACConsumption = worksheet.cell_value(current_row, 3)
                station.maxHVACConsumption = worksheet.cell_value(current_row, 4)
                station.tau = worksheet.cell_value(current_row, 5)
                station.save()

                # create tracks
                if index < len(stations) - 1:
                    next_station = stations[index + 1]
                    name = station.name + "-" + next_station.name
                    metro_track = MetroTrack.objects.get(metroLine=line, name=name)
                    metro_track.auxiliariesConsumption = worksheet.cell_value(current_row, 8)
                    metro_track.ventilationConsumption = worksheet.cell_value(current_row, 9)
                    metro_track.save()

                current_row += 1

            current_row = first_row
            for depot in depots:
                depot.auxConsumption = worksheet.cell_value(current_row, 12)
                depot.ventilationConsumption = worksheet.cell_value(current_row, 13)
                depot.dcConsumption = worksheet.cell_value(current_row, 14)
                depot.save()

            current_row = 3 + len(stations) + SEPARATION_HEIGHT + 1

            line.usableEnergyContent = worksheet.cell_value(current_row, 1)
            current_row += 1
            line.chargingEfficiency = worksheet.cell_value(current_row, 1)
            current_row += 1
            line.dischargingEfficiency = worksheet.cell_value(current_row, 1)
            current_row += 1
            line.peakPower = worksheet.cell_value(current_row, 1)
            current_row += 1
            line.maximumEnergySavingPossiblePerHour = worksheet.cell_value(current_row, 1)
            current_row += 1
            line.energySavingMode = worksheet.cell_value(current_row, 1)
            current_row += 1
            line.powerLimitToFeed = worksheet.cell_value(current_row, 1)
            line.save()

        self.scene.timeStampStep3File = timezone.now()
        self.scene.save()


class Step5ExcelReader(ExcelReader):
    """ create excel file for step 5 """

    def __init__(self, scene):
        super(self.__class__, self).__init__(scene)

    def process_file(self, in_memory_file):
        """ read excel file and retrieve data """
        workbook = xlrd.open_workbook(file_contents=in_memory_file.read())

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

            first_row = 3
            current_row = first_row
            current_column = 1

            for station in stations:
                for period in periods:
                    OperationPeriodForMetroStation.objects.create(
                        operationPeriod=period,
                        metroStation=station,
                        metric=OperationPeriodForMetroStation.PASSENGERS_IN_STATION,
                        value=worksheet.cell_value(current_row, current_column),
                        direction=MetroLineMetric.GOING)
                    OperationPeriodForMetroStation.objects.create(
                        operationPeriod=period,
                        metroStation=station,
                        metric=OperationPeriodForMetroStation.PASSENGERS_IN_STATION,
                        value=worksheet.cell_value(current_row, current_column + 3),
                        direction=MetroLineMetric.REVERSE)
                    current_column += 1
                current_row += 1
                current_column = 1

            current_row += SEPARATION_HEIGHT + 3
            current_column = 1

            for track in tracks:
                for period in periods:
                    OperationPeriodForMetroTrack.objects.create(
                        operationPeriod=period,
                        metroTrack=track,
                        metric=OperationPeriodForMetroTrack.PASSENGERS_TRAVELING_BETWEEN_STATION,
                        value=worksheet.cell_value(current_row, current_column),
                        direction=MetroLineMetric.GOING)
                    OperationPeriodForMetroTrack.objects.create(
                        operationPeriod=period,
                        metroTrack=track,
                        metric=OperationPeriodForMetroTrack.PASSENGERS_TRAVELING_BETWEEN_STATION,
                        value=worksheet.cell_value(current_row, current_column + 3),
                        direction=MetroLineMetric.REVERSE)
                    current_column += 1
                current_row += 1
                current_column = 1

            current_row += SEPARATION_HEIGHT + 3
            current_column = 1

            for track in tracks:
                for period in periods:
                    OperationPeriodForMetroTrack.objects.create(
                        operationPeriod=period,
                        metroTrack=track,
                        metric=OperationPeriodForMetroTrack.MAX_TRAVEL_TIME_BETWEEN_STATION,
                        value=worksheet.cell_value(current_row, current_column),
                        direction=MetroLineMetric.GOING)
                    OperationPeriodForMetroTrack.objects.create(
                        operationPeriod=period,
                        metroTrack=track,
                        metric=OperationPeriodForMetroTrack.MAX_TRAVEL_TIME_BETWEEN_STATION,
                        value=worksheet.cell_value(current_row, current_column + 3),
                        direction=MetroLineMetric.REVERSE)
                    current_column += 1
                current_row += 1
                current_column = 1

            current_row += SEPARATION_HEIGHT + 3
            current_column = 1

            for station in stations:
                for period in periods:
                    OperationPeriodForMetroStation.objects.create(
                        operationPeriod=period,
                        metroStation=station,
                        metric=OperationPeriodForMetroStation.DWELL_TIME,
                        value=worksheet.cell_value(current_row, current_column),
                        direction=MetroLineMetric.GOING)
                    OperationPeriodForMetroStation.objects.create(
                        operationPeriod=period,
                        metroStation=station,
                        metric=OperationPeriodForMetroStation.DWELL_TIME,
                        value=worksheet.cell_value(current_row, current_column + 3),
                        direction=MetroLineMetric.REVERSE)
                    current_column += 1
                current_row += 1
                current_column = 1

            current_row += SEPARATION_HEIGHT + 3
            current_column = 1

            for period in periods:
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.FREQUENCY,
                    value=worksheet.cell_value(current_row, current_column),
                    direction=MetroLineMetric.GOING)
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.FREQUENCY,
                    value=worksheet.cell_value(current_row, current_column + 3),
                    direction=MetroLineMetric.REVERSE)
                current_column += 1
            current_row += 1

            current_row += SEPARATION_HEIGHT + 3
            current_column = 1

            previous_row = current_row
            for period in periods:
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.PERC_DC_DISTRIBUTION_LOSSES,
                    value=worksheet.cell_value(current_row, current_column),
                    direction=MetroLineMetric.GOING)
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.PERC_DC_DISTRIBUTION_LOSSES,
                    value=worksheet.cell_value(current_row, current_column + 3),
                    direction=MetroLineMetric.REVERSE)
                current_row += 1
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.PERC_AC_SUBSTATION_LOSSES_FEED_ENTIRE_SYSTEM,
                    value=worksheet.cell_value(current_row, current_column),
                    direction=MetroLineMetric.GOING)
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.PERC_AC_SUBSTATION_LOSSES_FEED_ENTIRE_SYSTEM,
                    value=worksheet.cell_value(current_row, current_column + 3),
                    direction=MetroLineMetric.REVERSE)
                current_row += 1
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.PERC_AC_SUBSTATION_LOSSES_FEED_AC_ELEMENTS,
                    value=worksheet.cell_value(current_row, current_column),
                    direction=MetroLineMetric.GOING)
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.PERC_AC_SUBSTATION_LOSSES_FEED_AC_ELEMENTS,
                    value=worksheet.cell_value(current_row, current_column + 3),
                    direction=MetroLineMetric.REVERSE)
                current_row += 1
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.PERC_DC_SUBSTATION_LOSSES,
                    value=worksheet.cell_value(current_row, current_column),
                    direction=MetroLineMetric.GOING)
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.PERC_DC_SUBSTATION_LOSSES,
                    value=worksheet.cell_value(current_row, current_column + 3),
                    direction=MetroLineMetric.REVERSE)

                current_column += 1
                current_row = previous_row

            current_row += 4 + SEPARATION_HEIGHT + 2
            current_column = 1

            for period in periods:
                OperationPeriodForMetroLine.objects.create(
                    operationPeriod=period,
                    metroLine=line,
                    metric=OperationPeriodForMetroLine.RECEPTIVITY,
                    value=worksheet.cell_value(current_row, current_column),
                    direction=None)
                current_column += 1

            current_row += SEPARATION_HEIGHT + 3
            current_column = 1

            for station in stations:
                for period in periods:
                    OperationPeriodForMetroStation.objects.create(
                        operationPeriod=period,
                        metroStation=station,
                        metric=OperationPeriodForMetroStation.VENTILATION_FLOW,
                        value=worksheet.cell_value(current_row, current_column),
                        direction=None)
                    current_column += 1
                current_row += 1
                current_column = 1

        self.scene.timeStampStep5File = timezone.now()
        self.scene.save()


class Step6ExcelReader(ExcelReader):
    """ create excel file for step 6 """

    def __init__(self, scene):
        super(self.__class__, self).__init__(scene)

    def process_file(self, in_memory_file):
        """ read excel file and retrieve data """
        workbook = xlrd.open_workbook(file_contents=in_memory_file.read())

        # process file

        self.scene.timeStampStep6File = timezone.now()
        self.scene.save()
