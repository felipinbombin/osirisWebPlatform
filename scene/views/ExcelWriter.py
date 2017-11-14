# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod
from io import BytesIO
from django.core.files.base import ContentFile

from scene.models import MetroLineMetric

import xlsxwriter

# row between blocks in worksheet
SEPARATION_HEIGHT = 3


class ExcelHelper:
    """ methods to manipulate structures inside workbook """

    def __init__(self, workbook):

        self.workbook = workbook
        self.cell_title_format = self.workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "bg_color": "#169F85",
            "font_color": "white",
            "locked": 1,
        })

        self.cell_left_title_format = self.workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": "left",
            "valign": "vcenter",
            "bg_color": "#169F85",
            "font_color": "white",
            "locked": 1,
        })

        self.cell_format = self.workbook.add_format({
            "bold": 1,
            "border": 1
        })

        self.widths = []

    def write_comment(self, worksheet, row, col, text):
        """ write a comment on cell"""
        worksheet.write_comment(row, col, text)

    def make_text_cell(self, worksheet, upper_left_corner, text, width=0,
                       height=0, cell_format=None):
        """ merge cells and put text """
        upper_row = upper_left_corner[0]
        left_column = upper_left_corner[1]

        lower_row = upper_row + height
        right_column = left_column + width

        if height == 0 and width == 0:
            worksheet.write(upper_row, left_column, text, cell_format)
            self.fit_column_width(worksheet, left_column, text)
        else:
            worksheet.merge_range(upper_row, left_column, lower_row, right_column,
                                  text, cell_format)

    def make_title_cell(self, worksheet, upper_left_corner, text, width=0, height=0, cell_format=None):
        """ merge cells and give title format """
        if cell_format is None:
            cell_format = self.cell_title_format
        self.make_text_cell(worksheet, upper_left_corner, text, width,
                            height, cell_format)

    def make_blank_cell(self, worksheet, upper_left_corner):
        """ merge cells and give blank cell format """
        self.make_text_cell(worksheet, upper_left_corner, "", 0, 0,
                            self.cell_format)

    def make_horizontal_grid(self, worksheet, upper_left_corner, name_list, blank_width):
        """ make grid where nameList is located in the first column and next columns are blanks"""
        upper_row = upper_left_corner[0]
        left_column = upper_left_corner[1]
        right_column = left_column + blank_width

        current_row = upper_row
        for name in name_list:
            self.make_title_cell(worksheet, (current_row, left_column), name, 0, 0, self.cell_left_title_format)
            # apply format to empty cells
            for col in range(left_column + 1, right_column + 1):
                self.make_blank_cell(worksheet, (current_row, col))
            current_row += 1

        used_rows = len(name_list)
        return used_rows

    def make_param_header(self, worksheet, upper_left_corner, station_name_list, title, column_title_list,
                          print_direction=True,
                          both_directions=True, blank_rows=0):
        """
        Build a block of cells with title, train directions and column titles

        :param worksheet: xlsxWritter Excel worksheet object
        :param station_name_list: list of stations to create direction names
        :param upper_left_corner: location of the block
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
        row = upper_left_corner[0]
        column = upper_left_corner[1]
        title_width = column_title_number - 1

        if print_direction and both_directions:
            title_width = 2 * column_title_number - 1

        self.make_title_cell(worksheet, (row, column), title, title_width)
        row += 1

        if print_direction:
            first_direction = station_name_list[0] + "-" + station_name_list[-1]
            second_direction = station_name_list[-1] + "-" + station_name_list[0]

            self.make_title_cell(worksheet, (row, column), first_direction, column_title_number - 1)
            if both_directions:
                self.make_title_cell(worksheet, (row, column + column_title_number), second_direction,
                                     column_title_number - 1)
            row += 1

        col = 0
        for column_title in column_title_list:
            self.make_title_cell(worksheet, (row, column + col), column_title)
            if print_direction and both_directions:
                self.make_title_cell(worksheet, (row, column + column_title_number + col),
                                     column_title)
            col += 1

        row += 1
        for index in range(blank_rows):
            length = column_title_number
            if print_direction and both_directions:
                length = 2 * column_title_number
            for col in range(0, length):
                self.make_blank_cell(worksheet, (row, column + col))
            row += 1

        used_rows = row - upper_left_corner[0]
        return used_rows

    def fit_column_width(self, worksheet, column_index, value):

        while len(self.widths) <= column_index:
            self.widths.append(0)

        width = len(value)
        if self.widths[column_index] <= width:
            self.widths[column_index] = width
            worksheet.set_column(column_index, column_index, width)


class ExcelWriter:
    """ to manage excel files """
    __metaclass__ = ABCMeta

    def __init__(self, scene):
        scene.refresh_from_db()
        self.scene = scene
        self.stringIO = BytesIO()
        self.workbook = xlsxwriter.Workbook(self.stringIO, {"in_memory": True})
        self.helper = ExcelHelper(self.workbook)

    def get_file_name(self):
        """ name of file """
        TYPE = "generic"
        EXTENSION = "xlsx"
        NAME = self.scene.name.replace(" ", "_")

        file_name = "{}_{}.{}".format(NAME, TYPE, EXTENSION)

        return file_name

    def save(self, file_field):
        """ save file in scene field """
        self.workbook.close()
        file_field.save(self.get_file_name(), ContentFile(self.stringIO.getvalue()))

    @abstractmethod
    def create_file(self, *args):
        pass


class Step1ExcelWriter(ExcelWriter):
    """ create excel file for step 2 """

    def __init__(self, scene):
        super(self.__class__, self).__init__(scene)

    def get_file_name(self):
        """ name of file """
        fileName = super(self.__class__, self).get_file_name()
        NAME = "topologico"
        fileName = fileName.replace("generic", NAME)

        return fileName

    def make_structure_header(self, worksheet):

        STRUCTURE_TITLE = "Características físicas de estaciones y túneles"
        STRUCTURE_STATION_TITLE = "Estaciones"
        STRUCTURE_TUNNEL_TITLE = "Túneles"

        STRUCTURE_STATION_SEGMENT_TITLE = "Segmento:"
        STRUCTURE_STATION_LENGTH_TITLE = "Largo [m]:"
        STRUCTURE_STATION_SURFACE_TITLE = "Superficie [m^2]:"
        STRUCTURE_STATION_PERIMETER_TITLE = "Perímetro [m]:"
        STRUCTURE_2ND_LEVEL_AVG_HEIGHT_TITLE = "Altura promedio 2do nivel [m]:"
        STRUCTURE_2ND_LEVEL_AVG_SURFACE_TITLE = "Superficie 2do nivel [m^2]:"

        worksheet.merge_range("A1:K1", STRUCTURE_TITLE, self.helper.cell_title_format)
        worksheet.merge_range("A2:F2", STRUCTURE_STATION_TITLE, self.helper.cell_title_format)
        worksheet.merge_range("H2:K2", STRUCTURE_TUNNEL_TITLE, self.helper.cell_title_format)
        worksheet.write("A3", STRUCTURE_STATION_SEGMENT_TITLE, self.helper.cell_title_format)
        worksheet.write("B3", STRUCTURE_STATION_LENGTH_TITLE, self.helper.cell_title_format)
        worksheet.write("C3", STRUCTURE_STATION_SURFACE_TITLE, self.helper.cell_title_format)
        worksheet.write("D3", STRUCTURE_STATION_PERIMETER_TITLE, self.helper.cell_title_format)
        worksheet.write("E3", STRUCTURE_2ND_LEVEL_AVG_HEIGHT_TITLE, self.helper.cell_title_format)
        worksheet.write("F3", STRUCTURE_2ND_LEVEL_AVG_SURFACE_TITLE, self.helper.cell_title_format)

        worksheet.write("H3", STRUCTURE_STATION_SEGMENT_TITLE, self.helper.cell_title_format)
        worksheet.write("I3", STRUCTURE_STATION_LENGTH_TITLE, self.helper.cell_title_format)
        worksheet.write("J3", STRUCTURE_STATION_SURFACE_TITLE, self.helper.cell_title_format)
        worksheet.write("K3", STRUCTURE_STATION_PERIMETER_TITLE, self.helper.cell_title_format)

        # fit witdh 
        texts = [
            STRUCTURE_STATION_SEGMENT_TITLE,
            STRUCTURE_STATION_LENGTH_TITLE,
            STRUCTURE_STATION_SURFACE_TITLE,
            STRUCTURE_STATION_PERIMETER_TITLE,
            STRUCTURE_2ND_LEVEL_AVG_HEIGHT_TITLE,
            STRUCTURE_2ND_LEVEL_AVG_SURFACE_TITLE,
            "space",
            STRUCTURE_STATION_SEGMENT_TITLE,
            STRUCTURE_STATION_LENGTH_TITLE,
            STRUCTURE_STATION_SURFACE_TITLE,
            STRUCTURE_STATION_PERIMETER_TITLE,
        ]
        for index, text in enumerate(texts):
            self.helper.fit_column_width(worksheet, index, text)

        used_rows = 2
        return used_rows

    def create_file(self, *args):
        """ create excel file based on scene data """

        for line in self.scene.metroline_set.all().order_by("name"):
            worksheet = self.workbook.add_worksheet(line.name)

            last_row = self.make_structure_header(worksheet)

            station_name_list = list(line.metrostation_set.values_list("name", flat=True).order_by("id"))
            height = self.helper.make_horizontal_grid(worksheet, (last_row + 1, 0),
                                                      station_name_list, 5)

            track_name_list = []
            track_name = "{}-".format(station_name_list[0])
            for name in station_name_list[1:]:
                track_name += name
                track_name_list.append(track_name)
                track_name = "{}-".format(name)
            self.helper.make_horizontal_grid(worksheet, (last_row + 1, 7), track_name_list, 3)

            last_row += height + SEPARATION_HEIGHT

            # additionHeaders
            titles = ["Pendiente", "Radio de curvatura", "Límite de velocidad",
                      "Nivel (1: sobre tierra, 0: bajo tierra)"]
            sub_titles = [
                ["Inicio de segmento [m]", "Fin de segmento [m]", "Pendiente [%]"],
                ["Inicio de segmento [m]", "Fin de segmento [m]", "Radio [m]"],
                ["Inicio de segmento [m]", "Fin de segmento [m]", "Límite [m/s]"],
                ["Inicio de segmento [m]", "Fin de segmento [m]", "Nivel"]
            ]
            both_directions = [True, True, True, False]

            for index, title in enumerate(titles):
                height = self.helper.make_param_header(worksheet, (last_row + 1, 0), station_name_list, title,
                                                       sub_titles[index], blank_rows=1,
                                                       both_directions=both_directions[index])
                last_row += height + SEPARATION_HEIGHT

        self.save(self.scene.step1Template)


class Step3ExcelWriter(ExcelWriter):
    """ create excel file for step 4 """

    def __init__(self, scene):
        super(self.__class__, self).__init__(scene)

    def get_file_name(self):
        """ name of file """
        file_name = super(self.__class__, self).get_file_name()
        NAME = "sistemico"
        file_name = file_name.replace("generic", NAME)

        return file_name

    def make_structure_header(self, worksheet):

        TITLE = "Consumo energético de estaciones, túneles y depósitos"
        STATION_TITLE = "Estaciones"
        TUNNEL_TITLE = "Túneles"
        DEPOT_TITLE = "Depósitos"

        STATION_SEGMENT_TITLE = "Estación:"
        STATION_MIN_AUX_CONSUMPTION_TITLE = "Consumo auxiliar mín [W]:"
        STATION_MAX_AUX_CONSUMPTION_TITLE = "Consumo auxiliar máx [W]:"
        STATION_MIN_HVAC_CONSUMPTION_TITLE = "Consumo HVAC mín [W]:"
        STATION_MAX_HVAC_CONSUMPTION_TITLE = "Consumo HVAC máx [W]:"
        STATION_TAU_TITLE = "Tau:"

        TRACK_SEGMENT_TITLE = "Túnel:"
        TRACK_AUX_CONSUMPTION_TITLE = "Consumo de auxiliares [W]:"
        TRACK_VENTILATION_CONSUMPTION_TITLE = "Consumo de ventilación [W]:"

        DEPOT_SEGMENT_TITLE = "Depósito:"
        DEPOT_AUX_CONSUMPTION_TITLE = "Consumo de auxiliares [W]:"
        DEPOT_VENTILATION_CONSUMPTION_TITLE = "Consumo de ventilación [W]:"
        DEPOT_DC_CONSUMPTION_TITLE = "Consumo DC [W]:"

        worksheet.merge_range("A1:O1", TITLE, self.helper.cell_title_format)
        worksheet.merge_range("A2:F2", STATION_TITLE, self.helper.cell_title_format)
        worksheet.merge_range("H2:J2", TUNNEL_TITLE, self.helper.cell_title_format)
        worksheet.merge_range("L2:O2", DEPOT_TITLE, self.helper.cell_title_format)
        worksheet.write("A3", STATION_SEGMENT_TITLE, self.helper.cell_title_format)
        worksheet.write("B3", STATION_MIN_AUX_CONSUMPTION_TITLE, self.helper.cell_title_format)
        worksheet.write("C3", STATION_MAX_AUX_CONSUMPTION_TITLE, self.helper.cell_title_format)
        worksheet.write("D3", STATION_MIN_HVAC_CONSUMPTION_TITLE, self.helper.cell_title_format)
        worksheet.write("E3", STATION_MAX_HVAC_CONSUMPTION_TITLE, self.helper.cell_title_format)
        worksheet.write("F3", STATION_TAU_TITLE, self.helper.cell_title_format)

        worksheet.write("H3", TRACK_SEGMENT_TITLE, self.helper.cell_title_format)
        worksheet.write("I3", TRACK_AUX_CONSUMPTION_TITLE, self.helper.cell_title_format)
        worksheet.write("J3", TRACK_VENTILATION_CONSUMPTION_TITLE, self.helper.cell_title_format)
        worksheet.write("L3", DEPOT_SEGMENT_TITLE, self.helper.cell_title_format)
        worksheet.write("M3", DEPOT_AUX_CONSUMPTION_TITLE, self.helper.cell_title_format)
        worksheet.write("N3", DEPOT_VENTILATION_CONSUMPTION_TITLE, self.helper.cell_title_format)
        worksheet.write("O3", DEPOT_DC_CONSUMPTION_TITLE, self.helper.cell_title_format)

        # fit witdh 
        texts = [
            STATION_SEGMENT_TITLE,
            STATION_MIN_AUX_CONSUMPTION_TITLE,
            STATION_MAX_AUX_CONSUMPTION_TITLE,
            STATION_MIN_HVAC_CONSUMPTION_TITLE,
            STATION_MAX_HVAC_CONSUMPTION_TITLE,
            STATION_TAU_TITLE,
            "space",
            TRACK_SEGMENT_TITLE,
            TRACK_AUX_CONSUMPTION_TITLE,
            TRACK_VENTILATION_CONSUMPTION_TITLE,
            "space",
            DEPOT_SEGMENT_TITLE,
            DEPOT_AUX_CONSUMPTION_TITLE,
            DEPOT_VENTILATION_CONSUMPTION_TITLE,
            DEPOT_DC_CONSUMPTION_TITLE
        ]
        for index, text in enumerate(texts):
            self.helper.fit_column_width(worksheet, index, text)

        used_rows = 2
        return used_rows

    def create_file(self, *args):
        """ create excel file based on scene data """

        for line in self.scene.metroline_set.all().order_by("name"):
            worksheet = self.workbook.add_worksheet(line.name)

            last_row = self.make_structure_header(worksheet)

            station_name_list = line.metrostation_set.values_list("name", flat=True).order_by("id")
            station_height = self.helper.make_horizontal_grid(worksheet, (last_row + 1, 0),
                                                              station_name_list, 5)

            track_name_list = []
            track_name = "{}-".format(station_name_list[0])
            for name in station_name_list[1:]:
                track_name += name
                track_name_list.append(track_name)
                track_name = "{}-".format(name)
            self.helper.make_horizontal_grid(worksheet, (last_row + 1, 7), track_name_list, 2)

            depot_name_list = line.metrodepot_set.values_list("name", flat=True)
            depot_height = self.helper.make_horizontal_grid(worksheet, (last_row + 1, 11),
                                                            depot_name_list, 3)

            last_row += max(station_height, depot_height) + SEPARATION_HEIGHT

            # additionHeaders
            title = "Características SESS de la línea"
            self.helper.make_title_cell(worksheet, (last_row + 1, 0), title, 1)

            sub_titles = [
                "Usable energy content [Wh]:",
                "Charging Efficiency [%]:",
                "Discharging Efficiency [%]:",
                "Peak power [W]:",
                "Maximum energy saving possible per hour [W]:",
                "Energy saving mode (1 = true / 0 = false):",
                "Power limit to feed [W]:"
            ]
            self.helper.make_horizontal_grid(worksheet, (last_row + 2, 0), sub_titles, 1)

        self.save(self.scene.step3Template)


class Step5ExcelWriter(ExcelWriter):
    """ create excel file for step 5 """

    def __init__(self, scene):
        super(self.__class__, self).__init__(scene)

    def get_file_name(self):
        """ name of file """
        file_name = super(self.__class__, self).get_file_name()
        NAME = "operación"
        file_name = file_name.replace("generic", NAME)

        return file_name

    def create_file(self, *args):
        """ create excel file based on scene data """

        periods_name_list = list(self.scene.operationperiod_set.values_list("name", flat=True).order_by("id"))

        for line in self.scene.metroline_set.all().order_by("name"):
            worksheet = self.workbook.add_worksheet(line.name)
            station_name_list = list(line.metrostation_set.values_list("name", flat=True).order_by("id"))

            track_name_list = []
            track_name = "{}-".format(station_name_list[0])
            for name in station_name_list[1:]:
                track_name += name
                track_name_list.append(track_name)
                track_name = "{}-".format(name)

            last_row = 0

            title = "Pasajeros en estación"
            column_title_list = ["Estación/período"] + periods_name_list
            last_row += self.helper.make_param_header(worksheet, (last_row, 0), station_name_list, title,
                                                      column_title_list)
            self.helper.make_horizontal_grid(worksheet, (last_row, 0), station_name_list, len(periods_name_list))
            last_row += self.helper.make_horizontal_grid(worksheet, (last_row, 1 + len(periods_name_list)),
                                                         station_name_list[::-1], len(periods_name_list))

            last_row += SEPARATION_HEIGHT

            title = "Pasajeros viajando entre estaciones"
            column_title_list = ["Túnel / Período"] + periods_name_list
            last_row += self.helper.make_param_header(worksheet, (last_row, 0), station_name_list, title,
                                                      column_title_list)
            self.helper.make_horizontal_grid(worksheet, (last_row, 0), track_name_list, len(periods_name_list))
            last_row += self.helper.make_horizontal_grid(worksheet, (last_row, 1 + len(periods_name_list)),
                                                         track_name_list[::-1], len(periods_name_list))

            last_row += SEPARATION_HEIGHT

            title = "Máximo tiempo permitido de viaje entre dos estaciones [s]"
            column_title_list = ["Túnel / Período"] + periods_name_list
            last_row += self.helper.make_param_header(worksheet, (last_row, 0), station_name_list, title,
                                                      column_title_list)
            self.helper.make_horizontal_grid(worksheet, (last_row, 0), track_name_list, len(periods_name_list))
            last_row += self.helper.make_horizontal_grid(worksheet, (last_row, 1 + len(periods_name_list)),
                                                         track_name_list[::-1], len(periods_name_list))

            last_row += SEPARATION_HEIGHT

            title = "Tiempo de permanencia en estación [s]"
            column_title_list = ["Estación / Período"] + periods_name_list
            last_row += self.helper.make_param_header(worksheet, (last_row, 0), station_name_list, title,
                                                      column_title_list)
            self.helper.make_horizontal_grid(worksheet, (last_row, 0), station_name_list, len(periods_name_list))
            last_row += self.helper.make_horizontal_grid(worksheet, (last_row, 1 + len(periods_name_list)),
                                                         station_name_list[::-1], len(periods_name_list))

            last_row += SEPARATION_HEIGHT

            title = "Frecuencia de trenes"
            column_title_list = ["Período:"] + periods_name_list
            frequency_list = ["Frecuencia [trenes/hora]"]
            last_row += self.helper.make_param_header(worksheet, (last_row, 0), station_name_list, title,
                                                      column_title_list)
            self.helper.make_horizontal_grid(worksheet, (last_row, 0), frequency_list, len(periods_name_list))
            last_row += self.helper.make_horizontal_grid(worksheet, (last_row, 1 + len(periods_name_list)),
                                                         frequency_list, len(periods_name_list))

            last_row += SEPARATION_HEIGHT

            title = "Porcentaje de perdida"
            column_title_list = ["Período:"] + periods_name_list
            param_list = ["Percentage DC distribution Losses:",
                          "Percentage AC substation Losses (feed entire system):",
                          "Percentage AC substation Losses (feed AC elements):",
                          "Percentage DC substation Losses:"]
            last_row += self.helper.make_param_header(worksheet, (last_row, 0), station_name_list, title,
                                                      column_title_list)
            self.helper.make_horizontal_grid(worksheet, (last_row, 0), param_list, len(periods_name_list))
            last_row += self.helper.make_horizontal_grid(worksheet, (last_row, 1 + len(periods_name_list)),
                                                         param_list,
                                                         len(periods_name_list))

            last_row += SEPARATION_HEIGHT

            title = "Receptivity of the line [%]:"
            column_title_list = ["Período:"] + periods_name_list
            last_row += self.helper.make_param_header(worksheet, (last_row, 0), station_name_list, title,
                                                      column_title_list,
                                                      print_direction=False)
            last_row += self.helper.make_horizontal_grid(worksheet, (last_row, 0), ["Receptivity [%]"],
                                                         len(periods_name_list))

            last_row += SEPARATION_HEIGHT

            title = "Flujo de ventilación [m^3/s]"
            column_title_list = ["Estación / Período"] + periods_name_list
            last_row += self.helper.make_param_header(worksheet, (last_row, 0), station_name_list, title,
                                                      column_title_list,
                                                      print_direction=False)
            last_row += self.helper.make_horizontal_grid(worksheet, (last_row, 0), station_name_list,
                                                         len(periods_name_list))

        self.save(self.scene.step5Template)


class Step6ExcelWriter(ExcelWriter):
    """ create excel file for step 6 """

    def __init__(self, scene):
        super(self.__class__, self).__init__(scene)

    def get_file_name(self):
        """ name of file """
        file_name = super(self.__class__, self).get_file_name()
        NAME = "velocidad_entrada"
        file_name = file_name.replace("generic", NAME)

        return file_name

    def create_file(self, *args):
        """ create excel file based on scene data """
        WORKSHEET_NAME = "Speed"
        DESCRIPTION = "Descripción"
        LINE_DESCRIPTION = "Línea"
        OP_DESCRIPTION = "Período operación"
        TRACK_DESCRIPTION = "Túnel"

        ATTR_NAMES = ["Distancia [m]", "Velocidad [m/s]"]

        line_objs = self.scene.metroline_set.all().order_by("name")
        operation_periods = self.scene.operationperiod_set.all().order_by("id")

        worksheet = self.workbook.add_worksheet(WORKSHEET_NAME)

        first_column_index = 0
        first_row_index = 0

        current_row = first_row_index
        current_column = first_column_index

        # header
        corner = (current_row, first_column_index)
        self.helper.make_title_cell(worksheet, corner, DESCRIPTION, width=2)
        current_row += 1
        for description in [LINE_DESCRIPTION, OP_DESCRIPTION, TRACK_DESCRIPTION]:
            corner = (current_row, current_column)
            self.helper.make_title_cell(worksheet, corner, description)
            current_column += 1
        current_row += 1

        for line_index, line_obj in enumerate(line_objs):
            track_objs = line_obj.metrotrack_set.all().order_by("id")

            track_objs_reversed = reversed(track_objs)
            for op_index, operation_period in enumerate(operation_periods):
                for direction, track_objs in zip([MetroLineMetric.GOING, MetroLineMetric.REVERSE],
                                                 [track_objs, track_objs_reversed]):
                    worksheet.write(current_row, 0, line_obj.name)
                    worksheet.write(current_row, 1, operation_period.name)

                    for track_index, track_obj in enumerate(track_objs):
                        current_column = 4
                        track_name = track_obj.get_name(direction=direction)
                        worksheet.write(current_row, 2, track_name)

                        for index, attr_name in enumerate(ATTR_NAMES):
                            worksheet.write(current_row + index, 3, attr_name)

                        values = range(int(track_obj.length) + 1)

                        for distance, value in enumerate(values):
                            worksheet.write(current_row, current_column, distance)
                            worksheet.write(current_row + 1, current_column, None)
                            current_column += 1

                        current_row += 3

        self.save(self.scene.step6Template)
