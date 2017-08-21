# -*- coding: utf-8 -*-
from django.db import models

from scene.models import Scene


class Model(models.Model):
    """ math models used by osiris web platform """
    name = models.CharField('Nombre', max_length=100)
    clusterFile = models.CharField('archivo bash', max_length=100)

    def get_dictionary(self):
        """  """
        dictionary = {
            "name": self.name,
            "id": self.id,
            "follow": [{"name": c.follow.name, "id": c.follow.id} for c in self.start_set.all().order_by("id")]
        }
        return dictionary

class PossibleQueue(models.Model):
    """ define which models can run after one model """
    start = models.ForeignKey(Model, on_delete=models.CASCADE, related_name="start_set")
    follow = models.ForeignKey(Model, on_delete=models.CASCADE, related_name="follow_set")

class ModelExecutionHistory(models.Model):
    """  record history of models execution """
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    model = models.ForeignKey(Model, on_delete=models.CASCADE)
    start = models.DateTimeField('Tiempo de inicio', null=False)
    end = models.DateTimeField('Tiempo de fin', null=True)
    answer = models.TextField()
    # answer given by executed model in CMM cluster
    OK = 'ok'
    RUNNING = 'running'
    ERROR = 'error'
    CANCEL = 'cancel'
    STATUS = (
        (RUNNING, 'En ejecución'),
        (OK, 'Terminado exitosamente'),
        (ERROR, 'Terminado con error'),
        (CANCEL, 'Cancelado por el usuario'),
    )
    status = models.CharField('Estado', max_length=40, choices=STATUS, default=RUNNING)
    """
    Cluster data
    """
    jobNumber = models.BigIntegerField(null=True)

    def __str__(self):
        return u"{} {} {}".format(self.model, self.start, self.end, self.start)

    def get_dictionary(self):
        """  """
        dictionary = {
            "start": self.start,
            "end": self.end,
            "status": self.status,
            "queuedModels": [m.get_dictionary for m in self.modelexecutionhistory_set.all().order_by("id")]
        }

        if self.end is not None:
            dictionary["duration"] = self.end - self.start

        return dictionary


class ModelExecutionQueue(models.Model):
    """  record history of models execution """
    modelExecutionHistory = models.ForeignKey(ModelExecutionHistory, on_delete=models.CASCADE)
    model = models.ForeignKey(Model, on_delete=models.CASCADE)

    def get_dictionary(self):
        """  """
        return self.model.get_dictionary()