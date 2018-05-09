from django.db import models

from cmmmodel.models import ModelExecutionHistory
from scene.models import MetroLine, MetroTrack, OperationPeriod, MetroStation


class ModelAnswer(models.Model):
    """ model answer by execution """
    execution = models.ForeignKey(ModelExecutionHistory, on_delete=models.CASCADE)
    metroLine = models.ForeignKey(MetroLine, null=True)
    direction = models.CharField(max_length=1, null=True)
    operationPeriod = models.ForeignKey(OperationPeriod, null=True)
    metroTrack = models.ForeignKey(MetroTrack, null=True)
    attributeName = models.CharField(max_length=100)
    order = models.IntegerField()
    value = models.FloatField()

    """
    def get_dictionary(self):
        """  """
        dictionary = {
            "name": self.direction,
            "id": self.id,
        }
        return dictionary
    """

    def __str__(self):
        return "{}".format(self.id)

    class Meta:
        indexes = [
            models.Index(fields=['execution', 'metroLine', 'direction', 'operationPeriod', 'metroTrack']),
        ]


class HeatModelTableAnswer(models.Model):
    """ save data related to tables shown in heat model view """
    execution = models.ForeignKey(ModelExecutionHistory, on_delete=models.CASCADE)
    metroStation = models.ForeignKey(MetroStation, null=False)
    operationPeriod = models.ForeignKey(OperationPeriod, null=False)
    attributeName = models.CharField(max_length=100)
    group = models.CharField(max_length=15)  # platform_level or second_level
    value = models.FloatField()


class EnergyCenterModelAnswer(models.Model):
    """

    """
    execution = models.ForeignKey(ModelExecutionHistory, on_delete=models.CASCADE)
    metroLine = models.CharField(max_length=100)
    via = models.CharField(max_length=100)
    attributeName = models.CharField(max_length=100)
    order = models.IntegerField()
    value = models.FloatField()
