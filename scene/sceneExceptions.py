# -*- coding: utf-8 -*-

class OsirisException(Exception):
    """ Raised when some part of scene app does not work well """

    def __init__(self, status_response):
        """ constructor """
        self.status_response = status_response

    def __str__(self):
        return self.status_response["status"]["message"]

    def get_code(self):
        return self.status_response["status"]["code"]

    def get_title(self):
        return self.status_response["status"]["title"]

    def get_status_response(self):
        return self.status_response