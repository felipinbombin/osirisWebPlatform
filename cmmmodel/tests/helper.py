from django.urls import reverse


class APIHelper(object):

    def __init__(self, test_helper, scene_obj, model_id):
        self.test_helper = test_helper
        self.scene_obj = scene_obj
        self.model_id = model_id

    def get_model_status(self):
        """ ask for model status through url """
        status_url = reverse("cmmmodel:status")
        data = {
            "scene_id": self.scene_obj.id
        }
        return self.test_helper.make_get_request(status_url, data, expected_response=None)

    def run_test_model(self, expected_response=None):
        """  """
        run_url = reverse("cmmmodel:run")
        data = {
            "scene_id": self.scene_obj.id,
            "model_id": self.model_id
        }

        return self.test_helper.make_post_request(run_url, data, expected_response=expected_response)

    def stop_test_model(self, expected_response=None):
        """  """
        stop_url = reverse("cmmmodel:stop")
        data = {
            "scene_id": self.scene_obj.id,
            "model_id": self.model_id
        }

        return self.test_helper.make_post_request(stop_url, data, expected_response=expected_response)
