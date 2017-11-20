from __future__ import unicode_literals
from django.utils import timezone
from django.core.files.base import ContentFile

from io import BytesIO

from cmmmodel.transform.processData import ProcessData
from cmmmodel.models import Model
from scene.models import MetroLine
from scene.views.ExcelWriter import ExcelHelper
from viz.models import ModelAnswer

import xlsxwriter


class ProcessEnergyData(ProcessData):
    def __init__(self, execution_obj):
        super(ProcessEnergyData, self).__init__(Model.ENERGY_MODEL_ID, execution_obj)

    def load(self, data):
        self.delete_previous_data()

        line_number = MetroLine.objects.filter(scene=self.scene_obj).order_by("id").count()
        consumptions = [
            self.get_total_consumption(line_number, data),
            self.get_train_consumption(line_number, data),
            self.get_track_consumption(line_number, data),
            self.get_station_consumption(line_number, data),
            self.get_depot_consumption(line_number, data)
        ]

        for names, values in consumptions:
            for index, name, value in zip(range(len(names)), names, values):
                ModelAnswer.objects.create(execution=self.execution_obj, metroLine=None, direction=None,
                                           metroTrack=None, operationPeriod=None, attributeName=name,  order=index,
                                           value=value)

    def create_excel_file(self, data):

        # NAMES
        file_name = "Energía"
        file_extension = ".xlsx"

        worksheet_name = "Energy"
        description = "Description"
        item = "Item"
        unit = "[MWh]"
        percentage = "%"

        titles = [
            "Total consumption",
            "Trains consumption",
            "Tracks consumption",
            "Stations consumption",
            "Depots consumption",
        ]

        string_io = BytesIO()
        workbook = xlsxwriter.Workbook(string_io, {'in_memory': True})
        excel_helper = ExcelHelper(workbook)

        worksheet = workbook.add_worksheet(worksheet_name)

        first_column_index = 0
        first_row_index = 0

        current_row = first_row_index
        # header
        corner = (current_row, first_column_index)
        excel_helper.make_title_cell(worksheet, corner, description, width=2)
        current_row += 2

        line_number = MetroLine.objects.filter(scene=self.scene_obj).count()
        consumptions = [
            self.get_total_consumption(line_number, data),
            self.get_train_consumption(line_number, data),
            self.get_track_consumption(line_number, data),
            self.get_station_consumption(line_number, data),
            self.get_depot_consumption(line_number, data)
        ]

        for title, (names, values) in zip(titles, consumptions):

            excel_helper.make_title_cell(worksheet, (current_row, 0), title, width=2)
            current_row += 1

            for current_column, description in enumerate([item, unit, percentage]):
                corner = (current_row, current_column)
                excel_helper.make_title_cell(worksheet, corner, description)
            current_row += 1

            total = sum(values)
            for name, value in zip(names, values):
                attr_name = name.split("_")[1]
                percentage = value / total if total != 0 else 0

                worksheet.write(current_row, 0, attr_name)
                worksheet.write(current_row, 1, value)
                worksheet.write(current_row, 2, percentage)

                excel_helper.fit_column_width(worksheet, 0, attr_name)
                excel_helper.fit_column_width(worksheet, 1, str(value))
                excel_helper.fit_column_width(worksheet, 2, str(percentage))

                current_row += 1

            current_row += 1

        workbook.close()
        now = timezone.now().replace(microsecond=0)
        self.execution_obj.timestampFile = now
        self.execution_obj.downloadFile.save("{}_{}{}".format(file_name, now, file_extension),
                                             ContentFile(string_io.getvalue()))

    def get_total_consumption(self, line_number, data):

        t1 = 0
        s1 = 0
        tr1 = 0
        ss1 = 0
        r1 = 0

        for k in range(line_number):
            s1 += data['Stations']['Lines'][k]['E_HVAC'] + data['Stations']['Lines'][k]['E_Aux']
            tr1 += data['Tracks']['Lines'][k]['Energy'][data['thours'].seconds - 1]
            ss1 += sum(data['SS']['Lines'][k]['Energy'][-1, :])

            for s in range(2):
                t1 += data['Trains']['Lines'][k]['Energy_Trains'][s][-1, :]
                r1 += data['Trains']['Lines'][k]['Energy_Trains'][s][-1, 4]

        t2 = (sum(t1[0:3]) + t1[-1]) / 1000000
        s2 = s1 / 1000000
        tr2 = (tr1[0:1] + tr1[3]) / 1000000
        ss2 = ss1 / 1000000
        r2 = r1 / 1000000

        prefix = "totalConsumption"
        names = ["%s_trains" % prefix,
                 "%s_stations" % prefix,
                 "%s_tracks" % prefix,
                 "%s_substations" % prefix,
                 "%s_recoveredEnergy" % prefix,
                 ]
        #TODO: remove [0]
        values = [t2, s2[0], tr2[0], ss2, r2]

        return names, values

    def get_train_consumption(self, line_number, data):

        au = 0
        h = 0
        t = 0
        o = 0
        tr = 0
        ore = 0
        tl = 0

        factor = 0.000277778 / 1000
        for k in range(line_number):
            for s in range(2):
                au += data['Trains']['Lines'][k]['Energy_Trains'][s][-1, 0] * factor
                h += data['Trains']['Lines'][k]['Energy_Trains'][s][-1, 1] * factor
                t += data['Trains']['Lines'][k]['Energy_Trains'][s][-1, 2] * factor
                o += data['Trains']['Lines'][k]['Energy_Trains'][s][-1, 3] * factor
                tr += data['Trains']['Lines'][k]['Energy_Trains'][s][-1, 4] * factor
                ore += data['Trains']['Lines'][k]['Energy_Trains'][s][-1, 5] * factor
                tl += data['Trains']['Lines'][k]['Energy_Trains'][s][-1, 6] * factor

        prefix = "trainConsumption"
        names = ["%s_auxiliaries" % prefix,
                 "%s_hvac" % prefix,
                 "%s_traction" % prefix,
                 "%s_obess" % prefix,
                 "%s_tractionRecovery" % prefix,
                 "%s_obessRecovery" % prefix,
                 "%s_terminalLosses" % prefix,
                 ]
        values = [au, h, t, o, tr, ore, tl]

        return names, values

    def get_track_consumption(self, line_number, data):

        au = 0
        v = 0
        dc = 0
        se = 0
        lns = 0
        factor = 0.000277778 / 1000
        for k in range(line_number):
            au += data['Tracks']['Lines'][k]['Energy'][data['thours'].seconds - 1][0] * factor
            v += data['Tracks']['Lines'][k]['Energy'][data['thours'].seconds - 1][1] * factor
            dc += data['Tracks']['Lines'][k]['Energy'][data['thours'].seconds - 1][2] * factor
            se += data['Tracks']['Lines'][k]['Energy'][data['thours'].seconds - 1][3] * factor
            lns += data['Tracks']['Lines'][k]['Energy'][data['thours'].seconds - 1][4] * factor

        prefix = "trackConsumption"
        names = ["%s_auxiliaries" % prefix,
                 "%s_ventilation" % prefix,
                 "%s_dcDistributionLosses" % prefix,
                 "%s_dcSessLosses" % prefix,
                 "%s_noSavingCapacityLosses" % prefix
                 ]
        values = [au, v, dc, se, lns]

        return names, values

    def get_station_consumption(self, line_number, data):

        au = 0
        v = 0
        factor = 0.000277778 / 1000
        for k in range(line_number):
            au += data['Stations']['Lines'][k]['E_Aux'] * factor
            v += data['Stations']['Lines'][k]['E_HVAC'] * factor

        prefix = "stationConsumption"
        names = ["%s_auxiliaries" % prefix,
                 "%s_ventilation" % prefix
                 ]
        # TODO: remove [0]
        values = [au[0], v[0]]

        return names, values

    def get_depot_consumption(self, line_number, data):

        au = 0
        v = 0
        factor = 0.000277778 / 1000
        for k in range(line_number):
            au += data['Depots']['Lines'][k]['E_aux'] * factor
            v += data['Depots']['Lines'][k]['E_vent'] * factor

        prefix = "depotConsumption"
        names = ["%s_auxiliaries" % prefix,
                 "%s_ventilation" % prefix
                 ]
        values = [au, v]

        return names, values
