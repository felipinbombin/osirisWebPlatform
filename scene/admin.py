# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import quote
from django.contrib import admin
from django.utils import timezone
from django.shortcuts import redirect
from .models import Scene, MetroLine, MetroStation, MetroDepot, MetroConnection, SystemicParams

class SceneChangeList(ChangeList):
    def url_for_result(self, result):
        pk = getattr(result, self.pk_attname)
        return '/admin/scene/panel/%d' % (quote(pk))

# Register your models here.
class SceneAdmin(admin.ModelAdmin):
    #date_hierarchy = 'timeCreation'
    #fields = ('name',)
    fieldsets = (
        (None, {'fields': ('name',)}),
    )
    list_filter = []
    list_display = ('name', 'timeCreation', 'status', 'currentStep')

    def get_changelist(self, request, **kwargs):
        return SceneChangeList

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.timeCreation = timezone.now()

        """
        # metrics for systemic params
        systemic_params = {
            "Fuerzas": [
                {"order": 1, "modelName": "trainMass", "value": None, "unit": "Kg", "label":"Masa"},
                {"order": 2, "modelName": "inercialMass", "value": None, "unit": "Kg", "label":"Masa inercial"},
                {"order": 3, "modelName": "maxAcc", "value": None, "unit": "m/s<sub>2</sub>", "label":"Máxima aceleración permitida"},
                {"order": 4, "modelName": "maxStartForce", "value": None, "unit": "N", "label":"Máxima fuerza inicial permitida"},
                {"order": 5, "modelName": "maxBrakeForce", "value": None, "unit": "N", "label":"Máxima fuerza de frenado permitida"},
                {"order": 6, "modelName": "regimeChange", "value": None, "unit": "m/s", "label":"Velocidad de cambio de regimen del motor"},
                {"order": 7, "modelName": "maxPower", "value": None, "unit": "W", "label":"Potencia máxima"},
                {"order": 8, "modelName": "maxSpeed", "value": None, "unit": "m/s", "label":"Velocidad máxima permitida"},
                {"order": 9, "modelName": "Davis", "value": None, "unit": "", "label":"A"},
                {"order": 10, "modelName": "Davis", "value": None, "unit": "", "label":"B"},
                {"order": 11, "modelName": "Davis", "value": None, "unit": "", "label":"C"},
                {"order": 12, "modelName": "Davis", "value": None, "unit": "", "label":"D"},
                {"order": 13, "modelName": "Davis", "value": None, "unit": "", "label":"E"}
            ],
            "Tracción": [
                {"order": 1, "modelName": "tractEff", "value": None, "unit": "%", "label":"Eficiencia del sistema de tracción"},
                {"order": 2, "modelName": "brakeEff", "value": None, "unit": "%", "label":"Eficiencia del sistema de frenos"},
                {"order": 3, "modelName": "electBrakeT.p1", "value": None, "unit": "Km/h", "label":"Umbral de freno eléctrico"},
                {"order": 4, "modelName": "electBrakeT.p2", "value": None, "unit": "Km/h", "label":"Umbral de freno electromecánico"}
            ],
            "Estructura": [
                {"order": 1, "modelName": "trainLength", "value": None, "unit": "m", "label": "Largo"},
                {"order": 2, "modelName": "trainCars", "value": None, "unit": "", "label":"Número de carros"},
                {"order": 3, "modelName": "car_width", "value": None, "unit": "m", "label":"Ancho de carro"},
                {"order": 4, "modelName": "car_height", "value": None, "unit": "m", "label":"Altura de carro"},
                {"order": 5, "modelName": "car_thick", "value": None, "unit": "m", "label":"Espesor de paredes del carro"},
                {"order": 6, "modelName": "car_lambda", "value": None, "unit": "W/m/K", "label":"Conductividad térmica de pared del carro"},
                {"order": 7, "modelName": "car_factor", "value": None, "unit": "", "label":"Cabin Volume Factor"},
                {"order": 8, "modelName": "passenger_capacity", "value": None, "unit": "", "label":"Capacidad de pasajeros del tren"},

                {"order": 9, "modelName": "point_in", "value": None, "unit": "", "label":""},
                {"order": 10, "modelName": "point_out", "value": None, "unit": "", "label":""},
                {"order": 11, "modelName": "point_in", "value": None, "unit": "", "label":""},
                {"order": 12, "modelName": "point_out", "value": None, "unit": "", "label":""},
                {"order": 13, "modelName": "point_in", "value": None, "unit": "", "label":""},
                {"order": 14, "modelName": "point_out", "value": None, "unit": "", "label":""},
                {"order": 15, "modelName": "point_in", "value": None, "unit": "", "label":""},
                {"order": 16, "modelName": "point_out", "value": None, "unit": "", "label":""},
                {"order": 17, "modelName": "point_in", "value": None, "unit": "", "label":""},
                {"order": 18, "modelName": "point_out", "value": None, "unit": "", "label":""},

                {"order": 19, "modelName": "ExtraPowerHRS", "value": None, "unit": "W", "label":"HRS Extra Power"},
                {"order": 20, "modelName": "isOBESS", "value": None, "unit": "[0 o 1]", "label":"On Board Energy Storage System"},
                {"order": 21, "modelName": "OBESScapacity", "value": None, "unit": "[0 a 2]", "label":"Storage Capacity Weighting"}
            ],
            "Energía": [
                {"order": 1, "modelName": "trainHVACConsumption", "value": None, "unit": "W", "label": "Consumo HVAC"},
                {"order": 2, "modelName": "trainAuxConsumption", "value": None, "unit": "W", "label": "Consumo de auxiliares"},
                {"order": 3, "modelName": "trainTerminalsResistence", "value": None, "unit": "ohm", "label": "Resistencia del terminal de trenes"},
                {"order": 4, "modelName": "trainPotencial", "value": None, "unit": "V", "label": "Votaje DC de terminal de trenes"},
            ],
            "Modelo de tracción CMM": [
                {"order": 1, "modelName": "charge_eff", "value": None, "unit": "%", "label": "OBESS charge efficiency"},
                {"order": 2, "modelName": "discharge_eff", "value": None, "unit": "%", "label": "OBESS discharge efficiency"},
                {"order": 3, "modelName": "OBESS_usable", "value": None, "unit": "kWh", "label": "OBESS Usable energy content"},
                {"order": 4, "modelName": "OBESS_peak_power", "value": None, "unit": "W", "label": "Maximun discharge power"},
                {"order": 5, "modelName": "OBESS_max_saving", "value": None, "unit": "W", "label": "Maximum energy saving possible per hour"},
                {"order": 6, "modelName": "OBESS_power_limit", "value": None, "unit": "W", "label": "Power limit to feed"}
            ]
        }

        for fields, group in systemic_params.items():
            for field in fields:
                SystemicParams.objects.create(scene=obj, group=group, order=field["order"],
                                              modelName=field["modelName"], value=field["value"], unit=field["unit"],
                                              label=field["label"])
        """
        super(SceneAdmin, self).save_model(request, obj, form, change)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        
        return super(SceneAdmin, self).add_view(request, form_url, extra_context)

    def response_add(self, request, obj, post_url_continue=None):
        url = '/admin/scene/wizard/{}'.format(obj.id)
        return redirect(url)
        #return super(SceneAdmin, self).response_add(request, ibj, post_url_continue)

admin.site.register(Scene, SceneAdmin)
admin.site.register(MetroLine)
admin.site.register(MetroStation)
admin.site.register(MetroDepot)
admin.site.register(MetroConnection)
admin.site.register(SystemicParams)
