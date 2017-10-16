# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from datetime import timedelta

from scene.models import Scene


class Model(models.Model):
    """ math models used by osiris web platform """
    name = models.CharField('Nombre', max_length=100)
    clusterExecutionId = models.CharField('archivo bash', max_length=100)
    vizURL = models.CharField(max_length=100)

    SPEED_MODEL_ID = 1
    STRONG_MODEL_ID = 2
    ENERGY_MODEL_ID = 3
    TEMPERATURE_MODEL_ID = 4

    def get_dictionary(self):
        """  """
        dictionary = {
            "name": self.name,
            "id": self.id,
            "vizURL": self.vizURL,
            "follow": [{"name": c.follow.name, "id": c.follow.id} for c in self.start_set.all().order_by("id")]
        }
        return dictionary

    def __unicode__(self):
        return self.name


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
    # answer given by executed model in CMM cluster
    OK = 'ok'
    RUNNING = 'running'
    ERROR = 'error'
    ERROR_TO_START = 'error to start'
    ERROR_TO_COMMUNICATE_ANSWER = "cluster didn't send answer"
    CANCEL = 'cancel'
    STATUS = (
        (RUNNING, 'En ejecución'),
        (OK, 'Terminado exitosamente'),
        (ERROR, 'Terminado con error'),
        (ERROR_TO_START, 'Error al iniciar'),
        (CANCEL, 'Cancelado por el usuario'),
        (ERROR_TO_COMMUNICATE_ANSWER, 'Clúster no informó respuesta')
    )
    status = models.CharField('Estado', max_length=40, choices=STATUS, default=RUNNING)
    check_answer = models.IntegerField('', default=0)
    # used by crontab to save the number of time that execution has been checked before to change state to
    # ERROR_TO_COMMUNICATE_ANSWER
    """
    Cluster data
    """
    jobNumber = models.BigIntegerField(null=True, unique=True)
    std_out = models.TextField()
    # to save error messages
    std_err = models.TextField()
    externalId = models.UUIDField(null=False)
    answer = models.FileField(upload_to='modelOutput/', null=True)

    """
    download file data
    """
    timestampFile = models.DateTimeField(null=True, default=None)
    downloadFile = models.FileField(upload_to='modelOutputFile/', null=True)

    def __unicode__(self):
        return "{} {} {}".format(self.model, timezone.localtime(self.start), timezone.localtime(self.end))

    def get_dictionary(self):
        """  """
        status = [user_message for (code, user_message) in self.STATUS if self.status == code][0]
        dictionary = {
            "start": self.start,
            "end": self.end,
            "status": status,
            "id": self.externalId,
            "queuedModels": [m.get_dictionary() for m in self.modelexecutionqueue_set.all().order_by("id")]
        }

        if self.end is not None:
            duration = self.end - self.start
            dictionary["duration"] = str(duration - timedelta(microseconds=duration.microseconds))
        else:
            dictionary["duration"] = ""

        return dictionary


class ModelExecutionQueue(models.Model):
    """  record history of models execution """
    modelExecutionHistory = models.ForeignKey(ModelExecutionHistory, on_delete=models.CASCADE)
    model = models.ForeignKey(Model, on_delete=models.CASCADE)

    def get_dictionary(self):
        """  """
        return self.model.get_dictionary()
