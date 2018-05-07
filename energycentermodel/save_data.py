# -*- coding: utf-8 -*-
from django.db import transaction, DatabaseError

from energycentermodel.models import Resultados_Terminales, Resultados_Elementos_DC, Resultados_Branch, \
    Resumen_Simulaciones_DC


def saveACresults(RedAC, ResData, simID):
    # Guardar resultados de simulación para cada terminal
    for Bus, BusRes in ResData['Terminales'].items():
        fechas = list()
        V = list()
        delta = list()
        P = list()
        Q = list()

        for fecha, Res in BusRes.items():
            fechas.append(fecha)
            V.append(Res['V'])
            delta.append(Res['delta'])
            P.append(Res['P'])
            Q.append(Res['Q'])
        # Query para intentar recuperar datos la simulación si es que existen
        query_set = Resultados_Terminales.objects.filter(sim_id=simID, term_id=Bus, fecha__gt=min(fechas),
                                                         fecha__lte=max(fechas), red_id=RedAC)
        with transaction.atomic():
            if query_set.exists():
                # actualizar resultados de simulaciones
                for i, fecha in enumerate(fechas):
                    # Primero tratar de actualizar campos en caso de que ya existan datos
                    Resultados_Terminales.objects.filter(sim_id=simID, fecha=fecha, term_id=Bus, red_id=RedAC).update(
                        v=V[i], delta=delta[i], p=P[i], q=Q[i])
            else:
                data = []
                for i, fecha in enumerate(fechas):
                    data.append([simID, fecha, Bus, RedAC, V[i], delta[i], P[i], Q[i]])
                    Resultados_Terminales.objects.create(sim_id=simID, fecha=fecha, term_id=Bus, red_id=RedAC, v=V[i],
                                                         delta=delta[i], p=P[i], q=Q[i])

    # Guardar resultados de simulación para cada cable y trafo
    for Branch, BranchRes in ResData['Ramas'].items():
        fechas = list()
        Pf = list()
        Qf = list()
        Ploss = list()
        Qloss = list()
        Loading = list()
        for fecha, Res in BranchRes.items():
            fechas.append(fecha)
            Pf.append(Res['Pf'])
            Qf.append(Res['Qf'])
            Ploss.append(Res['Ploss'])
            Qloss.append(Res['Qloss'])
            Loading.append(Res['Loading'])

        query_set = Resultados_Branch.objects.filter(sim_id=simID, branch_id=Branch, fecha__gt=min(fechas),
                                                     fecha__lte=max(fechas), red_id=RedAC)
        with transaction.atomic():
            if query_set.exists():
                # actualizar datos
                for i, fecha in enumerate(fechas):
                    Resultados_Branch.objects.filter(sim_id=simID, fecha=fecha, branch_id=Branch, red_id=RedAC).update(
                        pf=Pf[i], qf=Qf[i], ploss=Ploss[i], qloss=Qloss[i], loading=Loading[i])
            else:
                for i, fecha in enumerate(fechas):
                    Resultados_Branch.objects.create(sim_id=simID, fecha=fecha, branch_id=Branch, red_id=RedAC,
                                                     pf=Pf[i], qf=Qf[i], ploss=Ploss[i], qloss=Qloss[i],
                                                     loading=Loading[i])


def saveDCresults(Linea, ResData, simID):
    # Guardar parámetros de simulación realizada
    try:
        with transaction.atomic():
            Resumen_Simulaciones_DC.objects.filter(sim_id=simID).delete()
            Resumen_Simulaciones_DC.objects.create(sim_id=simID, e_ser=sum(ResData['General']['PSER']),
                                                   e_trenes=sum(ResData['General']['PTrenes']),
                                                   e_perdidas=sum(ResData['General']['Perdidas']),
                                                   e_almacenable=-sum(ResData['General']['Pexc']))
    except DatabaseError:
        raise ValueError("no se definieron parámetros válidos para registrar la simulación.")

    # Guardar resultados de simulación para cada tren
    for Tren, TrenRes in ResData['Trenes'].items():
        fechas = list()
        V = list()
        P = list()
        for fecha, Res in TrenRes.items():
            fechas.append(fecha)
            V.append(Res['V'])
            P.append(Res['P'])
        query_set = Resultados_Elementos_DC.objects.filter(sim_id=simID, elemento_id=Tren, fecha__gt=min(fechas),
                                                           fecha__lte=max(fechas))
        if query_set.exists():
            for i, fecha in enumerate(fechas):
                Resultados_Elementos_DC.objects.filter(sim_id=simID, fecha=fecha, elemento_id=Tren,
                                                       linea_id=Linea).update(v=V[i], p=P[i])
        # No existen datos por lo que se deben insertar
        else:
            for i, fecha in enumerate(fechas):
                Resultados_Elementos_DC.objects.create(sim_id=simID, fecha=fecha, elemento_id=Tren, linea_id=Linea,
                                                       v=V[i], p=P[i])

    # Guardar resultados de simulación para cada SER
    for SER, SERRes in ResData['SER'].items():
        fechas = list()
        V = list()
        P = list()
        for fecha, Res in SERRes.items():
            fechas.append(fecha)
            V.append(Res['V'])
            P.append(Res['P'])

        query_set = Resultados_Elementos_DC.objects.filter(sim_id=simID, elemento_id=SER, fecha__gt=min(fechas),
                                                           fecha__lte=max(fechas))
        if query_set.exists():
            # Existen datos por lo que se deben actualizar
            for i, fecha in enumerate(fechas):
                Resultados_Elementos_DC.objects.filter(sim_id=simID, fecha=fecha, elemento_id=SER,
                                                       linea_id=Linea).update(v=V[i], p=P[i])
        # No existen datos por lo que se deben insertar
        else:
            for i, fecha in enumerate(fechas):
                Resultados_Elementos_DC.objects.create(sim_id=simID, fecha=fecha, elemento_id=SER,
                                                       linea_id=Linea, v=V[i], p=P[i].item())

    # Guardar resultados de simulación para cada PV
    for PVdc, PVdcRes in ResData['PV'].items():
        fechas = list()
        V = list()
        P = list()
        for fecha, Res in PVdcRes.items():
            fechas.append(fecha)
            V.append(Res['V'])
            P.append(Res['P'])

        query_set = Resultados_Elementos_DC.objects.filter(sim_id=simID, elemento_id=PVdc, fecha__gt=min(fechas),
                                                           fecha__lte=max(fechas))
        if query_set.exists():
            # Existen datos por lo que se deben actualizar
            for i, fecha in enumerate(fechas):
                Resultados_Elementos_DC.objects.filter(sim_id=simID, elemento_id=PVdc, fecha=fecha,
                                                       linea_id=Linea).update(v=V[i], p=P[i])
        # No existen datos por lo que se deben insertar
        else:
            for i, fecha in enumerate(fechas):
                Resultados_Elementos_DC.objects.create(sim_id=simID, elemento_id=PVdc, fecha=fecha,
                                                       linea_id=Linea, v=V[i], p=P[i])
