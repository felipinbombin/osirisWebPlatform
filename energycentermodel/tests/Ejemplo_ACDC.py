# -*- coding: utf-8 -*-
# Ejemplo que sirve para simular red AC y linéa de tracción DC de forma secuencial
import os

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'osirisWebPlatform.settings'
django.setup()


import energycentermodel.tests.RedAC as ac_network
import energycentermodel.tests.RedLineas as line_network
import energycentermodel.read_data as read_data
import energycentermodel.save_data as save_data

# Crear diccionario con datos y escenario de simulación de la red a partir de la base de datos
DatosCochrane = read_data.datos_ac('Cochrane', '2017-01-01 00:00:00', '2017-01-01 23:59:00')

# Crear diccionario con datos y escenario de simulación de la línea a partir de la base de datos
DatosLinea1 = read_data.datos_dc('Linea1', '2017-01-01 00:00:00', '2017-01-01 23:59:00')

# Crear objeto linea
Linea1 = line_network.Linea('Linea1', DatosLinea1)

# Crear objeto red AC
Cochrane = ac_network.RedAC('Cochrane', DatosCochrane)

# Conectar línea a red AC
Cochrane.addLinea(Linea1)

# Definir escenario de simulación con el diccionario creado anteriormente
Cochrane.DefinirSimulacion(DatosCochrane)

# Definir escenario de simulación con el diccionario creado anteriormente
Linea1.DefinirSimulacion(DatosLinea1)

# Simular operación conjunto de red AC y línea de metro con potencia base Sbase = 1 [MW]
Cochrane.simular(1)

# Diccionario de resultados de las simulaciones
Resultados = Cochrane.saveresults()

# Guardar resultados de simulaciones de red AC en base de datos
save_data.saveACresults(Cochrane.ID, Resultados, 'sim1')

# Guardar resultados de simulaciones de líneas en base de datos
for lineaID, lineaRes in Resultados['Lineas'].items():
    save_data.saveDCresults(lineaID, lineaRes, 'sim1')

# Graficar resultados para red AC
Cochrane.plotresults()

# Graficar resultados para red de tracción DC de línea
Linea1.plotresults()