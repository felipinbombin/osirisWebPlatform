from django.test import TestCase
from cmmmodel.clusterConnection import get_paramiko_client


class ConnectionException(Exception):
    pass


class CheckConnectionStatusTest(TestCase):


    def test_ExectCommandWithRealConnection(self):
        """  """

        client = get_paramiko_client()
        command = "ls -al osiris/"
        stdin, stdout, stderr = client.exec_command(command)

        for line in stdout:
            print(line)

        for _ in stderr:
            raise ConnectionException(stderr.read())