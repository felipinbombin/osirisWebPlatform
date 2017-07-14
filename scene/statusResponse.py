# -*- coding: utf-8 -*-

class Status:
    OK = 200
    INVALID_SIZE_FILE = 401
    INVALID_STEP = 402
    INVALID_FORMAT_FILE = 403
    EXCEL_ERROR = 404

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
        EXCEL_ERROR: {
          'code': EXCEL_ERROR,
          'title': 'Error al procesar archivo',
          'message': 'error description', 'type': 'error'
        },
    }

    @staticmethod
    def getJsonStatus(code, jsonObj, title=None, message=None):
        """ return json with status and message related to code """
        status = Status.statusDict[code]
        if title is not None:
            status['title'] = title
        if message is not None:
            status['message'] = message

        jsonObj['status'] = status
 
        return jsonObj
