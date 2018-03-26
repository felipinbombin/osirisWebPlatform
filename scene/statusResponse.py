# -*- coding: utf-8 -*-
from __future__ import unicode_literals


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
    MODEL_INPUT_DOES_NOT_EXIST_ERROR = 411
    INCOMPLETE_SCENE_ERROR = 412
    LAST_MODEL_ANSWER_DATA_DOES_NOT_EXISTS_ERROR = 413
    LAST_MODEL_FINISHED_BADLY_ERROR = 414
    PREVIOUS_MODEL_DID_NOT_FINISH_WELL = 415
    GENERIC_ERROR = 499

    statusDict = {
        LAST_MODEL_FINISHED_BADLY_ERROR: {
            "code": LAST_MODEL_FINISHED_BADLY_ERROR, "title": "Última ejecución con problemas",
            "message": "La última ejecución del modelo no terminó correctamente o está en ejecución.",
            "type": "error"
        },
        LAST_MODEL_ANSWER_DATA_DOES_NOT_EXISTS_ERROR: {
            "code": LAST_MODEL_ANSWER_DATA_DOES_NOT_EXISTS_ERROR, "title": "Sin resultados",
            "message": "No hay resultados disponibles para el modelo.",
            "type": "warning"
        },
        INCOMPLETE_SCENE_ERROR: {
            "code": INCOMPLETE_SCENE_ERROR, "title": "Escenario incompleto",
            "message": "El escenario debe ser completado antes de poder ejecutar el modelo.",
            "type": "error"
        },
        MODEL_INPUT_DOES_NOT_EXIST_ERROR: {
            "code": MODEL_INPUT_DOES_NOT_EXIST_ERROR, "title": "Modelo sin datos de entrada",
            "message": "No existe entrada para correr el modelo. Debe ejecutar los modelos previos.",
            "type": "error"
        },
        MODEL_EXECUTION_DOES_NOT_EXIST_ERROR: {
            "code": MODEL_EXECUTION_DOES_NOT_EXIST_ERROR, "title": "Problema al detener modelo",
            "message": "La ejecución del modelo ya finalizó o fue detenido por otro usuario.",
            "type": "error"
        },
        MODEL_IS_RUNNING_ERROR: {
            "code": MODEL_IS_RUNNING_ERROR, "title": "Modelo en ejecución",
            "message": "El modelo se encuentra en ejecución. Si desea iniciarlo nuevamente debe detener la ejecución actual.",
            "type": "error"
        },
        ENQUEUED_MODEL_ERROR: {
            "code": ENQUEUED_MODEL_ERROR, "title": "Modelo encolado actualmente",
            "message": "El modelo ya se encuentra encolado en el sistema. Debe esperar que el modelo en ejecución termine o detenerlo.",
            "type": "error"
        },
        SCENE_DOES_NOT_EXIST_ERROR: {
            "code": SCENE_DOES_NOT_EXIST_ERROR, "title": "Escenario no existe",
            "message": "El escenario no existe en el sistema.", "type": "error"
        },
        SUCCESS_NEW_NAME: {
            "code": SUCCESS_NEW_NAME, "title": "Cambio exitoso",
            "message": "El nombre ha sido actualizado exitosamente.", "type": "success"
        },
        GENERIC_ERROR: {
            "code": GENERIC_ERROR, "title": "Error",
            "message": "error genérico", "type": "error"
        },
        OK: {
            "code": OK, "title": "Consulta exitosa",
            "message": ":-)", "type": "success"
        },
        INVALID_SIZE_FILE_ERROR: {
            "code": INVALID_SIZE_FILE_ERROR, "title": "Tamaño de archivo no válido",
            "message": "El archivo ha superado el espacio permitido", "type": "error"
        },
        INVALID_STEP_ERROR: {
            "code": INVALID_STEP_ERROR, "title": "Paso no permitido",
            "message": "Debe completar los pasos previos", "type": "error"
        },
        INVALID_FORMAT_FILE_ERROR: {
            "code": INVALID_FORMAT_FILE_ERROR, "title": "Formato de archivo no válido",
            "message": "El archivo debe tener formato Excel", "type": "error"
        },
        EXCEL_ERROR: {
            "code": EXCEL_ERROR, "title": "Error al procesar archivo",
            "message": "error description", "type": "error"
        },
        INVALID_SCENE_NAME_ERROR: {
            "code": INVALID_SCENE_NAME_ERROR, "title": "Error",
            "message": "Nombre de escenario no válido", "type": "error"
        },
        USER_NOT_LOGGED_ERROR: {
            "code": USER_NOT_LOGGED_ERROR, "title": "Error",
            "message": "Debe iniciar sesión nuevamente", "type": "error"
        },
        PREVIOUS_MODEL_DID_NOT_FINISH_WELL: {
            "code": PREVIOUS_MODEL_DID_NOT_FINISH_WELL, "title": "Error",
            "message": "La ejecución del modelo previo no terminó bien. Debe corregir el problema antes de continuar.",
            "type": "error"
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
