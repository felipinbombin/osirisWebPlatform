from abc import ABCMeta, abstractmethod

from viz.models import ModelAnswer, HeatModelTableAnswer
from cmmmodel.models import Model


class ProcessData:
    __metaclass__ = ABCMeta

    def __init__(self, model_id, execution_obj):
        self.model_id = model_id
        self.execution_obj = execution_obj
        self.scene_obj = execution_obj.scene

    def delete_previous_data(self):
        # delete data before insert a new one
        ModelAnswer.objects.filter(execution__model_id=self.model_id,
                                   execution__scene=self.scene_obj).delete()
        if self.model_id == Model.THERMAL_MODEL_ID:
            HeatModelTableAnswer.objects.filter(execution__model_id=self.model_id,
                                                execution__scene=self.scene_obj).delete()

    @abstractmethod
    def load(self, data):
        pass

    @abstractmethod
    def create_excel_file(self, data):
        pass
