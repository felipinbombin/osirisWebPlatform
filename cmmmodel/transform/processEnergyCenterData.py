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

from viz.models import EnergyCenterModelAnswer

import xlsxwriter
import numpy as np


class ProcessEnergyCenterData(ProcessData):
    dictionary_group = {
        # network chart
        "cdc_evol_mw": _("CDC injection evolution [MW]"),
        "cdc_evol_mvar": _("CDC injection evolution [MVAr]"),
        # line charts
        "vol_evol": _("Voltage evolution"),
        "pow_evol": _("Power evolution"),
        "losses_evol": _("Losses evolution"),
        "trains_evol": _("Train consumption evolution"),
        "ser_injection_evol": _("SERs injection evolution"),
        "pow_pv_injection_evol": _("Evolution of power given by PV"),
    }

    def __init__(self, execution_obj):
        super(ProcessEnergyCenterData, self).__init__(CMMModel.ENERGY_CENTER_MODEL_ID, execution_obj)

    def delete_previous_data(self):
        # delete data before insert a new one
        Resultados_Branch.objects.all().delete()
        Resultados_Elementos_DC.objects.all().delete()
        Resultados_Terminales.objects.all().delete()
        EnergyCenterModelAnswer.objects.filter(execution=self.execution_obj).delete()

    def load(self, data):
        self.delete_previous_data()

        saveACresults('Cochrane', data, 'sim1')
        # Guardar resultados de simulaciones de líneas en base de datos
        for line_id, line_attributes in data['Lineas'].items():
            saveDCresults(line_id, line_attributes, 'sim1')
            # save chart data
            for chart in line_attributes['graficos']:
                print(line_attributes['graficos'][chart]['x_data'])
                print(line_attributes['graficos'][chart]['y_data'])
                print("   ----")

        # data for network chart
        for chart in data['graficos']:
            for x, y in zip(data['graficos'][chart]['x_data'], data['graficos'][chart]['y_data']):
                EnergyCenterModelAnswer.objects.create(execution=self.execution_obj, attributeName=chart,
                                                       metroLine=None, via=None, order=x, value=y)

    """
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
    """
