# -*- coding: utf-8 -*-

class Status:
    OK = 200
    INVALID_SIZE_FILE = 401
    INVALID_STEP = 402
    INVALID_FORMAT_FILE = 403
    EXCEL_ERROR = 404
    INVALID_SCENE_NAME = 405
    USER_NOT_LOGGED = 406
    ERROR = 200

    statusDict = {
        ERROR: {
          "code": ERROR,
          "title": u"Error",
          "message": u"error genérico", "type": u"success"
        },
        OK: {
          "code": OK,
          "title": u"Consulta exitosa",
          "message": u":-)", "type": u"success"
        },
        INVALID_SIZE_FILE: {
          "code": INVALID_SIZE_FILE,
          "title": u"Tamaño de archivo no válido",
          "message": u"El archivo ha superado el espacio permitido", "type": u"error"
        },
        INVALID_STEP: {
          "code": INVALID_STEP,
          "title": u"Paso no permitido",
          "message": u"Debe completar los pasos previos", "type": u"error"
        },
        INVALID_FORMAT_FILE: {
          "code": INVALID_FORMAT_FILE,
          "title": u"Formato de archivo no válido",
          "message": u"El archivo debe tener formato Excel", "type": u"error"
        },
        EXCEL_ERROR: {
          "code": EXCEL_ERROR,
          "title": u"Error al procesar archivo",
          "message": u"error description", "type": u"error"
        },
        INVALID_SCENE_NAME: {
            "code": INVALID_SCENE_NAME,
            "title": u"Error",
            "message": u"Nombre de escenario no válido", "type": u"error"
        },
        USER_NOT_LOGGED: {
            "code": USER_NOT_LOGGED,
            "title": u"Error",
            "message": u"Debe iniciar sesión nuevamente", "type": u"error"
        }
    }

    @staticmethod
    def getJsonStatus(code, jsonObj, title=None, message=None):
        """ return json with status and message related to code """
        status = Status.statusDict[code]
        if title is not None:
            status["title"] = title
        if message is not None:
            status["message"] = message

        jsonObj["status"] = status
 
        return jsonObj
