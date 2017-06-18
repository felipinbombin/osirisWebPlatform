# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.core.files import File

from scene.models import Scene, MetroConnection, MetroLine, MetroStation, MetroDepot, MetroConnectionStation

import xlsxwriter
import os

class Excel(object):
    ''' to manage excel files '''

    def __init__(self, scene):

        scene.refresh_from_db()
        self.scene = scene
        self.workbook = xlsxwriter.Workbook('{}/{}'.format(self.getMediaPath(), self.getFileName()))

        self.cellTitleFormat = self.workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#169F85',
            'font_color': 'white'})

        self.widths = []

    def getMediaPath(self):
        ''' path where files are saved '''
        PATH = os.path.join(settings.MEDIA_ROOT, 'step2Template')

        return PATH

    def getFileName(self):
        ''' name of file '''
        NAME = 'generic'
        EXTENSION = 'xlsx'

        fileName = '{}_{}.{}'.format(self.scene.name, NAME, EXTENSION)

        return fileName

    def fitColumnWidth(self, worksheet, columnIndex, value):

        while len(self.widths) <= columnIndex:
            self.widths.append(0)

        width = len(value)
        if self.widths[columnIndex] <= width:
            self.widths[columnIndex] = width
            worksheet.set_column(columnIndex, columnIndex, width)

    def makeParamHeader(self, worksheet, metroLine, firstRow, title, subTitleList, bothDirections=True):

        stationNameList = metroLine.metrostation_set.values_list('name', flat=True)
        firstStation = stationNameList[0]
        lastStation = stationNameList[len(stationNameList)-1]
        firstDirection = '{}-{}'.format(firstStation, lastStation)
        secondDirection = '{}-{}'.format(lastStation, firstStation)

        subTitleNumber = len(subTitleList)
        row = firstRow
        if bothDirections:
            titleWidth = 2*subTitleNumber - 1
        else:
            titleWidth = subTitleNumber -1

        worksheet.merge_range(row,0, row, titleWidth, title, self.cellTitleFormat)

        row += 1
        worksheet.merge_range(row, 0, row, subTitleNumber-1, firstDirection, self.cellTitleFormat)
        if bothDirections:
            worksheet.merge_range(row, subTitleNumber, row, 2*subTitleNumber-1, secondDirection, self.cellTitleFormat)

        col = 0
        for subTitle in subTitleList:
            worksheet.write(firstRow + 2, col, subTitle, self.cellTitleFormat)
            self.fitColumnWidth(worksheet, col, subTitle)
            if bothDirections:
                worksheet.write(firstRow + 2, subTitleNumber + col, subTitle, self.cellTitleFormat)
                self.fitColumnWidth(worksheet, subTitleNumber + col, subTitle)
            col += 1

    def save(self, fileField):
        ''' save file in scene field '''

        self.workbook.close()

        localFile = open('{}/{}'.format(self.getMediaPath(), self.getFileName()))
        djangoFile = File(localFile)
        fileField.save(self.getFileName(), djangoFile)
        localFile.close()

class Step2Excel(Excel):
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

    def createTopologicalFile(self):
        ''' create excel file based on scene data '''

        for line in self.scene.metroline_set.all().order_by('name'):
            worksheet = self.workbook.add_worksheet(line.name)
            self.makeStructureHeader(worksheet)

            cellFormat = self.workbook.add_format({
                'bold': 1,
                'border': 1
            })
            row = 3
            tunnelName = ''
            for index, station in enumerate(line.metrostation_set.all()):
                worksheet.write(row, 0, station.name, cellFormat)
                self.fitColumnWidth(worksheet, 0, station.name)

                # apply format to empty cells
                for col in range(1,6):
                    worksheet.write(row, col, None, cellFormat)

                # add tunnel names
                if index > 0:
                    tunnelName += station.name 
                    worksheet.write(row-1, 7, tunnelName, cellFormat)
                    self.fitColumnWidth(worksheet, 7, tunnelName)
                    # apply format to empty cells
                    for col in range(8, 11):
                        worksheet.write(row-1, col, None, cellFormat)
                tunnelName = '{}-'.format(station.name)
                row += 1
  
            # additionHeaders
            titles = ['Pendiente', 'Radio de curvatura', 'Límite de velocidad', 'Nivel (1: sobre tierra, 0: bajo tierra)']
            subTitles = [
                ['Inicio de segmento [m]', 'Fin de segmento [m]', 'Pendiente [%]'],
                ['Inicio de segmento [m]', 'Fin de segmento [m]', 'Radio [m]'],
                ['Inicio de segmento [m]', 'Fin de segmento [m]', 'Límite [m/s]'],
                ['Inicio de segmento [m]', 'Fin de segmento [m]', 'Nivel']
            ]
            bothDirections = [True, True, True, False]
            row += 4    
            for index, title in enumerate(titles):
                self.makeParamHeader(worksheet, line, row, title, subTitles[index], 
                    bothDirections=bothDirections[index])
                row += 7

        self.save(self.scene.step2Template)

