# -*- coding: utf-8 -*-
# Ejemplo que sirve para linéa de tracción DC independiente

import energycentermodel.tests.RedLineas as line_network
import energycentermodel.read_data as read_data
import energycentermodel.save_data as save_data

# Crear diccionario con datos y escenario de simulación de la línea a partir de la base de datos
DatosLinea1 = read_data.datos_dc('Linea1', '2017-01-01 00:00:00', '2017-01-01 23:59:00')

# Crear objeto linea
Linea1 = line_network.Linea('Linea1', DatosLinea1)

# Definir escenario de simulación con el diccionario creado anteriormente
Linea1.DefinirSimulacion(DatosLinea1)

# Simular operación conjunto de red AC y línea de metro con potencia base Sbase = 1 [MW]
Linea1.simular()

# Guardar resultados de simulaciones de líneas en base de datos
save_data.saveDCresults(Linea1.ID, Linea1.saveresults(), 'sim1')

# Graficar resultados para red de tracción DC de línea
Linea1.plotresults()
