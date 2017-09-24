from django.db import models

from cmmmodel.models import ModelExecutionHistory
from scene.models import MetroLine, MetroTrack, OperationPeriod


class ModelAnswer(models.Model):
    """ model answer by execution """
    execution = models.ForeignKey(ModelExecutionHistory, on_delete=models.CASCADE)
    metroLine = models.ForeignKey(MetroLine)
    direction = models.CharField(max_length=1)
    operationPeriod = models.ForeignKey(OperationPeriod)
    metroTrack = models.ForeignKey(MetroTrack)
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

