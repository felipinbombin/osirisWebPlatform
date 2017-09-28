from django.test import TestCase
from django.utils import timezone

from mock import Mock
from io import BytesIO

from cmmmodel.cron.checkExecutionStatus import check_execution_is_running
from cmmmodel.models import ModelExecutionHistory
from scene.tests.testHelper import TestHelper

import paramiko
import uuid


class CheckExecutionStatusTest(TestCase):
    fixtures = ['models', 'test_model', 'possibleQueue']

    def setUp(self):
        """
            create user and log in
        """
        self.testHelper = TestHelper(self)

        self.client = self.testHelper.get_logged_client()

        # create scene
        self.scene_name = "Escenario 1"
        self.scene_obj = self.testHelper.create_scene(self.scene_name)

        # create paramiko mock
        self.client = paramiko.SSHClient()
        self.client.exec_command = Mock(name="exec_command")

    def test_CheckWithoutExecutionIsRunning(self):
        """  """
        check_execution_is_running(self.client)

    def test_FirstCallToParamikoWithError(self):
        """ simulate that squeue command return error """
        self.client.exec_command.side_effect = [(None, BytesIO(b"out1"), BytesIO(b"err1"))]

        # create execution with state running
        external_id = uuid.uuid4()
        ModelExecutionHistory.objects.create(scene=self.scene_obj, model_id=1, externalId=external_id,
                                             start=timezone.now(), status=ModelExecutionHistory.RUNNING)

        check_execution_is_running(self.client)

    def test_CheckJobsId(self):
        """   """
        # job numbers active on cmm cluster
        squeue = b"title\n1\n2\n3"
        self.client.exec_command.side_effect = [(None, BytesIO(squeue), BytesIO(b"")), # check squeue
                                                (None, BytesIO(squeue), BytesIO(b"")), # check squeue
                                                (None, BytesIO(b"ok1"), BytesIO(b"")),
                                                (None, BytesIO(b""), BytesIO(b"")),
                                                (None, BytesIO(b""), BytesIO(b"")), # check squeue
                                                (None, BytesIO(b""), BytesIO(b"")), # check squeue
                                                (None, BytesIO(b""), BytesIO(b"")),
                                                (None, BytesIO(b""), BytesIO(b"error")),
                                                (None, BytesIO(b""), BytesIO(b"")),
                                                (None, BytesIO(b""), BytesIO(b"error"))
                                                ]

        # create execution with state running
        job_numbers = [1, 2, 4]
        for jobNumber in job_numbers:
            external_id = uuid.uuid4()
            ModelExecutionHistory.objects.create(scene=self.scene_obj, model_id=1, externalId=external_id,
                                                 start=timezone.now(), status=ModelExecutionHistory.RUNNING,
                                                 jobNumber=jobNumber)

        # first check
        check_execution_is_running(self.client)

        expected_values = [0, 0, 1]
        for expected_value, job_number in zip(expected_values, job_numbers):
            self.assertEqual(ModelExecutionHistory.objects.get(jobNumber=job_number).check_answer, expected_value)

        # second check
        check_execution_is_running(self.client)

        expected_values = [0, 0, 2]
        for expected_value, job_number in zip(expected_values, job_numbers):
            self.assertEqual(ModelExecutionHistory.objects.get(jobNumber=job_number).check_answer, expected_value)

        expected_values = ["", "", "ok1"]
        for expected_value, job_number in zip(expected_values, job_numbers):
            self.assertEqual(ModelExecutionHistory.objects.get(jobNumber=job_number).std_out, expected_value)

        # third check, jobs 1 and 2 summarize one
        check_execution_is_running(self.client)

        expected_values = [1, 1, 2]
        for expected_value, job_number in zip(expected_values, job_numbers):
            self.assertEqual(ModelExecutionHistory.objects.get(jobNumber=job_number).check_answer, expected_value)

        # third check, jobs 1 and 2 summarize one again, but there is error in jobs 1 and 2
        check_execution_is_running(self.client)

        expected_values = [1, 1, 2]
        for expected_value, job_number in zip(expected_values, job_numbers):
                self.assertEqual(ModelExecutionHistory.objects.get(jobNumber=job_number).check_answer, expected_value)
