
import uuid

from abc import ABCMeta, abstractmethod
from .Excel import Step1Excel, Step3Excel
from scene.models import MetroConnection, MetroLine, MetroStation, MetroDepot, MetroConnectionStation


class StepSaver:
    """
    save step data
    """
    __metaclass__ = ABCMeta

    def __init__(self, scene):
        self.scene = scene

    @abstractmethod
    def validate(self, data):
        pass

    def save(self, data):
        self.validate(data)


class Step0Saver(StepSaver):
    """
    logic to save step 0 data
    """
    def validate(self, request):
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
        step1Excel = Step1Excel(self.scene)
        step1Excel.createTemplateFile()

        # create template file for step 3
        step3Excel = Step3Excel(self.scene)
        step3Excel.createTemplateFile()

        return True

class Step2Saver(StepSaver):
    """
    logic to save step 2 data
    """

    def validate(self, request):
        return True

    def save(self, data):
        super(Step0Saver, self).save(data)
        print data

        return True

class Step5Saver(StepSaver):
    """
    logic to save step 5 data
    """

    def validate(self, request):
        return True

    def save(self, data):
        super(Step0Saver, self).save(data)