# -*- coding: utf-8 -*-

class Status:
    OK = 200
    SUCCESS_NEW_NAME = 201

    INVALID_SIZE_FILE_ERROR = 401
    INVALID_STEP_ERROR = 402
    INVALID_FORMAT_FILE_ERROR = 403
    EXCEL_ERROR = 404
    INVALID_SCENE_NAME_ERROR = 405
    USER_NOT_LOGGED_ERROR = 406
    SCENE_DOES_NOT_EXIST_ERROR = 407
    ENQUEUED_MODEL_ERROR = 408
    MODEL_IS_RUNNING_ERROR = 409
    MODEL_EXECUTION_DOES_NOT_EXIST_ERROR = 410
    GENERIC_ERROR = 499

    statusDict = {
        MODEL_EXECUTION_DOES_NOT_EXIST_ERROR: {
            "code": MODEL_EXECUTION_DOES_NOT_EXIST_ERROR, "title": "Problema al detener modelo",
            "message": "La ejecución del modelo ya finalizó o fue detenido por otro usuario.",
            "type": u"error"
        },
        MODEL_IS_RUNNING_ERROR: {
            "code": MODEL_IS_RUNNING_ERROR, "title": "Modelo en ejecución",
            "message": "El modelo se encuentra en ejecución. Si desea iniciarlo nuevamente debe detener la ejecución actual.",
            "type": u"error"
        },
        ENQUEUED_MODEL_ERROR: {
            "code": ENQUEUED_MODEL_ERROR, "title": "Modelo encolado actualmente",
            "message": "El modelo ya se encuentra encolado en el sistema. Debe esperar que el modelo en ejecución termine o detenerlo.",
            "type": u"error"
        },
        SCENE_DOES_NOT_EXIST_ERROR: {
          "code": SCENE_DOES_NOT_EXIST_ERROR, "title": "Escenario no existe",
          "message": "El escenario no existe en el sistema.", "type": u"error"
        },
        SUCCESS_NEW_NAME: {
          "code": SUCCESS_NEW_NAME, "title": u"Cambio exitoso",
          "message": u"El nombre ha sido actualizado exitosamente.", "type": u"success"
        },
        GENERIC_ERROR: {
          "code": GENERIC_ERROR, "title": u"Error",
          "message": u"error genérico", "type": u"error"
        },
        OK: {
          "code": OK, "title": u"Consulta exitosa",
          "message": u":-)", "type": u"success"
        },
        INVALID_SIZE_FILE_ERROR: {
          "code": INVALID_SIZE_FILE_ERROR, "title": u"Tamaño de archivo no válido",
          "message": u"El archivo ha superado el espacio permitido", "type": u"error"
        },
        INVALID_STEP_ERROR: {
          "code": INVALID_STEP_ERROR, "title": u"Paso no permitido",
          "message": u"Debe completar los pasos previos", "type": u"error"
        },
        INVALID_FORMAT_FILE_ERROR: {
          "code": INVALID_FORMAT_FILE_ERROR, "title": u"Formato de archivo no válido",
          "message": u"El archivo debe tener formato Excel", "type": u"error"
        },
        EXCEL_ERROR: {
          "code": EXCEL_ERROR, "title": u"Error al procesar archivo",
          "message": u"error description", "type": u"error"
        },
        INVALID_SCENE_NAME_ERROR: {
            "code": INVALID_SCENE_NAME_ERROR, "title": u"Error",
            "message": u"Nombre de escenario no válido", "type": u"error"
        },
        USER_NOT_LOGGED_ERROR: {
            "code": USER_NOT_LOGGED_ERROR, "title": u"Error",
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
