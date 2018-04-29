from __future__ import unicode_literals
from django.utils import timezone
from django.core.files.base import ContentFile
from django.utils.translation import ugettext as _

from io import BytesIO

from cmmmodel.transform.processData import ProcessData
from cmmmodel.models import CMMModel
from scene.views.ExcelWriter import ExcelHelper
from energycentermodel.models import Resultados_Branch, Resultados_Elementos_DC, Resultados_Terminales
from energycentermodel.save_data import saveACresults, saveDCresults

import xlsxwriter
import numpy as np


class ProcessEnergyCenterData(ProcessData):
    dictionary_group = {
        "heatAbsorvedByTheGroundOnTheStations": _("Heat absorved by the ground on the stations"),
        "heatLossesFromTraction": _("Heat losses from traction"),
        "heatLossesFromPassengersOnStations": _("Heat losses from passengers on stations"),
        "heatLossesOnStations": _("Heat losses on stations"),
        "averageTemperatureDuringTheDay": _("Average temperature during the day"),
        "averageAbsolutelyHumidityDuringTheDay": _("Average absolutely humidity during the day"),
        "averageRelativeHumidityDuringTheDay": _("Average relative humidity during the day"),
    }

    def __init__(self, execution_obj):
        super(ProcessEnergyCenterData, self).__init__(CMMModel.ENERGY_CENTER_MODEL_ID, execution_obj)

    def delete_previous_data(self):
        # delete data before insert a new one
        Resultados_Branch.objects.all().delete()
        Resultados_Elementos_DC.objects.all().delete()
        Resultados_Terminales.objects.all().delete()

    def load(self, data):
        self.delete_previous_data()

        saveACresults('Cochrane', data, 'sim1')
        # Guardar resultados de simulaciones de líneas en base de datos
        for lineaID, lineaRes in data['Lineas'].items():
            saveDCresults(lineaID, lineaRes, 'sim1')

    def create_excel_file(self, data):
        return True
        # NAMES
        file_name = _("Thermal model")
        file_extension = ".xlsx"

        string_io = BytesIO()
        workbook = xlsxwriter.Workbook(string_io, {'in_memory': True})
        excel_helper = ExcelHelper(workbook)

        line_objs = MetroLine.objects.prefetch_related('metrostation_set').filter(scene=self.scene_obj).order_by("id")
        for line_obj in line_objs:
            worksheet_name = line_obj.name
            worksheet = workbook.add_worksheet(worksheet_name)

            first_column_index = 0
            first_row_index = 0

            current_row = first_row_index
            # header
            corner = (current_row, first_column_index)
            return True
            excel_helper.make_title_cell(worksheet, corner, description, width=2)
            current_row += 2

            line_number = MetroLine.objects.filter(scene=self.scene_obj).count()
            consumptions = [
                self.get_heat_absorved_by_the_ground_on_the_stations(line_number, data),
                self.get_train_consumption(line_number, data),
                self.get_track_consumption(line_number, data),
                self.get_station_consumption(line_number, data),
                self.get_depot_consumption(line_number, data)
            ]

            titles = [
                self.dictionary_group["totalConsumption"],
                self.dictionary_group["trainConsumption"],
                self.dictionary_group["trackConsumption"],
                self.dictionary_group["stationConsumption"],
                self.dictionary_group["depotConsumption"]
            ]

            for title, (names, values) in zip(titles, consumptions):

                excel_helper.make_title_cell(worksheet, (current_row, 0), title, width=2)
                current_row += 1

                for current_column, label in enumerate([item, unit, percentage]):
                    corner = (current_row, current_column)
                    excel_helper.make_title_cell(worksheet, corner, label)
                current_row += 1

                total = sum(values)
                for name, value in zip(names, values):
                    attr_name = name.split("_")[1]
                    perc = value / total if total != 0 else 0

                    worksheet.write(current_row, 0, attr_name)
                    worksheet.write(current_row, 1, value)
                    worksheet.write(current_row, 2, perc)

                    excel_helper.fit_column_width(worksheet, 0, attr_name)
                    excel_helper.fit_column_width(worksheet, 1, str(value))
                    excel_helper.fit_column_width(worksheet, 2, str(perc))

                    current_row += 1

                current_row += 1

        workbook.close()
        now = timezone.now().replace(microsecond=0)
        self.execution_obj.timestampFile = now
        self.execution_obj.downloadFile.save("{}_{}{}".format(file_name, now, file_extension),
                                             ContentFile(string_io.getvalue()))

    def get_heat_absorved_by_the_ground_on_the_stations(self, line_index, data):

        qg = data['TM']['lines'][line_index]['Qg']
        temp = data['TM']['lines'][line_index]['Temp']
        dz = data['TM']['lines'][line_index]['dz']
        Ndz = data['TM']['lines'][line_index]['Ndz']
        # Ndz1 = data['TM']['lines'][k]['Ndz1']
        # h = data['TM']['lines'][k]['h']
        r = data['TM']['lines'][line_index]['Rtot']
        station = data['TM']['lines'][line_index]['Station']

        result_data = np.empty(Ndz)
        for j in range(Ndz):
            if station[j] == 0:
                result_data[j] = 0
            else:
                result_data[j] = np.sum(qg[:, j]) - np.sum(temp[:, j] / r[j])

        x = np.array(range(Ndz)) * dz
        y = result_data * 2.77778e-7  # J to kWh

        return x, y

    def get_heat_losses_from_traction(self, line_index, data):

        qt = data['TM']['lines'][line_index]['Qt']
        dz = data['TM']['lines'][line_index]['dz']
        Ndz = data['TM']['lines'][line_index]['Ndz']
        Ndz1 = data['TM']['lines'][line_index]['Ndz1']
        h = data['TM']['lines'][line_index]['h']

        d0 = np.empty(Ndz)
        d1 = np.sum(qt, axis=0)
        aux = 0
        for j in range(Ndz1):
            if h[j] != -1:
                d0[aux] = d1[j]
                aux = + 1

        x = np.array(range(Ndz)) * dz
        y = d0 * 2.77778e-7  # J to kWh

        return x, y

    def get_heat_losses_from_passengers_on_stations(self, line_index, data):

        # qpas = data['TM']['lines'][line_index]['Qpas']
        dz = data['TM']['lines'][line_index]['dz']
        ndz = data['TM']['lines'][line_index]['Ndz']
        ndz1 = data['TM']['lines'][line_index]['Ndz1']
        h = data['TM']['lines'][line_index]['h']
        time = data['TM']['lines'][line_index]['time']
        sum_st = data['TM']['lines'][line_index]['sumSt']
        temp = data['TM']['lines'][line_index]['Temp']
        station = data['TM']['lines'][line_index]['Station']
        nst = max(station)
        thermal_in = data['EM']['Thermal_in']
        en_ps_st = thermal_in[line_index][:, 3 + 2 * nst:4 + 3 * nst - 1]

        t1 = []
        for t in range(len(en_ps_st[:, 0])):
            if t in time:
                t1.append(t)

        d = np.zeros([len(time), ndz])
        for j in range(ndz1):
            if h[j] == -1:
                j1 = int(h[j + 1])
                s = int(station[j1] - 1)
                d[:, j1] = en_ps_st[t1, s] * (-3.6517 * temp[:, j] + 168.15) / sum_st[s]
            else:
                if h[j - 1] == -1:
                    j1 = int(h[j])
                    d[:, j1] = en_ps_st[t1, int(station[j1] - 1)] * (
                            -3.6517 * temp[:, j] + 168.15) / sum_st[int(station[j1] - 1)]

        dt = np.append(0, np.diff(time))
        d2 = np.dot(np.transpose(d), dt)

        x = np.array(range(ndz)) * dz
        y = d2 * 2.77778e-7  # j to kWh

        return x, y

    def get_heat_losses_on_stations(self, line_index, data):

        qst = data['TM']['lines'][line_index]['Qst']
        dz = data['TM']['lines'][line_index]['dz']
        ndz = data['TM']['lines'][line_index]['Ndz']
        ndz1 = data['TM']['lines'][line_index]['Ndz1']
        h = data['TM']['lines'][line_index]['h']

        d0 = np.empty(ndz)
        d1 = np.sum(qst, axis=0)
        aux = 0
        for j in range(ndz1):
            if h[j] != -1:
                d0[aux] = d1[j]
                aux = + 1

        x = np.array(range(ndz)) * dz
        y = d0 * 2.77778e-7 * 2  # j to kWh

        return x, y

    def get_average_temperature_during_the_day(self, line_index, data):

        data1 = data['TM']['lines'][line_index]['tables'][0][0]
        data2l = data['TM']['lines'][line_index]['tables'][0][1]

        cell_text = np.around(data1, decimals=2)
        cell_text2l = np.around(data2l, decimals=2)

        return cell_text, cell_text2l

    def get_average_absolutely_humidity_during_the_day(self, line_index, data):

        data1 = data['TM']['lines'][line_index]['tables'][1][0]
        data2l = data['TM']['lines'][line_index]['tables'][1][1]

        cell_text = np.around(data1, decimals=5)
        cell_text2l = np.around(data2l, decimals=5)

        return cell_text, cell_text2l

    def get_average_relative_humidity_during_the_day(self, line_index, data):

        data1 = data['TM']['lines'][line_index]['tables'][2][0]
        data2l = data['TM']['lines'][line_index]['tables'][2][1]

        cell_text = np.around(data1, decimals=5)
        cell_text2l = np.around(data2l, decimals=5)

        return cell_text, cell_text2l
