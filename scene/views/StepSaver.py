
from abc import ABCMeta, abstractmethod
from .ExcelWriter import Step1ExcelWriter, Step3ExcelWriter, Step5ExcelWriter
from scene.models import MetroConnection, MetroLine, MetroStation, MetroDepot, MetroConnectionStation, SystemicParams, \
    OperationPeriod

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
        MetroConnectionStation.objects.filter(metroConnection__scene=self.scene).\
            update(isOld=True)

        for line in data['lines']:
            externalId = line['id']
            name = line['name']
            if externalId:
                lineObj = MetroLine.objects.get(scene=self.scene, externalId=externalId)
                lineObj.name = name
                lineObj.isOld = False
                lineObj.save()
            else:
                lineObj = MetroLine.objects.create(scene=self.scene, name=name,
                                                   externalId=uuid.uuid4())

            for station in line['stations']:
                if station['id']:
                    MetroStation.objects.filter(metroLine=lineObj, externalId=station['id']). \
                        update(name=station['name'], isOld=False)
                else:
                    MetroStation.objects.create(metroLine=lineObj, name=station['name'], externalId=uuid.uuid4())

            for depot in line['depots']:
                if depot['id']:
                    MetroDepot.objects.filter(metroLine=lineObj, externalId=depot['id']). \
                        update(name=depot['name'], isOld=False)
                else:
                    MetroDepot.objects.create(metroLine=lineObj, name=depot['name'], externalId=uuid.uuid4())

        for connection in data['connections']:
            # global connections
            externalId = connection['id']
            avgHeight = float(connection['avgHeight'])
            avgSurface = float(connection['avgSurface'])
            if externalId:
                connectionObj = MetroConnection.objects.prefetch_related('stations'). \
                    get(scene=self.scene, externalId=externalId)
                connectionObj.name = connection['name']
                connectionObj.avgHeight = avgHeight
                connectionObj.avgSurface = avgSurface
                connectionObj.isOld = False
                connectionObj.save()
            else:
                connectionObj = MetroConnection.objects.create(scene=self.scene, name=connection['name'],
                                                               avgHeight=avgHeight, avgSurface=avgSurface,
                                                               externalId=uuid.uuid4())

            for connectionStation in connection['stations']:
                station = connectionStation['station']
                line = connectionStation['line']

                if station['id']:
                    stationObj = MetroStation.objects.get(metroLine__scene=self.scene, externalId=station['id'])
                else:
                    stationObj = MetroStation.objects.get(metroLine__name=line['name'],
                                                          metroLine__scene=self.scene, name=station['name'])

                if connectionStation['id']:
                    MetroConnectionStation.objects.filter(metroConnection=connectionObj,
                                                          externalId=connectionStation['id']).update(
                        metroStation=stationObj, isOld=False)
                else:
                    MetroConnectionStation.objects.create(metroConnection=connectionObj,
                                                          metroStation=stationObj, externalId=uuid.uuid4())

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
        step1Excel = Step1ExcelWriter(self.scene)
        step1Excel.createTemplateFile()

        # create template file for step 3
        step3Excel = Step3ExcelWriter(self.scene)
        step3Excel.createTemplateFile()

        return True


class Step2Saver(StepSaver):
    """
    logic to save step 2 data
    """

    def validate(self, data):
        """ check inputs before save """
        if isinstance(data, dict):
            for key, value in data.items():
                self.validate(value)
        elif data is None:
            raise(Exception, "error")

        return True

    def save(self, data):
        super(Step2Saver, self).save(data)

        systemicParamsData = data['systemicParams']
        connections = data['connections']

        if SystemicParams.objects.filter(scene=self.scene).count() == 0:
            SystemicParams.objects.create(scene=self.scene)

        SystemicParams.objects.filter(scene=self.scene).update(**systemicParamsData)

        for connection in connections:
            MetroConnection.objects.filter(scene=self.scene, externalId=connection['id'])\
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
        step5Excel = Step5ExcelWriter(self.scene)
        step5Excel.createTemplateFile()

        return True
