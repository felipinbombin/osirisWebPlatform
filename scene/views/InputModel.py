from cmmmodel.clusterConnection import get_input_data


class InputModel:
    def __init__(self, scene_obj, model_id):
        """ constructor """
        self.model_id = model_id
        self.scene_obj = scene_obj

    def get_input(self):
        """ retrieve input data """

        input_dict = get_input_data(self.scene_obj.id, self.model_id)

        return input_dict
