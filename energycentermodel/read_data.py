# -*- coding: utf-8 -*-
import warnings

from energycentermodel.models import Atributos_Terminales, Atributos_Trafos, Atributos_SAF, Atributos_CDC, \
    Atributos_PVAC, Atributos_Cables, Perfiles_PV, Perfiles_SAF, Atributos_Lineas, Atributos_Vias, Atributos_Trenes, \
    Lista_Elementos_DC, Atributos_SER, Atributos_PVdc, Bitacora_trenes


# Funcion para leer datos de atributos de objetos de red AC
def leer_atributos_ac(RedACID, data_dict):
    # Crear diccionario de datos para red ac
    atributos = dict()
    # Resetear diccionario de datos generales
    data_dict['Atributos'] = dict()
    # Crear terminales en lado AC para red respectiva
    try:
        # Crear diccionario para datos de terminales
        term_data = dict()
        for row in Atributos_Terminales.objects.filter(Red_ID=RedACID):
            term_data[row.Term_ID] = {
                'Vnom': row.Vnom,
                'Save': row.save
            }
        # Guardar diccionario con atributos de terminales en diccionario de datos de red AC
        atributos['TermData'] = term_data
    except:
        raise ValueError('No se encuentran terminales para la red especificada. No es posible construir la topología')

    # Crear transformadores de red AC
    try:
        # Obtener parametros de la vias y agregarlas a la linea creada
        # Crear diccionario para datos de terminales
        trafo_data = dict()
        results = Atributos_Trafos.objects.filter(Red_ID=RedACID, En_operacion=True)
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
                'Save': row.save
            }

        # Guardar diccionario con atributos de trafos en diccionario de datos de red AC
        atributos['TrafoData'] = trafo_data
    except:
        raise ValueError('No se encuentran transformadores para la línea especificada, no se puede construir topología')

    # Crear SAF y conectarlos a sus respectivos terminales
    try:
        # Obtener parametros de la vias y agregarlas a la linea creada
        results = Atributos_SAF.objects.filter(Red_ID=RedACID, En_operacion=True)
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
    except:
        warnings.warn('No se encuentran SAF para la línea especificada')

    # Crear CDC de la linea
    try:
        # Obtener parametros de la vias y agregarlas a la linea creada
        results = Atributos_CDC.objects.filter(Red_ID=RedACID)
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
                'Save': row.save
            }

        # Guardar diccionario con atributos de CDC en diccionario de datos de red AC
        atributos['CDCData'] = CDCData
    except:
        raise ValueError('No se encuentran CDC para la línea especificada, no se puede construir topología.')

    # Crear módulos PV en lado AC
    # Obtener PVAC de la línea
    try:
        # Obtener parametros de la vias y agregarlas a la linea creada
        ListaPVAC = Atributos_PVAC.objects.filter(Red_ID=RedACID, En_operacion=True)
        # Crear diccionario para datos de módulos PV en red ac
        PVacData = dict()
        for row in ListaPVAC:
            # Obtener ID de cada módulo
            PVACID = row.PVac_id
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
    try:
        # Obtener parametros de la vias y agregarlas a la linea creada
        results = Atributos_Cables.objects.filter(Red_ID=RedACID, En_operacion=True)
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
                'Save': row.save
            }

        # Guardar diccionario con atributos de cables en diccionario de datos de red AC
        atributos['CablesData'] = CablesData
    except:
        raise ValueError('No se encuentran cables disponibles para la línea especificada')

    # Guardar diccionario con atributos en diccinario de datos generales
    data_dict['Atributos'] = atributos
    # Retornar diccionario con datos de red AC para constuir objetos
    return data_dict


# Funcion para leer datos de atributos de objetos de red AC
def leer_escenarios_ac(Data, Fecha_ini, Fecha_fin):
    # Resetear diccionario de datos generales
    Data['Escenario'] = dict()
    # Crear diccionario de datos para red ac
    Escenario = dict()
    # Si hay una red con atributos definida en el diccionario de datos, empezar a rescatar datos de simulación
    if Data['Atributos']:
        # Extraer y asignar perfiles PVac
        PerfilPVSim = dict()
        for PVacID, PVac in Data['Atributos']['PVacData'].items():
            Perfil = PVac['Perfil']
            try:
                # Obtener perfiles de módulos PV
                results = Perfiles_PV.objects.filter(Perfil_ID=Perfil, Fecha__gte=Fecha_ini,
                                                     Fecha__lt=Fecha_fin).order_by('fecha')
                PerfilPV = dict()
                for row in results:
                    PerfilPV[row.Fecha] = {
                        'P': row.p
                    }
                # Guardar datos de simulación
                PerfilPVSim[PVacID] = PerfilPV
            except:
                raise ValueError('No se encuentran perfiles disponibles para módulos pv de la línea')
        # Guardar datos en diccionario general para simulación de red AC
        Escenario['Perfiles_PV'] = PerfilPVSim

        # Extraer y asignar perfiles SAF
        PerfilSAFSim = dict()
        for SAFID, SAF in Data['Atributos']['SAFData'].items():
            ConsumoID = SAF['Consumo']
            try:
                # Obtener parametros de la vias y agregarlas a la linea creada
                results = Perfiles_SAF.objects.filter(Consumo_ID=ConsumoID, Fecha__gte=Fecha_ini, Fecha__lt=Fecha_fin)
                # Recuperar arreglo de fechas
                PerfilSAF = dict()
                for row in results:
                    PerfilSAF[row.Fecha] = {
                        'P': row.p,
                        'Q': row.q
                    }
                # Guardar datos de simulación
                PerfilSAFSim[SAFID] = PerfilSAF
            except:
                raise ValueError('No se encuentran perfiles de consumo disponibles para SAFs de la línea')
        # Guardar datos en diccionario general para simulación de red AC
        Escenario['Perfiles_SAF'] = PerfilSAFSim

    # Guardar diccionario con datos para simulación en diccinario de datos generales
    Data['Escenario'] = Escenario
    # Retornar diccionario con datos de red AC para simulación
    return Data


# Funcion para leer datos de atributos de objetos de red DC
def leer_atributos_dc(linea_id, data_dict):
    # Resetear diccionario de datos generales
    data_dict['Atributos'] = dict()
    # Crear diccionario de datos para red ac
    Atributos = dict()

    # Verificar que línea especificada existe en base de datos
    try:
        # Obtener parametros de la linea
        results = Atributos_Lineas.objects.get(Linea_ID=linea_id)
        LineaData = dict()
        LineaData[results.Linea_ID] = {
            'Vnom': results.Vnom
        }
        Atributos['LineaData'] = LineaData
    except:
        raise ValueError('No se encuentra la línea especificada en la base de datos')

    # VIAS
    try:
        # Obtener parametros de la vias y agregarlas a la linea creada
        results = Atributos_Vias.objects.filter(Linea_ID=linea_id)
        # Crear diccionario para datos de vías de la línea
        ViasData = dict()
        # Guardar en diccionario
        for row in results:
            ViasData[row.Via_ID] = {
                'L': row.Largo,
                'r': row.Resistividad,
                'Nrieles': row.Nrieles
            }
        # Guardar diccionario con atributos de vías en diccionario de datos de línea para tracción
        Atributos['ViasData'] = ViasData
    except:
        raise ValueError('No se encuentran vias para la línea especificada')

    # TRENES
    try:
        # Obtener parametros de la vias y agregarlas a la linea creada
        results = Atributos_Trenes.objects.filter(Linea_ID=linea_id, En_operacion=True)
        # Crear diccionario para datos de vías de la línea
        TrenesData = dict()
        # Guardar datos en diccionario
        for row in results:
            # Agregar Tren
            TrenesData[row.Tren_ID] = {
                'Via': row.Via_ID,
                'Status': row.En_operacion,
                'Save': row.Save
            }
        # Guardar diccionario con atributos de trenes en diccionario de datos de línea para tracción
        Atributos['TrenesData'] = TrenesData
    except:
        raise ValueError('No se encontraron trenes para la línea especificada')

    # SER
    # Obtener SER de la línea
    try:
        # Obtener parametros de la vias y agregarlas a la linea creada
        ListaSER = Lista_Elementos_DC.objects.filter(Linea_ID=linea_id, Tipo='SER')
        # Crear diccionario para datos de SER de la línea
        SERData = dict()
        for row in ListaSER:
            # Obtener ID de cada SER
            SERID = row.Elemento_ID
            # Sacar vias que alimenta cada SER
            try:
                results = Atributos_SER.objects.filter(ser_id=SERID, En_operacion=True)
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
                SERData[SERID] = {
                    'Vias': ViasIDSER,
                    'pos': PosSER,
                    'Vac': VacSER,
                    'Vdc': VdcSER,
                    'R': RSER,
                    'TermID': TermID,
                    'Save': Save
                }
            except:
                pass
        # Guardar diccionario con atributos de SER en diccionario de datos de línea para tracción
        Atributos['SERData'] = SERData
    except:
        raise ValueError('No se encontraron SER para la línea especificada, revisar definición de datos')

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
            try:
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
            except:
                pass
        # Guardar diccionario con atributos de módulos PV en diccionario de datos de línea para tracción
        Atributos['PVdcData'] = PVdcData
    except:
        warnings.warn('No se encontraron PV para la línea especificada, revisar definición de datos')

    # Guardar diccionario con datos para simulación en diccinario de datos generales
    data_dict['Atributos'] = Atributos
    # Retornar diccionario con datos de red AC para simulación
    return data_dict


# Funcion para leer datos de atributos de objetos de red AC
def leer_escenarios_dc(LineaID, data_dict, Fecha_ini, Fecha_fin):
    # Resetear diccionario de datos generales
    data_dict['Escenario'] = dict()
    # Crear diccionario de datos para red ac
    escenario = dict()

    # Extraer bitacora de trenes
    # Crear diccionario de datos de simulación para trenes
    bitacora_tren = dict()
    for tren_id, tren in data_dict['Atributos']['TrenesData'].items():
        try:
            # Obtener parametros de la vias y agregarlas a la linea creada
            results = Bitacora_trenes.objects.filter(Linea_ID=LineaID, Fecha__gte=Fecha_ini, Fecha__lt=Fecha_fin,
                                                     Tren_ID=tren_id).order_by('Fecha')
            # Obtener lista de posiciones para simulación
            Bitacora = dict()
            for row in results:
                Bitacora[row['fecha']] = {
                    'pos': row.Posicion,
                    'P': row.Potencia
                }
            # Guardar bitácora de cada tren
            bitacora_tren[tren_id] = Bitacora
        except:
            raise ValueError('No se encuentran bitacoras disponibles para trenes de la línea')
    # Guardar bitácoras en diccionario de perfiles para simulaciones
    escenario['Trenes'] = bitacora_tren

    # Extraer y asignar perfiles PVdc
    # Crear diccionario de datos de simulación para trenes
    perfil_pv = dict()
    for PVID, PVdcdata in data_dict['Atributos']['PVdcData'].items():
        try:
            # Obtener parametros de la vias y agregarlas a la linea creada
            results = Perfiles_PV.objects.filter(Fecha__gte=Fecha_ini, Fecha__lt=Fecha_fin,
                                                 Perfil_ID=PVdcdata['Perfil']).order_by('Fecha')
            # Recuperar arreglo de fechas
            fechas = [row.Fecha for row in results]
            # Obtener lista perfilPV para simulación
            MPPT = [row.p for row in results]
            perfil_pv[PVID] = {
                'Fechas': fechas,
                'P': MPPT
            }
        except:
            raise ValueError('No se encuentran perfiles disponibles para módulos pv de la línea')
    # Guardar bitácoras en diccionario de perfiles para simulaciones
    escenario['PV'] = perfil_pv

    # Guardar diccionario con datos para simulación en diccinario de datos generales
    data_dict['Escenario'] = escenario
    # Retornar diccionario con datos de red AC para simulación
    return data_dict


# Función main para ejecutar métodos para lectura de datos desde servidor
def datos_dc(LineaID, Fecha_ini, Fecha_fin):
    Data = dict()

    leer_atributos_dc(LineaID, Data)

    leer_escenarios_dc(LineaID, Data, Fecha_ini, Fecha_fin)

    return Data


# Función main para ejecutar métodos para lectura de datos desde servidor
def datos_ac(RedACID, Fecha_ini, Fecha_fin):
    Data = dict()

    leer_atributos_ac(RedACID, Data)

    leer_escenarios_ac(Data, Fecha_ini, Fecha_fin)

    return Data
