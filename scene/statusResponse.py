# -*- coding: utf-8 -*-
from django.http import JsonResponse

class Status():
    OK = 200
    INVALID_SIZE_FILE = 401
    INVALID_STEP = 402
    INVALID_FORMAT_FILE = 403

    statusDict = {
        OK: {
          'code': OK, 
          'title': 'Consulta exitosa', 
          'message': ':-)', 'type': 'success'
        },
        INVALID_SIZE_FILE: {
          'code': INVALID_SIZE_FILE, 
          'title': 'Tamaño de archivo no válido', 
          'message': 'El archivo ha superado el espacio permitido.', 'type': 'error'
        },
        INVALID_STEP: {
          'code': INVALID_STEP, 
          'title': 'Paso no permitido', 
          'message': 'Debe completar los pasos previos.', 'type': 'error'
        },
        INVALID_FORMAT_FILE: {
          'code': INVALID_FORMAT_FILE, 
          'title': 'Formato de archivo no válido', 
          'message': 'El archivo debe tener formato Excel.', 'type': 'error'
        },
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
