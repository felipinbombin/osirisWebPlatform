# -*- coding: utf-8 -*-
from django.http import JsonResponse

class Status():
    OK = 1

    statusDict = {
        OK: {'status': 200, 'title': '', 'message': 'consulta exitosa', 'type': 'success'}
    }

    @staticmethod
    def getJsonStatus(code, jsonObj, title=None, message=None):
        """ return json with status and message related to code """
        status = Status.statusDict[code]
        if title != None:
            status['title'] = title
        if message != None:
            status['message'] = message

        jsonObj.update(status)
 
        return jsonObj
