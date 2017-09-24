from django.db import models

from cmmmodel.models import ModelExecutionHistory
# Create your models here.


class ModelAnswer(models.Model):
    """ model answer by execution """
    execution = models.ForeignKey(ModelExecutionHistory, on_delete=models.CASCADE)
    line = models.IntegerField()
    direction = models.CharField(max_length=1)
    operation = models.IntegerField()
    track = models.IntegerField(null=True)
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

