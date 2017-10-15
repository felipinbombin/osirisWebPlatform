# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from .ExcelWriter import Step1ExcelWriter, Step3ExcelWriter, Step5ExcelWriter
from scene.models import MetroConnection, MetroLine, MetroStation, MetroDepot, MetroConnectionStation, SystemicParams, \
    OperationPeriod
from scene.sceneExceptions import OsirisException
from scene.statusResponse import Status

import uuid


class StepSaver:
    """
    save step data
    """
    __metaclass__ = ABCMeta

    def __init__(self, scene):
        self.scene = scene

    @abstractmethod
    def validate(self, data):
        # if found an error throw an exception with user message
        pass

    def save(self, data):
        # validate data before saved
        self.validate(data)


class Step0Saver(StepSaver):
    """
    logic to save step 0 data
    """

    def validate(self, data):
        return True

    def save(self, data):
        super(Step0Saver, self).save(data)

        # all records all old by default
        self.scene.metroline_set.update(isOld=True)
        MetroStation.objects.filter(metroLine__scene=self.scene).update(isOld=True)
        MetroDepot.objects.filter(metroLine__scene=self.scene).update(isOld=True)
        MetroConnection.objects.filter(scene=self.scene).update(isOld=True)
        MetroConnectionStation.objects.filter(metroConnection__scene=self.scene). \
            update(isOld=True)

        for line in data['lines']:
            external_id = line['id']
            name = line['name']
            if external_id:
                line_obj = MetroLine.objects.get(scene=self.scene, externalId=external_id)
                line_obj.name = name
                line_obj.isOld = False
                line_obj.save()
            else:
                line_obj = MetroLine.objects.create(scene=self.scene, name=name,
                                                    externalId=uuid.uuid4())

            for station in line['stations']:
                if station['id']:
                    MetroStation.objects.filter(metroLine=line_obj, externalId=station['id']). \
                        update(name=station['name'], isOld=False)
                else:
                    MetroStation.objects.create(metroLine=line_obj, name=station['name'], externalId=uuid.uuid4())

            for depot in line['depots']:
                if depot['id']:
                    MetroDepot.objects.filter(metroLine=line_obj, externalId=depot['id']). \
                        update(name=depot['name'], isOld=False)
                else:
                    MetroDepot.objects.create(metroLine=line_obj, name=depot['name'], externalId=uuid.uuid4())

        for connection in data['connections']:
            # global connections
            external_id = connection['id']
            avg_height = float(connection['avgHeight'])
            avg_surface = float(connection['avgSurface'])
            if external_id:
                connection_obj = MetroConnection.objects.prefetch_related('stations'). \
                    get(scene=self.scene, externalId=external_id)
                connection_obj.name = connection['name']
                connection_obj.avgHeight = avg_height
                connection_obj.avgSurface = avg_surface
                connection_obj.isOld = False
                connection_obj.save()
            else:
                connection_obj = MetroConnection.objects.create(scene=self.scene, name=connection['name'],
                                                                avgHeight=avg_height, avgSurface=avg_surface,
                                                                externalId=uuid.uuid4())

            for connection_station in connection['stations']:
                station = connection_station['station']
                line = connection_station['line']

                if station['id']:
                    station_obj = MetroStation.objects.get(metroLine__scene=self.scene, externalId=station['id'])
                else:
                    station_obj = MetroStation.objects.get(metroLine__name=line['name'],
                                                           metroLine__scene=self.scene, name=station['name'])

                if connection_station['id']:
                    MetroConnectionStation.objects.filter(metroConnection=connection_obj,
                                                          externalId=connection_station['id']).update(
                        metroStation=station_obj, isOld=False)
                else:
                    MetroConnectionStation.objects.create(metroConnection=connection_obj,
                                                          metroStation=station_obj, externalId=uuid.uuid4())

        MetroLine.objects.filter(scene=self.scene, isOld=True).delete()
        MetroStation.objects.filter(metroLine__scene=self.scene, isOld=True).delete()
        MetroDepot.objects.filter(metroLine__scene=self.scene, isOld=True).delete()
        MetroConnection.objects.filter(scene=self.scene, isOld=True).delete()
        MetroConnectionStation.objects.filter(metroConnection__scene=self.scene, isOld=True).delete()

        # move to next step
        if self.scene.currentStep == 0:
            self.scene.currentStep = 1
            self.scene.save()

        # create template file for step 1
        step1_excel = Step1ExcelWriter(self.scene)
        step1_excel.create_file()

        # create template file for step 3
        step3_excel = Step3ExcelWriter(self.scene)
        step3_excel.create_file()

        return True


class Step2Saver(StepSaver):
    """
    logic to save step 2 data
    """

    def validate(self, data, attr_name=None):
        """ check inputs before save """
        if isinstance(data, dict):
            for key, value in data.items():
                self.validate(value, key)
        if isinstance(data, list):
            for el in data:
                self.validate(el)
        elif data is None or data == "":
            response = Status.getJsonStatus(Status.EXCEL_ERROR, {})
            response["status"]["message"] = u"El valor del campo {} no puede ser vacío.".format(attr_name, data)
            raise (OsirisException(response))

        return True

    def save(self, data):
        super(Step2Saver, self).save(data)

        systemic_params_data = data['systemicParams']
        connections = data['connections']

        if SystemicParams.objects.filter(scene=self.scene).count() == 0:
            SystemicParams.objects.create(scene=self.scene)

        SystemicParams.objects.filter(scene=self.scene).update(**systemic_params_data)

        for connection in connections:
            MetroConnection.objects.filter(scene=self.scene, externalId=connection['id']) \
                .update(consumption=connection['consumption'])

        return True


class Step4Saver(StepSaver):
    """
    logic to save step 4 data
    """

    def validate(self, data):
        return True

    def save(self, data):
        super(Step4Saver, self).save(data)

        self.scene.averageMassOfAPassanger = data['averageMassOfAPassanger']
        self.scene.annualTemperatureAverage = data['annualTemperatureAverage']
        self.scene.save()

        OperationPeriod.objects.filter(scene=self.scene).update(isOld=True)

        for operationPeriod in data['operationPeriods']:
            if operationPeriod["id"]:
                OperationPeriod.objects.filter(scene=self.scene, externalId=operationPeriod["id"]).update(
                    name=operationPeriod["name"],
                    start=operationPeriod["start"],
                    end=operationPeriod["end"],
                    temperature=operationPeriod["temperature"],
                    humidity=operationPeriod["humidity"],
                    co2Concentration=operationPeriod["co2Concentration"],
                    solarRadiation=operationPeriod["solarRadiation"],
                    sunElevationAngle=operationPeriod["sunElevationAngle"],
                    isOld=False
                )
            else:
                OperationPeriod.objects.create(
                    scene=self.scene,
                    externalId=uuid.uuid4(),
                    name=operationPeriod["name"],
                    start=operationPeriod["start"],
                    end=operationPeriod["end"],
                    temperature=operationPeriod["temperature"],
                    humidity=operationPeriod["humidity"],
                    co2Concentration=operationPeriod["co2Concentration"],
                    solarRadiation=operationPeriod["solarRadiation"],
                    sunElevationAngle=operationPeriod["sunElevationAngle"]
                )
        OperationPeriod.objects.filter(scene=self.scene, isOld=True).delete()

        # create template file for step 5
        step5_excel = Step5ExcelWriter(self.scene)
        step5_excel.create_file()

        return True
