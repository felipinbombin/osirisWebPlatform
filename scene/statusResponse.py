# -*- coding: utf-8 -*-
from django.http import JsonResponse

class Status():
    OK = 1

    statusDict = {
        OK: {'code': 200, 'title': 'Consulta exitosa', 'message': ':-)', 'type': 'success'}
    }

    @staticmethod
    def getJsonStatus(code, jsonObj, title=None, message=None):
        """ return json with status and message related to code """
        status = Status.statusDict[code]
        if title != None:
            status['title'] = title
        if message != None:
            status['message'] = message

        jsonObj['status'] = status
 
        return jsonObj
