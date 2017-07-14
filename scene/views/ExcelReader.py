# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from abc import ABCMeta, abstractmethod
from StringIO import StringIO
from django.core.files.base import ContentFile

import ExcelWriter
from ..models import MetroTrack, MetroLineMetric

import xlrd

GOING = "going"
REVERSE = "reverse"

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
            depots = line.metrodepot_set.all().order_by('id')

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
                    metroTrack.averageParameter = worksheet.cell_value(currentRow, 10)
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
                                                       direction=GOING)
                        MetroLineMetric.objects.create(metroLine=line,
                                                       metric=metrics[currentArray],
                                                       start=worksheet.cell_value(row, 3),
                                                       end=worksheet.cell_value(row, 4),
                                                       value=worksheet.cell_value(row, 5),
                                                       direction=REVERSE)
                row += 1

        MetroTrack.objects.filter(metroLine__scene=self.scene, isOld=True).delete()

class Step3Excel(ExcelReader):
    ''' create excel file for step 4 '''

    def __init__(self, scene):
        super(self.__class__, self).__init__(scene)

    def getFileName(self):
        ''' name of file '''
        fileName = super(self.__class__, self).getFileName()
        NAME = 'sistemico'
        fileName = fileName.replace('generic', NAME)

        return fileName

    def makeStructureHeader(self, worksheet):

        TITLE = 'Consumo energético de estaciones, túneles y depósitos'
        STATION_TITLE = 'Estaciones'
        TUNNEL_TITLE = 'Túneles'
        DEPOT_TITLE = 'Depósitos'

        STATION_SEGMENT_TITLE = 'Estación:'
        STATION_MIN_AUX_CONSUMPTION_TITLE = 'Consumo auxiliar mín [W]:'
        STATION_MAX_AUX_CONSUMPTION_TITLE = 'Consumo auxiliar máx [W]:'
        STATION_MIN_HVAC_CONSUMPTION_TITLE = 'Consumo HVAC mín [W]:'
        STATION_MAX_HVAC_CONSUMPTION_TITLE = 'Consumo HVAC máx [W]:'
        STATION_TAU_TITLE = 'Tau:'

        TRACK_SEGMENT_TITLE = 'Túnel:'
        TRACK_AUX_CONSUMPTION_TITLE = 'Consumo de auxiliares [W]:'
        TRACK_VENTILATION_CONSUMPTION_TITLE = 'Consumo de ventilación [W]:'

        DEPOT_SEGMENT_TITLE = 'Depósito:'
        DEPOT_AUX_CONSUMPTION_TITLE = 'Consumo de auxiliares [W]:'
        DEPOT_VENTILATION_CONSUMPTION_TITLE = 'Consumo de ventilación [W]:'
        DEPOT_DC_CONSUMPTION_TITLE = 'Consumo DC [W]:'

        worksheet.merge_range('A1:O1', TITLE, self.cellTitleFormat)
        worksheet.merge_range('A2:F2', STATION_TITLE, self.cellTitleFormat)
        worksheet.merge_range('H2:J2', TUNNEL_TITLE, self.cellTitleFormat)
        worksheet.merge_range('L2:O2', DEPOT_TITLE, self.cellTitleFormat)
        worksheet.write('A3', STATION_SEGMENT_TITLE, self.cellTitleFormat)
        worksheet.write('B3', STATION_MIN_AUX_CONSUMPTION_TITLE, self.cellTitleFormat)
        worksheet.write('C3', STATION_MAX_AUX_CONSUMPTION_TITLE, self.cellTitleFormat)
        worksheet.write('D3', STATION_MIN_HVAC_CONSUMPTION_TITLE, self.cellTitleFormat)
        worksheet.write('E3', STATION_MAX_HVAC_CONSUMPTION_TITLE, self.cellTitleFormat)
        worksheet.write('F3', STATION_TAU_TITLE, self.cellTitleFormat)

        worksheet.write('H3', TRACK_SEGMENT_TITLE, self.cellTitleFormat)
        worksheet.write('I3', TRACK_AUX_CONSUMPTION_TITLE, self.cellTitleFormat)
        worksheet.write('J3', TRACK_VENTILATION_CONSUMPTION_TITLE, self.cellTitleFormat)
        worksheet.write('L3', DEPOT_SEGMENT_TITLE, self.cellTitleFormat)
        worksheet.write('M3', DEPOT_AUX_CONSUMPTION_TITLE, self.cellTitleFormat)
        worksheet.write('N3', DEPOT_VENTILATION_CONSUMPTION_TITLE, self.cellTitleFormat)
        worksheet.write('O3', DEPOT_DC_CONSUMPTION_TITLE, self.cellTitleFormat)

        # fit witdh 
        texts = [
            STATION_SEGMENT_TITLE,
            STATION_MIN_AUX_CONSUMPTION_TITLE,
            STATION_MAX_AUX_CONSUMPTION_TITLE,
            STATION_MIN_HVAC_CONSUMPTION_TITLE,
            STATION_MAX_HVAC_CONSUMPTION_TITLE,
            STATION_TAU_TITLE,
            'space',
            TRACK_SEGMENT_TITLE,
            TRACK_AUX_CONSUMPTION_TITLE,
            TRACK_VENTILATION_CONSUMPTION_TITLE,
            'space',
            DEPOT_SEGMENT_TITLE,
            DEPOT_AUX_CONSUMPTION_TITLE,
            DEPOT_VENTILATION_CONSUMPTION_TITLE,
            DEPOT_DC_CONSUMPTION_TITLE
        ]
        for index, text in enumerate(texts):
            self.fitColumnWidth(worksheet, index, text)

        usedRows = 2
        return usedRows

    def createTemplateFile(self):
        ''' create excel file based on scene data '''

        for line in self.scene.metroline_set.all().order_by('name'):
            worksheet = self.workbook.add_worksheet(line.name)

            lastRow = self.makeStructureHeader(worksheet)

            stationNameList = line.metrostation_set.values_list('name', flat=True).order_by('id')
            stationHeight = self.makeHorizontalGrid(worksheet, (lastRow + 1, 0),
                                                    stationNameList, 5)

            trackNameList = []
            trackName = '{}-'.format(stationNameList[0])
            for name in stationNameList[1:]:
                trackName += name
                trackNameList.append(trackName)
                trackName = '{}-'.format(name)
            self.makeHorizontalGrid(worksheet, (lastRow + 1, 7), trackNameList, 2)

            depotNameList = line.metrodepot_set.values_list('name', flat=True)
            depotHeight = self.makeHorizontalGrid(worksheet, (lastRow + 1, 11),
                                                  depotNameList, 3)

            lastRow += max(stationHeight, depotHeight) + SEPARATION_HEIGHT

            # additionHeaders
            title = 'Características SESS de la línea'
            self.makeTitleCell(worksheet, (lastRow + 1, 0), title, 1)

            subTitles = [
                'Usable energy content [Wh]:',
                'Charging Efficiency [%]:',
                'Discharging Efficiency [%]:',
                'Peak power [W]:',
                'Maximum energy saving possible per hour [W]:',
                'Energy saving mode (1 = true / 0 = false):',
                'Power limit to feed [W]:'
            ]
            self.makeHorizontalGrid(worksheet, (lastRow + 2, 0), subTitles, 1)

        self.save(self.scene.step3Template)


class Step5Excel(ExcelReader):
    ''' create excel file for step 5 '''

    def __init__(self, scene):
        super(self.__class__, self).__init__(scene)

    def getFileName(self):
        ''' name of file '''
        fileName = super(self.__class__, self).getFileName()
        NAME = 'operación'
        fileName = fileName.replace('generic', NAME)

        return fileName

    def createTemplateFile(self):
        ''' create excel file based on scene data '''

        periodsNameList = list(self.scene.operationperiod_set.values_list('name', flat=True).order_by('id'))

        for line in self.scene.metroline_set.all().order_by('name'):
            worksheet = self.workbook.add_worksheet(line.name)
            stationNameList = list(line.metrostation_set.values_list('name', flat=True).order_by('id'))

            trackNameList = []
            trackName = '{}-'.format(stationNameList[0])
            for name in stationNameList[1:]:
                trackName += name
                trackNameList.append(trackName)
                trackName = '{}-'.format(name)

            lastRow = 0

            title = "Pasajeros en estación"
            columnTitleList = ["Estación/período"] + periodsNameList
            lastRow += self.makeParamHeader(worksheet, (lastRow, 0), stationNameList, title, columnTitleList)
            self.makeHorizontalGrid(worksheet, (lastRow, 0), stationNameList, len(periodsNameList))
            lastRow += self.makeHorizontalGrid(worksheet, (lastRow, 1+ len(periodsNameList)), stationNameList[::-1], len(periodsNameList))

            lastRow += SEPARATION_HEIGHT

            title = "Pasajeros viajando entre estaciones"
            columnTitleList = ["Túnel / Período"] + periodsNameList
            lastRow += self.makeParamHeader(worksheet, (lastRow, 0), stationNameList, title, columnTitleList)
            self.makeHorizontalGrid(worksheet, (lastRow, 0), trackNameList, len(periodsNameList))
            lastRow += self.makeHorizontalGrid(worksheet, (lastRow, 1+ len(periodsNameList)), trackNameList[::-1], len(periodsNameList))

            lastRow += SEPARATION_HEIGHT

            title = "Máximo tiempo permitido de viaje entre dos estaciones [s]"
            columnTitleList = ["Túnel / Período"] + periodsNameList
            lastRow += self.makeParamHeader(worksheet, (lastRow, 0), stationNameList, title, columnTitleList)
            self.makeHorizontalGrid(worksheet, (lastRow, 0), trackNameList, len(periodsNameList))
            lastRow += self.makeHorizontalGrid(worksheet, (lastRow, 1+ len(periodsNameList)), trackNameList[::-1], len(periodsNameList))

            lastRow += SEPARATION_HEIGHT

            title = "Tiempo de permanencia entre estaciones [s]"
            columnTitleList = ["Estación / Período"] + periodsNameList
            lastRow += self.makeParamHeader(worksheet, (lastRow, 0), stationNameList, title, columnTitleList)
            self.makeHorizontalGrid(worksheet, (lastRow, 0), stationNameList, len(periodsNameList))
            lastRow += self.makeHorizontalGrid(worksheet, (lastRow, 1+ len(periodsNameList)), stationNameList[::-1], len(periodsNameList))

            lastRow += SEPARATION_HEIGHT

            title = "Frecuencia de trenes"
            columnTitleList = ["Período:"] + periodsNameList
            frequency_list = ["Frecuencia [trenes/hora]"]
            lastRow += self.makeParamHeader(worksheet, (lastRow, 0), stationNameList, title, columnTitleList)
            self.makeHorizontalGrid(worksheet, (lastRow, 0), frequency_list, len(periodsNameList))
            lastRow += self.makeHorizontalGrid(worksheet, (lastRow, 1+ len(periodsNameList)), frequency_list, len(periodsNameList))

            lastRow += SEPARATION_HEIGHT

            title = "Porcentaje de perdida"
            columnTitleList = ["Período:"] + periodsNameList
            paramList = ["Percentage DC distribution Losses:",
                         "Percentage AC substation Losses (feed entire system):",
                         "Percentage AC substation Losses (feed AC elements):",
                         "Percentage DC substation Losses:"]
            lastRow += self.makeParamHeader(worksheet, (lastRow, 0), stationNameList, title, columnTitleList)
            self.makeHorizontalGrid(worksheet, (lastRow, 0), paramList, len(periodsNameList))
            lastRow += self.makeHorizontalGrid(worksheet, (lastRow, 1+ len(periodsNameList)), paramList,
                                               len(periodsNameList))

            lastRow += SEPARATION_HEIGHT

            title = "Receptivity of the line [%]:"
            columnTitleList = ["Período:"] + periodsNameList
            lastRow += self.makeParamHeader(worksheet, (lastRow, 0), stationNameList, title, columnTitleList,
                                            print_direction=False)
            lastRow += self.makeHorizontalGrid(worksheet, (lastRow, 0), ["Receptivity [%]"], len(periodsNameList))

            lastRow += SEPARATION_HEIGHT

            title = "Flujo de ventilación"
            columnTitleList = ["Estación", "Flujo [m^3/s]"]
            lastRow += self.makeParamHeader(worksheet, (lastRow, 0), stationNameList, title, columnTitleList,
                                            print_direction=False)
            lastRow += self.makeHorizontalGrid(worksheet, (lastRow, 0), stationNameList, 1)

        self.save(self.scene.step5Template)
