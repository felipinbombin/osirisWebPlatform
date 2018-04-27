# -*- coding: utf-8 -*-

def saveACresults(RedAC, ResData, simID, db_connection):
    # Crear cursor para realizar query
    cur = db_connection.cursor()

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
        sql = cur.mogrify('SELECT * FROM resultados_terminales WHERE sim_id=%s AND term_id=%s AND fecha>%s AND fecha<=%s AND red_id=%s;', (simID, Bus, min(fechas), max(fechas), RedAC))
        try:
            # Intentar recuperar datos para verificar si existen
            cur.execute(sql)
            data = cur.fetchall()
            # Existen datos por lo que se deben actualizar
            if data:
                # Crear lista de resultados de simulaciones que se van a actualizar
                newdata = []
                for fecha, i in enumerate(fechas):
                    newdata.append([V[i], delta[i], P[i], Q[i], simID, fecha, Bus, RedAC])
                # Primero tratar de actualizar campos en caso de que ya existan datos
                cur.executemany(
                    'UPDATE resultados_terminales SET v=%s, delta=%s, p=%s, q=%s WHERE sim_id = %s AND fecha = %s AND term_id = %s AND red_id = %s;',
                    newdata)
                db_connection.commit()
            # No existen datos por lo que se deben insertar
            else:
                data = []
                for i, fecha in enumerate(fechas):
                    data.append([simID, fecha, Bus, RedAC, V[i], delta[i], P[i], Q[i]])
                cur.executemany(
                    'INSERT INTO resultados_terminales (sim_id, fecha, term_id, red_id, v, delta, p, q) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                    data)
                db_connection.commit()
        except:
            db_connection.rollback()

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
        # Query para intentar recuperar datos la simulación si es que existen
        sql = cur.mogrify('SELECT * FROM resultados_branch WHERE sim_id=%s AND branch_id=%s AND fecha>%s AND fecha<=%s AND red_id=%s;',
              (simID, Branch, min(fechas), max(fechas), RedAC))
        try:
            # Intentar recuperar datos para verificar si existen
            cur.execute(sql)
            data = cur.fetchall()
            # Existen datos por lo que se deben actualizar
            if data:
                # Crear lista de resultados de simulaciones que se van a actualizar
                newdata = []
                for fecha, i in enumerate(fechas):
                    newdata.append([Pf[i], Qf[i], Ploss[i], Qloss[i], Loading[i], simID, fecha,Branch, RedAC])
                # Primero tratar de actualizar campos en caso de que ya existan datos
                cur.executemany('UPDATE resultados_branch SET pf = %s, qf = %s, ploss = %s, qloss = %s, loading = %s WHERE sim_id = %s AND fecha = %s AND branch_id = %s AND red_id = %s;', newdata)
                db_connection.commit()
            # No existen datos por lo que se deben insertar
            else:
                data = []
                for i, fecha in enumerate(fechas):
                    data.append([simID, fecha, Branch, RedAC, Pf[i], Qf[i], Ploss[i],Qloss[i], Loading[i]])
                cur.executemany(
                    'INSERT INTO resultados_branch (sim_id, fecha, branch_id, red_id, pf, qf, ploss, qloss, loading) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    data)
                db_connection.commit()
        except:
            db_connection.rollback()

    # Cerrar cursor
    cur.close()


def saveDCresults(Linea, ResData, simID, db_connection):
    # Crear cursor para realizar query
    cur = db_connection.cursor()

    # Guardar parámetros de simulación realizada
    try:
        sql = cur.mogrify('DELETE FROM resumen_simulaciones_dc WHERE sim_id=%s', (simID,))
        cur.execute(sql)
        sql = cur.mogrify('INSERT INTO resumen_simulaciones_dc (sim_id, e_ser, e_trenes, e_perdidas, e_almacenable) VALUES (%s,%s,%s, %s, %s);',
            (simID, sum(ResData['General']['PSER']), sum(ResData['General']['PTrenes']), sum(ResData['General']['Perdidas']), -sum(ResData['General']['Pexc'])))
        cur.execute(sql)
        db_connection.commit()
    except:
        db_connection.rollback()
        raise ValueError("no se definieron parámetros válidos para registrar la simulación.")

    # Guardar resultados de simulación para cada tren
    for Tren, TrenRes in ResData['Trenes'].items():
        fechas = list()
        V = list()
        P = list()
        for fecha, Res in TrenRes.items():
            fechas.append(fecha)
            V .append(Res['V'])
            P.append(Res['P'])
        # Query para intentar recuperar datos la simulación si es que existen
        sql = 'SELECT * FROM resultados_elementos_dc WHERE Sim_ID=%s AND Elemento_ID=%s AND Fecha>%s AND Fecha<=%s;'.format(simID, Tren, min(fechas), max(fechas))
        try:
            # Intentar recuperar datos para verificar si existen
            cur.execute(sql)
            data = cur.fetchall()
            # Existen datos por lo que se deben actualizar
            if data:
                # Crear lista de resultados de simulaciones que se van a actualizar
                newdata = []
                for fecha, i in enumerate(fechas):
                    newdata.append([V[i], P[i], simID, fecha, Tren, Linea])
                # Primero tratar de actualizar campos en caso de que ya existan datos
                cur.executemany(
                    'UPDATE resultados_elementos_dc SET V = %s, P = %s WHERE Sim_ID = %s AND Fecha = %s AND Elemento_ID = %s AND Linea_ID = %s;',
                    newdata)
                db_connection.commit()
            # No existen datos por lo que se deben insertar
            else:
                data = []
                for i, fecha in enumerate(fechas):
                    data.append([simID, fecha, Tren, Linea, V[i], P[i]])
                cur.executemany(
                    'INSERT INTO resultados_elementos_dc (Sim_ID, Fecha, Elemento_ID, Linea_ID, V, P) VALUES (%s, %s, %s, %s, %s, %s)',
                    data)
                db_connection.commit()
        except:
            db_connection.rollback()

    # Guardar resultados de simulación para cada SER
    for SER, SERRes in ResData['SER'].items():
        fechas = list()
        V = list()
        P = list()
        for fecha, Res in SERRes.items():
            fechas.append(fecha)
            V .append(Res['V'])
            P.append(Res['P'])
        # Query para intentar recuperar datos la simulación si es que existen
        sql = 'SELECT * FROM resultados_elementos_dc WHERE Sim_ID=%s AND Elemento_ID=%s AND Fecha>%s AND Fecha<=%s;'.format(
            simID, SER, min(fechas), max(fechas))
        try:
            # Intentar recuperar datos para verificar si existen
            cur.execute(sql)
            data = cur.fetchall()
            # Existen datos por lo que se deben actualizar
            if data:
                # Crear lista de resultados de simulaciones que se van a actualizar
                newdata = []
                for fecha, i in enumerate(fechas):
                    newdata.append([V[i], P[i], simID, fecha, SER, Linea])
                # Primero tratar de actualizar campos en caso de que ya existan datos
                cur.executemany(
                    'UPDATE resultados_elementos_dc SET V = %s, P = %s WHERE Sim_ID = %s AND Fecha = %s AND Elemento_ID = %s AND Linea_ID = %s;',
                    newdata)
                db_connection.commit()
            # No existen datos por lo que se deben insertar
            else:
                data = []
                for i, fecha in enumerate(fechas):
                    data.append([simID, fecha, SER, Linea, V[i], P[i].item()])
                cur.executemany(
                    'INSERT INTO resultados_elementos_dc (Sim_ID, Fecha, Elemento_ID, Linea_ID, V, P) VALUES (%s, %s, %s, %s, %s, %s)',
                    data)
                db_connection.commit()
        except:
            db_connection.rollback()

    # Guardar resultados de simulación para cada PV
    for PVdc, PVdcRes in ResData['PV'].items():
        fechas = list()
        V = list()
        P = list()
        for fecha, Res in PVdcRes.items():
            fechas.append(fecha)
            V .append(Res['V'])
            P.append(Res['P'])
        # Query para intentar recuperar datos la simulación si es que existen
        sql = 'SELECT * FROM resultados_elementos_dc WHERE Sim_ID=%s AND Elemento_ID=%s AND Fecha>%s AND Fecha<=%s;'.format(
            simID, PVdc, min(fechas), max(fechas))
        try:
            # Intentar recuperar datos para verificar si existen
            cur.execute(sql)
            data = cur.fetchall()
            # Existen datos por lo que se deben actualizar
            if data:
                # Crear lista de resultados de simulaciones que se van a actualizar
                newdata = []
                for fecha, i in enumerate(fechas):
                    newdata.append([V[i], P[i], simID, fecha, PVdc, Linea])
                # Primero tratar de actualizar campos en caso de que ya existan datos
                cur.executemany(
                    'UPDATE resultados_elementos_dc SET V = %s, P = %s WHERE Sim_ID = %s AND Fecha = %s AND Elemento_ID = %s AND Linea_ID = %s;',
                    newdata)
                db_connection.commit()
            # No existen datos por lo que se deben insertar
            else:
                data = []
                for i, fecha in enumerate(fechas):
                    data.append([simID, fecha, PVdc, Linea, V[i], P[i]])
                cur.executemany(
                    'INSERT INTO resultados_elementos_dc (Sim_ID, Fecha, Elemento_ID, Linea_ID, V, P) VALUES (%s, %s, %s, %s, %s, %s)',
                    data)
                db_connection.commit()
        except:
            db_connection.rollback()

    # Cerrar cursor
    cur.close()