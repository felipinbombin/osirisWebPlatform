# -*- coding: utf-8 -*-
# Ejemplo que sirve para simular red AC independiente
import energycentermodel.tests.RedAC as ac_network
import energycentermodel.read_data as read_data
import energycentermodel.save_data as save_data

# Crear diccionario con datos y escenario de simulación de la red a partir de la base de datos
DatosCochrane = read_data.datos_ac('Cochrane', '2017-01-01 00:00:00', '2017-01-01 23:59:00')

# Crear diccionario con datos y escenario de simulación de la línea a partir de la base de datos
DatosLinea1 = read_data.datos_dc('Linea1', '2017-01-01 00:00:00', '2017-01-01 23:59:00')

# Crear objeto red AC
Cochrane = ac_network.RedAC('Cochrane', DatosCochrane)

# Definir escenario de simulación con el diccionario creado anteriormente
Cochrane.DefinirSimulacion(DatosCochrane)

# Simular operación conjunto de red AC y línea de metro con potencia base Sbase = 1 [MW]
Cochrane.simular(1)

# Diccionario de resultados de las simulaciones
Resultados = Cochrane.saveresults()

# Guardar resultados de simulaciones de red AC en base de datos
save_data.saveACresults(Cochrane.ID, Resultados, 'sim1')

# Graficar resultados para red AC
Cochrane.plotresults()