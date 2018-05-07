# -*- coding: utf-8 -*-

import warnings

from django.utils import dateparse
from django.utils.timezone import utc

from energycentermodel.models import Atributos_Terminales, Atributos_Trafos, Atributos_SAF, Atributos_CDC, \
    Atributos_PVAC, Atributos_Cables, Perfiles_PV, Perfiles_SAF, Atributos_Lineas, Atributos_Vias, Atributos_Trenes, \
    Lista_Elementos_DC, Atributos_SER, Atributos_PVdc, Bitacora_trenes


# Funcion para leer datos de atributos de objetos de red AC
def leer_atributos_ac(red_ac_id, data_dict):
    # Crear diccionario de datos para red ac
    atributos = dict()

    # Crear terminales en lado AC para red respectiva

    # Crear diccionario para datos de terminales
    term_data_dict = dict()
    query_set = Atributos_Terminales.objects.filter(Red_ID=red_ac_id)
    if query_set.exists():
        for row in query_set:
            term_data_dict[row.Term_ID] = {
                'Vnom': row.Vnom,
                'Save': row.Save
            }
        # Guardar diccionario con atributos de terminales en diccionario de datos de red AC
        atributos['TermData'] = term_data_dict
    else:
        raise ValueError(
            'No se encuentran terminales para la red especificada. No es posible construir la topología')

    # Crear transformadores de red AC

    # Obtener parametros de la vias y agregarlas a la linea creada
    # Crear diccionario para datos de terminales
    trafo_data = dict()
    results = Atributos_Trafos.objects.filter(Red_ID=red_ac_id, En_operacion=True)
    if len(results) == 0:
        raise ValueError(
            'No se encuentran transformadores para la línea especificada, no se puede construir topología')
    for row in results:
        TrafoID = row.Trafo_ID
        # Obtener ID de terminal de conexión para primario de cada trafo
        HVTermID = row.HVTerm_ID
        # Obtener ID de terminal de conexión para secundario de cada trafo
        LVTermID = row.LVTerm_ID
        # Recuperar otros atributos de trafos
        capacidad = set(row.Snom for row in results).pop()
        resistencia = set(row.Resistencia for row in results).pop()
        reactancia = set(row.Reactancia for row in results).pop()
        # Crear diccionario para datos de transformadores
        trafo_data[TrafoID] = {
            'Snom': capacidad,
            'R': resistencia,
            'X': reactancia,
            'HV': HVTermID,
            'LV': LVTermID,
            'Save': row.Save
        }

    # Guardar diccionario con atributos de trafos en diccionario de datos de red AC
    atributos['TrafoData'] = trafo_data

    # Crear SAF y conectarlos a sus respectivos terminales

    # Obtener parametros de la vias y agregarlas a la linea creada
    results = Atributos_SAF.objects.filter(Red_ID=red_ac_id, En_operacion=True)
    if len(results) == 0:
        warnings.warn('No se encuentran SAF para la línea especificada')
    else:
        # Crear diccionario para datos de SAF
        saf_data = dict()
        for row in results:
            # Obtener ID de SAF
            saf_id = row.SAF_ID
            # Obtener ID de terminal de conexión para SAF
            term_id = row.Term_ID
            consumo_id = row.Consumo_ID
            Vac = row.Vac
            capacidad = row.Snom
            # Crear diccionario para datos de SAF
            saf_data[saf_id] = {
                'Vac': Vac,
                'Snom': capacidad,
                'Consumo': consumo_id,
                'TermID': term_id
            }

        # Guardar diccionario con atributos de SAF en diccionario de datos de red AC
        atributos['SAFData'] = saf_data

    # Crear CDC de la linea

    # Obtener parametros de la vias y agregarlas a la linea creada
    results = Atributos_CDC.objects.filter(Red_ID=red_ac_id)

    if len(results) == 0:
        raise ValueError('No se encuentran CDC para la línea especificada, no se puede construir topología.')
    # Crear diccionario para datos de CDC
    CDCData = dict()
    for row in results:
        CDCID = row.CDC_ID
        # Obtener ID de terminal de conexión para SAF
        term_id = row.Term_ID
        # Recuperar otros atributos de CDC
        Vac = row.Vnom
        capacidad = row.Snom
        # Crear diccionario para datos de CDC
        CDCData[CDCID] = {
            'Vac': Vac,
            'Snom': capacidad,
            'TermID': term_id,
            'Save': row.Save
        }

    # Guardar diccionario con atributos de CDC en diccionario de datos de red AC
    atributos['CDCData'] = CDCData

    # Crear módulos PV en lado AC
    # Obtener PVAC de la línea
    try:
        # Obtener parametros de la vias y agregarlas a la linea creada
        ListaPVAC = Atributos_PVAC.objects.filter(Red_ID=red_ac_id, En_operacion=True)
        # Crear diccionario para datos de módulos PV en red ac
        PVacData = dict()
        for row in ListaPVAC:
            # Obtener ID de cada módulo
            PVACID = row.PVac_ID
            voltaje = row.Vnom
            capacidad = row.Snom
            term_id = row.Term_ID
            cosphi = row.cosphi
            PerfilPVAC = row.PerfilPV
            # Agregar PVdc sin perfil, el cual se agrega una vez se realiza la simulación filtrando por fecha
            PVacData[PVACID] = {
                'Vac': voltaje,
                'Snom': capacidad,
                'Perfil': PerfilPVAC,
                'cosphi': cosphi,
                'TermID': term_id
            }

        # Guardar diccionario con atributos de módulos PV en lado ac en diccionario de datos de red AC
        atributos['PVacData'] = PVacData
    except:
        warnings.warn('No se encontraron PV para la red especificada.')

    # Crear cables para conectar terminales de la linea

    # Obtener parametros de la vias y agregarlas a la linea creada
    results = Atributos_Cables.objects.filter(Red_ID=red_ac_id, En_operacion=True)
    if len(results) == 0:
        raise ValueError('No se encuentran cables disponibles para la línea especificada')
    # Crear diccionario para datos de cables de red ac
    CablesData = dict()
    for row in results:
        CableID = row.Cable_ID
        # Obtener ID de terminal de conexión para SAF
        Term1ID = row.Term_ID1
        Term2ID = row.Term_ID2
        # Recuperar otros atributos de cables
        largo = row.Largo
        capacidad = row.Snom
        resistencia = row.Resistencia
        reactancia = row.Reactancia
        capacitancia = row.Capacitancia
        # Agregar cable
        CablesData[CableID] = {
            'Snom': capacidad,
            'L': largo,
            'r': resistencia,
            'x': reactancia,
            'c': capacitancia,
            'Term1': Term1ID,
            'Term2': Term2ID,
            'Save': row.Save
        }

    # Guardar diccionario con atributos de cables en diccionario de datos de red AC
    atributos['CablesData'] = CablesData

    # Guardar diccionario con atributos en diccinario de datos generales
    data_dict['Atributos'] = atributos
    # Retornar diccionario con datos de red AC para constuir objetos
    return data_dict


# Funcion para leer datos de atributos de objetos de red AC
def leer_escenarios_ac(data_dict, fecha_ini, fecha_fin):
    # Crear diccionario de datos para red ac
    escenario_dict = dict()
    # Si hay una red con atributos definida en el diccionario de datos, empezar a rescatar datos de simulación
    if data_dict['Atributos']:
        # Extraer y asignar perfiles PVac
        PerfilPVSim = dict()
        for PVacID, PVac in data_dict['Atributos']['PVacData'].items():
            Perfil = PVac['Perfil']
            # Obtener perfiles de módulos PV
            results = Perfiles_PV.objects.filter(Perfil_ID=Perfil, Fecha__gte=fecha_ini,
                                                 Fecha__lt=fecha_fin).order_by('Fecha')
            if len(results) == 0:
                raise ValueError('No se encuentran perfiles disponibles para módulos pv de la línea')
            PerfilPV = dict()
            for row in results:
                PerfilPV[row.Fecha] = {
                    'P': row.P
                }
            # Guardar datos de simulación
            PerfilPVSim[PVacID] = PerfilPV

        # Guardar datos en diccionario general para simulación de red AC
        escenario_dict['Perfiles_PV'] = PerfilPVSim

        # Extraer y asignar perfiles SAF
        PerfilSAFSim = dict()
        for SAFID, SAF in data_dict['Atributos']['SAFData'].items():
            consumo_id = SAF['Consumo']
            # Obtener parametros de la vias y agregarlas a la linea creada
            results = Perfiles_SAF.objects.filter(Consumo_ID=consumo_id, Fecha__gte=fecha_ini, Fecha__lt=fecha_fin)
            if len(results) == 0:
                raise ValueError('No se encuentran perfiles de consumo disponibles para SAFs de la línea')
            # Recuperar arreglo de fechas
            PerfilSAF = dict()
            for row in results:
                PerfilSAF[row.Fecha] = {
                    'P': row.P,
                    'Q': row.Q
                }
            # Guardar datos de simulación
            PerfilSAFSim[SAFID] = PerfilSAF

        # Guardar datos en diccionario general para simulación de red AC
        escenario_dict['Perfiles_SAF'] = PerfilSAFSim

    # Guardar diccionario con datos para simulación en diccinario de datos generales
    data_dict['Escenario'] = escenario_dict
    # Retornar diccionario con datos de red AC para simulación
    return data_dict


# Funcion para leer datos de atributos de objetos de red DC
def leer_atributos_dc(linea_id, data_dict):
    # Crear diccionario de datos para red ac
    atributos = dict()

    # Verificar que línea especificada existe en base de datos
    try:
        # Obtener parametros de la linea
        results = Atributos_Lineas.objects.get(Linea_ID=linea_id)

        linea_data = dict()
        linea_data[results.Linea_ID] = {
            'Vnom': results.Vnom
        }
        atributos['LineaData'] = linea_data
    except Atributos_Lineas.DoesNotExist:
        raise ValueError('No se encuentra la línea especificada en la base de datos')

    # VIAS
    # Obtener parametros de la vias y agregarlas a la linea creada
    results = Atributos_Vias.objects.filter(Linea_ID=linea_id)
    if len(results) == 0:
        raise ValueError('No se encuentran vias para la línea especificada')
    # Crear diccionario para datos de vías de la línea
    vias_data_dict = dict()
    # Guardar en diccionario
    for row in results:
        vias_data_dict[row.Via_ID] = {
            'L': row.Largo,
            'r': row.Resistividad,
            'Nrieles': row.Nrieles
        }
    # Guardar diccionario con atributos de vías en diccionario de datos de línea para tracción
    atributos['ViasData'] = vias_data_dict

    # TRENES
    # Obtener parametros de la vias y agregarlas a la linea creada
    results = Atributos_Trenes.objects.filter(Linea_ID=linea_id, En_operacion=True)
    if len(results) == 0:
        raise ValueError('No se encontraron trenes para la línea especificada')
    # Crear diccionario para datos de vías de la línea
    trenes_data = dict()
    # Guardar datos en diccionario
    for row in results:
        # Agregar Tren
        trenes_data[row.Tren_ID] = {
            'Via': row.Via_ID,
            'Status': row.En_operacion,
            'Save': row.Save
        }
    # Guardar diccionario con atributos de trenes en diccionario de datos de línea para tracción
    atributos['TrenesData'] = trenes_data

    # SER
    # Obtener SER de la línea

    # Obtener parametros de la vias y agregarlas a la linea creada
    ListaSER = Lista_Elementos_DC.objects.filter(Linea_ID=linea_id, Tipo='SER')
    if len(ListaSER) == 0:
        raise ValueError('No se encontraron SER para la línea especificada, revisar definición de datos')
    # Crear diccionario para datos de SER de la línea
    SERData = dict()
    for row in ListaSER:
        # Obtener ID de cada SER
        ser_id = row.Elemento_ID
        # Sacar vias que alimenta cada SER
        results = Atributos_SER.objects.filter(SER_ID=ser_id, En_operacion=True)
        # Obtener IDs de Vias alimentadas por cada SER
        ViasIDSER = set(row.Via_ID for row in results)
        # recuperar objetos de vias respectivos
        # RECORDATORIO: POR AHORA LOS SER ESTAN PENSADOS PARA ALIMENTAR VARIAS VIAS, POR LO QUE PODRIAN
        # TENER MAS DE UNA POSICION, RESISTENCIA, ETC... PERO EL CODIGO ESTA CONSIDERANDO LOS MISMOS
        # PARAMETROS PARA CADA VIA (pendiente para próxima actualización)
        # Obtener ID de terminal de conexión para cada SER
        TermID = set(row.Term_ID for row in results).pop()
        # Definir el resto de los parámetros de cada SER
        PosSER = set(row.PosVia for row in results).pop()
        VacSER = set(row.Vac for row in results).pop()
        VdcSER = set(row.Vdc for row in results).pop()
        RSER = set(row.Resistencia for row in results).pop()
        Save = set(row.Save for row in results).pop()
        # Guardar datos en diccionario
        SERData[ser_id] = {
            'Vias': ViasIDSER,
            'pos': PosSER,
            'Vac': VacSER,
            'Vdc': VdcSER,
            'R': RSER,
            'TermID': TermID,
            'Save': Save
        }
    # Guardar diccionario con atributos de SER en diccionario de datos de línea para tracción
    atributos['SERData'] = SERData

    # módulos PV en lado de tracción
    try:
        # Obtener parametros de la vias y agregarlas a la linea creada
        ListaPVDC = Lista_Elementos_DC.objects.filter(Linea_ID=linea_id, Tipo='PVDC')
        # Crear diccionario para datos de módulos PV de la línea
        PVdcData = dict()
        for row in ListaPVDC:
            # Obtener ID de cada SER
            PVDCID = row.Elemento_ID
            # Sacar vias que alimenta cada SER
            results = Atributos_PVdc.objects.filter(Linea_ID=linea_id, En_operacion=True)
            # Obtener IDs de Vias alimentadas por cada SER
            ViasIDPVDC = set(row.Via for row in results)
            # RECORDATORIO: POR AHORA LOS PV ESTAN PENSADOS PARA ALIMENTAR VARIAS VIAS, POR LO QUE PODRIAN
            # TENER MAS DE UNA POSICION, RESISTENCIA, ETC... PERO EL CODIGO ESTA CONSIDERANDO LOS MISMOS
            # PARAMETROS PARA CADA VIA (pendiente para próxima actualización)
            PosPVDC = set(row.PosVia for row in results).pop()
            PerfilPVDC = set(row.PerfilPV for row in results).pop()
            Save = set(row.Save for row in results).pop()
            # Agregar PVdc sin perfil, el cual se agrega una vez se realiza la simulación filtrando por fecha
            PVdcData[PVDCID] = {
                'Vias': ViasIDPVDC,
                'pos': PosPVDC,
                'Perfil': PerfilPVDC,
                'Save': Save
            }
        # Guardar diccionario con atributos de módulos PV en diccionario de datos de línea para tracción
        atributos['PVdcData'] = PVdcData
    except:
        warnings.warn('No se encontraron PV para la línea especificada, revisar definición de datos')

    # Guardar diccionario con datos para simulación en diccinario de datos generales
    data_dict['Atributos'] = atributos
    # Retornar diccionario con datos de red AC para simulación
    return data_dict


# Funcion para leer datos de atributos de objetos de red AC
def leer_escenarios_dc(lLinea_id, data_dict, fecha_ini, fecha_fin):
    # Crear diccionario de datos para red ac
    escenario_dict = dict()

    # Extraer bitacora de trenes
    # Crear diccionario de datos de simulación para trenes
    bitacora_tren_dict = dict()
    for tren_id, tren in data_dict['Atributos']['TrenesData'].items():
        # Obtener parametros de la vias y agregarlas a la linea creada
        results = Bitacora_trenes.objects.filter(Linea_ID=lLinea_id, Fecha__gte=fecha_ini, Fecha__lt=fecha_fin,
                                                 Tren_ID=tren_id).order_by('Fecha')
        if len(results) == 0:
            raise ValueError('No se encuentran bitacoras disponibles para trenes de la línea')
        # Obtener lista de posiciones para simulación
        bitacora_dict = dict()
        for row in results:
            bitacora_dict[row.Fecha] = {
                'pos': row.Posicion,
                'P': row.Potencia
            }
        # Guardar bitácora de cada tren
        bitacora_tren_dict[tren_id] = bitacora_dict

    # Guardar bitácoras en diccionario de perfiles para simulaciones
    escenario_dict['Trenes'] = bitacora_tren_dict

    # Extraer y asignar perfiles PVdc
    # Crear diccionario de datos de simulación para trenes
    perfil_pv_dict = dict()
    for PVID, PVdcdata in data_dict['Atributos']['PVdcData'].items():
        # Obtener parametros de la vias y agregarlas a la linea creada
        results = Perfiles_PV.objects.filter(Fecha__gte=fecha_ini, Fecha__lt=fecha_fin,
                                             Perfil_ID=PVdcdata['Perfil']).order_by('Fecha')
        if len(results) == 0:
            raise ValueError('No se encuentran perfiles disponibles para módulos pv de la línea')
        # Recuperar arreglo de fechas
        fechas = [row.Fecha for row in results]
        # Obtener lista perfilPV para simulación
        MPPT = [row.P for row in results]
        perfil_pv_dict[PVID] = {
            'Fechas': fechas,
            'P': MPPT
        }
    # Guardar bitácoras en diccionario de perfiles para simulaciones
    escenario_dict['PV'] = perfil_pv_dict

    # Guardar diccionario con datos para simulación en diccinario de datos generales
    data_dict['Escenario'] = escenario_dict
    # Retornar diccionario con datos de red AC para simulación
    return data_dict


# Función main para ejecutar métodos para lectura de datos desde servidor
def datos_dc(linea_id, fecha_ini, fecha_fin):
    data_dict = dict()

    fecha_ini = dateparse.parse_datetime(fecha_ini).replace(tzinfo=utc)
    fecha_fin = dateparse.parse_datetime(fecha_fin).replace(tzinfo=utc)

    leer_atributos_dc(linea_id, data_dict)
    leer_escenarios_dc(linea_id, data_dict, fecha_ini, fecha_fin)

    return data_dict


# Función main para ejecutar métodos para lectura de datos desde servidor
def datos_ac(red_ac_id, fecha_ini, fecha_fin):
    data_dict = dict()

    fecha_ini = dateparse.parse_datetime(fecha_ini).replace(tzinfo=utc)
    fecha_fin = dateparse.parse_datetime(fecha_fin).replace(tzinfo=utc)

    leer_atributos_ac(red_ac_id, data_dict)
    leer_escenarios_ac(data_dict, fecha_ini, fecha_fin)

    return data_dict
