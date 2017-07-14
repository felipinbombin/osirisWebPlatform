# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from abc import ABCMeta, abstractmethod
from StringIO import StringIO
from django.core.files.base import ContentFile

import xlsxwriter

SEPARATION_HEIGHT = 3
# row between blocks in worksheet


class ExcelWriter(object):
    ''' to manage excel files '''
    __metaclass__ = ABCMeta

    def __init__(self, scene):

        scene.refresh_from_db()
        self.scene = scene
        self.stringIO = StringIO()
        self.workbook = xlsxwriter.Workbook(self.stringIO, {'in_memory': True})

        self.cellTitleFormat = self.workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#169F85',
            'font_color': 'white',
            'locked': 1,
        })

        self.cellLeftTitleFormat = self.workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'left',
            'valign': 'vcenter',
            'bg_color': '#169F85',
            'font_color': 'white',
            'locked': 1,
        })

        self.cellFormat = self.workbook.add_format({
            'bold': 1,
            'border': 1
        })

        self.widths = []

    def getFileName(self):
        ''' name of file '''
        TYPE = 'generic'
        EXTENSION = 'xlsx'
        NAME = self.scene.name.replace(' ', '_')

        fileName = '{}_{}.{}'.format(NAME, TYPE, EXTENSION)

        return fileName

    def fitColumnWidth(self, worksheet, columnIndex, value):

        while len(self.widths) <= columnIndex:
            self.widths.append(0)

        width = len(value)
        if self.widths[columnIndex] <= width:
            self.widths[columnIndex] = width
            worksheet.set_column(columnIndex, columnIndex, width)

    def writeComment(self, worksheet, row, col, text):
        ''' write a comment on cell'''
        worksheet.write_comment(row, col, text)

    def makeTextCell(self, worksheet, upperLeftCorner, text, width=0,
                     height=0, cellFormat=None):
        ''' merge cells and put text '''
        upperRow = upperLeftCorner[0]
        leftColumn = upperLeftCorner[1]

        lowerRow = upperRow + height
        rightColumn = leftColumn + width

        if height == 0 and width == 0:
            worksheet.write(upperRow, leftColumn, text, cellFormat)
            self.fitColumnWidth(worksheet, leftColumn, text)
        else:
            worksheet.merge_range(upperRow, leftColumn, lowerRow, rightColumn,
                                  text, cellFormat)

    def makeTitleCell(self, worksheet, upperLeftCorner, text, width=0, height=0, cellFormat=None):
        ''' merge cells and give title format '''
        if cellFormat is None:
            cellFormat = self.cellTitleFormat
        self.makeTextCell(worksheet, upperLeftCorner, text, width,
                          height, cellFormat)

    def makeBlankCell(self, worksheet, upperLeftCorner):
        ''' merge cells and give blank cell format '''
        self.makeTextCell(worksheet, upperLeftCorner, '', 0, 0,
                          self.cellFormat)

    def makeHorizontalGrid(self, worksheet, upperLeftCorner, nameList, blankWidth):
        ''' make grid where first value is in the first column and next columns are blanks'''
        upperRow = upperLeftCorner[0]
        leftColumn = upperLeftCorner[1]
        rightColumn = leftColumn + blankWidth

        currentRow = upperRow
        for name in nameList:
            self.makeTitleCell(worksheet, (currentRow, leftColumn), name, 0, 0, self.cellLeftTitleFormat)
            # apply format to empty cells
            for col in range(leftColumn + 1, rightColumn + 1):
                self.makeBlankCell(worksheet, (currentRow, col))
            currentRow += 1

        usedRows = len(nameList)
        return usedRows

    def makeParamHeader(self, worksheet, upperLeftCorner, stationNameList, title, column_title_list, print_direction=True,
                        both_directions=True, blank_rows=0):
        """
        Build a block of cells with title, train directions and column titles

        :param worksheet: xlsxWritter Excel worksheet object
        :param stationNameList: list of stations to create direction names
        :param upperLeftCorner: location of the block
        :param title: main title
        :param column_title_list: list of header for each column
        :param print_direction: if print direction header. Default = True. If False so bothDirection is set to False
        :param both_directions: if print two train directions. Default = True
        :param blank_rows: number of rows below that have to be highlighted
        :return: on worksheet ==>

        |                         title                        |
        (row below is optional)
        |        first_direction   |         second_direction  |
        | subTitleList[0] |  ...   | subTitleList[0] | ...     |

        """
        column_title_number = len(column_title_list)
        row = upperLeftCorner[0]
        column = upperLeftCorner[1]
        titleWidth = column_title_number - 1

        if print_direction and both_directions:
            titleWidth = 2 * column_title_number - 1

        self.makeTitleCell(worksheet, (row, column), title, titleWidth)
        row += 1

        if print_direction:
            first_direction = stationNameList[0] + "-" + stationNameList[-1]
            second_direction = stationNameList[-1] + "-" + stationNameList[0]

            self.makeTitleCell(worksheet, (row, column), first_direction, column_title_number - 1)
            if both_directions:
                self.makeTitleCell(worksheet, (row, column + column_title_number), second_direction,
                                   column_title_number - 1)
            row += 1

        col = 0
        for column_title in column_title_list:
            self.makeTitleCell(worksheet, (row, column + col), column_title)
            if print_direction and both_directions:
                self.makeTitleCell(worksheet, (row, column + column_title_number + col),
                                   column_title)
            col += 1

        row += 1
        for index in range(blank_rows):
            length = column_title_number
            if print_direction and both_directions:
                length = 2 * column_title_number
            for col in range(0, length):
                self.makeBlankCell(worksheet, (row, column + col))
            row += 1

        usedRows = row - upperLeftCorner[0]
        return usedRows

    def save(self, fileField):
        ''' save file in scene field '''
        self.workbook.close()
        fileField.save(self.getFileName(), ContentFile(self.stringIO.getvalue()))

    @abstractmethod
    def createTemplateFile(self):
        pass


class Step1ExcelWriter(ExcelWriter):
    ''' create excel file for step 2 '''

    def __init__(self, scene):
        super(self.__class__, self).__init__(scene)

    def getFileName(self):
        ''' name of file '''
        fileName = super(self.__class__, self).getFileName()
        NAME = 'topologico'
        fileName = fileName.replace('generic', NAME)

        return fileName

    def makeStructureHeader(self, worksheet):

        STRUCTURE_TITLE = 'Características físicas de estaciones y túneles'
        STRUCTURE_STATION_TITLE = 'Estaciones'
        STRUCTURE_TUNNEL_TITLE = 'Túneles'

        STRUCTURE_STATION_SEGMENT_TITLE = 'Segmento:'
        STRUCTURE_STATION_LENGTH_TITLE = 'Largo [m]:'
        STRUCTURE_STATION_SURFACE_TITLE = 'Superficie [m^2]:'
        STRUCTURE_STATION_PERIMETER_TITLE = 'Perímetro [m]:'
        STRUCTURE_2ND_LEVEL_AVG_HEIGHT_TITLE = 'Altura promedio 2do nivel [m]:'
        STRUCTURE_2ND_LEVEL_AVG_SURFACE_TITLE = 'Superficie 2do nivel [m^2]:'

        worksheet.merge_range('A1:K1', STRUCTURE_TITLE, self.cellTitleFormat)
        worksheet.merge_range('A2:F2', STRUCTURE_STATION_TITLE, self.cellTitleFormat)
        worksheet.merge_range('H2:K2', STRUCTURE_TUNNEL_TITLE, self.cellTitleFormat)
        worksheet.write('A3', STRUCTURE_STATION_SEGMENT_TITLE, self.cellTitleFormat)
        worksheet.write('B3', STRUCTURE_STATION_LENGTH_TITLE, self.cellTitleFormat)
        worksheet.write('C3', STRUCTURE_STATION_SURFACE_TITLE, self.cellTitleFormat)
        worksheet.write('D3', STRUCTURE_STATION_PERIMETER_TITLE, self.cellTitleFormat)
        worksheet.write('E3', STRUCTURE_2ND_LEVEL_AVG_HEIGHT_TITLE, self.cellTitleFormat)
        worksheet.write('F3', STRUCTURE_2ND_LEVEL_AVG_SURFACE_TITLE, self.cellTitleFormat)

        worksheet.write('H3', STRUCTURE_STATION_SEGMENT_TITLE, self.cellTitleFormat)
        worksheet.write('I3', STRUCTURE_STATION_LENGTH_TITLE, self.cellTitleFormat)
        worksheet.write('J3', STRUCTURE_STATION_SURFACE_TITLE, self.cellTitleFormat)
        worksheet.write('K3', STRUCTURE_STATION_PERIMETER_TITLE, self.cellTitleFormat)

        # fit witdh 
        texts = [
            STRUCTURE_STATION_SEGMENT_TITLE,
            STRUCTURE_STATION_LENGTH_TITLE,
            STRUCTURE_STATION_SURFACE_TITLE,
            STRUCTURE_STATION_PERIMETER_TITLE,
            STRUCTURE_2ND_LEVEL_AVG_HEIGHT_TITLE,
            STRUCTURE_2ND_LEVEL_AVG_SURFACE_TITLE,
            'space',
            STRUCTURE_STATION_SEGMENT_TITLE,
            STRUCTURE_STATION_LENGTH_TITLE,
            STRUCTURE_STATION_SURFACE_TITLE,
            STRUCTURE_STATION_PERIMETER_TITLE,
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

            stationNameList = list(line.metrostation_set.values_list('name', flat=True).order_by('id'))
            height = self.makeHorizontalGrid(worksheet, (lastRow + 1, 0),
                                             stationNameList, 5)

            trackNameList = []
            trackName = '{}-'.format(stationNameList[0])
            for name in stationNameList[1:]:
                trackName += name
                trackNameList.append(trackName)
                trackName = '{}-'.format(name)
            self.makeHorizontalGrid(worksheet, (lastRow + 1, 7), trackNameList, 3)

            lastRow += height + SEPARATION_HEIGHT

            # additionHeaders
            titles = ['Pendiente', 'Radio de curvatura', 'Límite de velocidad',
                      'Nivel (1: sobre tierra, 0: bajo tierra)']
            subTitles = [
                ['Inicio de segmento [m]', 'Fin de segmento [m]', 'Pendiente [%]'],
                ['Inicio de segmento [m]', 'Fin de segmento [m]', 'Radio [m]'],
                ['Inicio de segmento [m]', 'Fin de segmento [m]', 'Límite [m/s]'],
                ['Inicio de segmento [m]', 'Fin de segmento [m]', 'Nivel']
            ]
            bothDirections = [True, True, True, False]

            for index, title in enumerate(titles):
                height = self.makeParamHeader(worksheet, (lastRow + 1, 0), stationNameList, title,
                                              subTitles[index], blank_rows=1,
                                              both_directions=bothDirections[index])
                lastRow += height + SEPARATION_HEIGHT

        self.save(self.scene.step1Template)


class Step3ExcelWriter(ExcelWriter):
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


class Step5ExcelWriter(ExcelWriter):
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
