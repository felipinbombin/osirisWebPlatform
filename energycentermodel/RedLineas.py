# -*- coding: utf-8 -*-

import numpy
import matplotlib.pyplot as plt
from datetime import datetime


############################################################
#                        CLASE LINEA                       #
############################################################
class Linea:
    # Constructor objeto Linea
    def __init__(self, LineaID, Data):
        # Linea ID
        self.ID = LineaID
        # Conjunto (sin repeticiones) de vias de la línea
        self.Vias = set()
        # Conjunto (sin repeticiones) de elementos de la línea
        self.Elementos = set()
        # Lista para definir nodos y más tarde ordenarlos
        self.Nodos = []
        # Lista de pérdidas en la líena
        self.Perdidas = []
        # Lista de potencia consumida por trenes
        self.PTrenes = []
        # Lista de potencia total suministrada por SER
        self.PSER = []
        # Lista de potencia excedentaria
        self.Pexc = []
        # Inicilizar vector de fechas de datos
        self.fechas = None
        # Inicializar vector de tiempo para la simulación
        self.t = None
        # fecha inicial de simulaciones
        self.Fecha_ini = None
        # Definir a que red ac pertenece para suministrar la línea
        self.RedAC = None
        # Flag para verificar si se cagaron datos de escenario de simulación
        self.IsSimDefine = False
        # Flag para verificar si se corrieron simulaciones para graficar resultados
        self.IsSim = False
        # Diccionario de resultados generales
        self.Results = dict()
        # Cargar datos de base de datos
        self.CargarDatos(Data)

    # Función para agregar una nueva vía
    def addVia(self, ViaID, largo, resistividad, num_rieles):
        viaref = Via(self, ViaID, largo, resistividad, num_rieles)
        self.Vias.add(viaref)
        return viaref

    # Función para agregar SER
    def addSER(self, vias, elementoID, pos, voltajeAC, voltaje, resistencia, TermID=None):
        newSER = SER(self, vias, elementoID, pos, voltajeAC, voltaje, resistencia, TermID)
        self.Elementos.add(newSER)
        return newSER

    # Función para agregar Tren
    def addTren(self, vias, elementoID, pos, *varargin):
        newTren = Tren(self, vias, elementoID, pos, *varargin)
        self.Elementos.add(newTren)
        return newTren

    # Función para agregar SER
    def addPV(self, vias, elementoID, pos, Perfil=None, MPPT=None, *varargin):
        newPV = PV(self, vias, elementoID, pos, Perfil, MPPT)
        self.Elementos.add(newPV)
        return newPV

    # Función para resetear vectores de resultados de las simulaciones
    def Reset(self):
        # Resetear flag de simulación realizada
        self.IsSim = False
        # Resetear resultados nodales de elementos
        for elemento in self.Elementos:
            elemento.V = []
            elemento.Results = dict()
            if isinstance(elemento,SER):
                elemento.P = []
        #Resetear indicadores gobales
        self.Perdidas = []
        self.PTrenes = []
        self.PSER = []
        self.Pexc = []

    # Construir objetos de la la línea
    def CargarDatos(self, Data):
        # leer datos de diccionario para crear objetos
        # Definir parámetros de la línea
        for LineaID, LineaData in Data['Atributos']['LineaData'].items():
            self.Vnom = LineaData['Vnom']

        # Crear vías de la línea
        for ViaID, ViaData in Data['Atributos']['ViasData'].items():
            self.addVia(ViaID, ViaData['L'], ViaData['r'], ViaData['Nrieles'])

        # Crear trenes de la línea
        for TrenID, TrenesData in Data['Atributos']['TrenesData'].items():
            Vias = set(via for via in self.Vias if via.ID == TrenesData['Via'])
            newTren = self.addTren(Vias, TrenID, None, None, None)
            newTren.Save = TrenesData['Save']

        # Crear SER de la línea
        for SERID, SERData in Data['Atributos']['SERData'].items():
            Vias = set(via for via in self.Vias if via.ID in SERData['Vias'])
            newSER = self.addSER(Vias, SERID, SERData['pos'], SERData['Vac'], SERData['Vdc'], SERData['R'], SERData['TermID'])
            newSER.Save = SERData['Save']

        # Crear módulos PV de la línea
        for PVdcID, PVdcData in Data['Atributos']['PVdcData'].items():
            Vias = set(via for via in self.Vias if via.ID in PVdcData['Vias'])
            newPVdc = self.addPV(Vias, PVdcID, PVdcData['pos'], PVdcData['Perfil'], None, None)
            newPVdc.Save = PVdcData['Save']

    # Función para definir simulación
    def DefinirSimulacion(self, SimData):
        # Recuperar fechas para simulaciones
        Fechas = []
        # Definir perfiles de consumo de trenes para simulaciones
        for tren in self.Elementos:
            if isinstance(tren, Tren):
                TrenID = tren.ID
                Bitacora = SimData['Escenario']['Trenes'][TrenID]
                # Crear listas de consumo de potencia y asignarla al objeto tren
                Consumo_P = list()
                newFechas = list()
                Posiciones = list()
                for fecha, TrenSimData in Bitacora.items():
                    newFechas.append(fecha)
                    Consumo_P.append(TrenSimData['P'])
                    Posiciones.append(TrenSimData['pos'])
                # Asignar consumo a tren respectivo
                tren.P = Consumo_P
                # Crear listas de posiciones y asignarla al objeto tren
                tren.posiciones = Posiciones
                # Recuperar fechas definidas en cada perfil de consumo SAF
                newFechas = [fecha for fecha in Bitacora.keys()]
                if len(newFechas) > len(Fechas):
                    Fechas = newFechas
        # Definir perfiles de inyección de módulos PV
        for PVdc in self.Elementos:
            if isinstance(PVdc, PV):
                PVID = PVdc.ID
                PerfilPV = SimData['Escenario']['PV'][PVID]
                # Crear listas de consumo de potencia y asignarla al objeto tren
                MPPT = PerfilPV['P']
                newFechas = PerfilPV['Fechas']
                # Asignar perfil de generación a módulo PV respectivo
                PVdc.fechas = newFechas
                PVdc.MPPT = MPPT
                PVdc.t = [(fecha-newFechas[0]).total_seconds() for fecha in newFechas]
                # Recuperar fechas definidas en cada perfil de consumo SAF
                if len(newFechas) > len(Fechas):
                    Fechas = newFechas
        # Guardar Fechas como atributo de la línea
        self.fechas = Fechas
        # Flag para confirmar que perfiles de escenario están cargados para simulación
        self.IsSimDefine = True

    # Función para resolver estado de la red
    def simular(self, t_index=None, *varargin):
        # Verificar que se cargó un escenario de simulación para la línea
        if not self.IsSimDefine:
            raise ValueError('No se definió un escenario de simulación para la línea')
        # Si se simula la línea sola, entonces se usa el vector de tiempo de su bitácora de trenes que esté cargada
        if t_index == None:
            # Resetear vector de resultados de voltajes para elementos
            self.Reset()
            # Definir vector de tiempo como vector de tiempo de elementos de la línea
            self.t = [(fecha-self.fechas[0]).total_seconds() for fecha in self.fechas]
            # Definir potencias para simulación de elementos de la vía
            for PVdc in self.Elementos:
                if isinstance(PVdc, PV):
                    PVdc.P = numpy.interp(self.t, PVdc.t, PVdc.MPPT)
            # Empezar simulación con tiempo propio
            for i, now in enumerate(self.t, start=0):
                self.simular(i, *varargin)
        else:
            # Definir voltaje nominal para iniciar supuesto de solución numérica
            Vnom = self.Vnom
            # Actualizar posición de trenes
            for j, elemento in enumerate(self.Elementos):
                # Actualizar posición de trenes de acuerdo con su bitácora
                if isinstance(elemento, Tren):
                    newpos = elemento.posiciones[t_index]
                    elemento.mover(newpos)

            # Recuperar nodos activos
            nodosactivos = [nodo for nodo in self.Nodos if nodo.IsActive]
            # Si no hay nodos activos terminar ejecución
            if not nodosactivos:
                raise ValueError("Error: no hay nodos activos en el sistema")
            # Ordenar lista de nodos por posición en las vías
            nodosactivos.sort(key = lambda x: x.Pos, reverse = False)
            Num_nodos = len(nodosactivos)

            # Inicializar matrices para resolver estado de la línea
            Voltajes = numpy.ones(Num_nodos)* Vnom
            Admitancia = numpy.zeros((Num_nodos, Num_nodos))
            Iiny = numpy.zeros((Num_nodos))
            P = numpy.zeros((Num_nodos))
            YSER = numpy.zeros((Num_nodos))

            # Construir matriz de admitancias
            for k, nodo in enumerate(nodosactivos):
                for elemento in nodo.Elementos:
                    Iiny[k] = Iiny[k] + elemento.I
                    if isinstance(elemento, Tren) or isinstance(elemento, PV):
                        P[k] = P[k] + elemento.P[t_index]
                    else:
                        YSER[k] = YSER[k] + elemento.Y
                for via in nodo.Vias:
                    # Obtener nodos activos de la vía
                    nodosvia = [nodo for nodo in via.Nodos if nodo.IsActive]
                    # Ordenar los nodos de acuerdo a su posición en la vía
                    nodosvia.sort(key = lambda x: x.Pos, reverse = False)
                    # Encontrar indice de nodo en la vía
                    i = nodosvia.index(nodo)
                    if i == 0:
                        # Caso en que nodo es primero en la lista
                        dist2 = nodosvia[i + 1].Pos - nodo.Pos
                        resis2 = dist2 * via.Resistividad / via.NRieles
                        j = nodosactivos.index(nodosvia[i + 1])
                        Admitancia[k, j] = Admitancia[k, j] - 1/resis2
                    elif i == len(nodosvia) - 1:
                        # Caso en que nodo es último en la lista
                        dist1 = nodo.Pos - nodosvia[i - 1].Pos
                        resis1 = dist1 * via.Resistividad / via.NRieles
                        j = nodosactivos.index(nodosvia[i - 1])
                        Admitancia[k, j] = Admitancia[k, j] - 1/resis1
                    else:
                        dist1 = nodo.Pos - nodosvia[i - 1].Pos
                        dist2 = nodosvia[i + 1].Pos - nodo.Pos
                        resis1 = dist1 * via.Resistividad / via.NRieles
                        resis2 = dist2 * via.Resistividad / via.NRieles
                        j = nodosactivos.index(nodosvia[i - 1])
                        Admitancia[k, j] = Admitancia[k, j] - 1 / resis1
                        j = nodosactivos.index(nodosvia[i + 1])
                        Admitancia[k, j] = Admitancia[k, j] - 1 / resis2
                Admitancia[k, k] = -Admitancia[k, :].sum() + YSER[k]

            # Resolver flujos iterativamente
            if len(varargin) == 2:
                tolerancia = varargin[1]
                Niter = varargin[2]
            elif len(varargin) == 1:
                tolerancia = varargin[1]
                Niter = 100
            else:
                # Valores por defecto de tolerancia y número de iteraciones
                tolerancia = 0.01
                Niter = 100

            current_error = 1000
            iter = 0
            I = Iiny + P / Voltajes

            while iter < Niter and abs(current_error) > tolerancia:
                # Guardar voltajes de iteración anterior
                Vold = Voltajes
                # Calcular nuevos voltajes
                Voltajes = numpy.linalg.inv(Admitancia).dot(I)
                # Calcular nuevas corrientes
                I = Iiny + P / Voltajes
                #Calcular máximo error
                current_error = abs(Voltajes - Vold).max()
                # Actualizar contador de iteraciones
                iter = iter + 1

            # Si se alcanza número máximo de iteraciones, notificar infactibilidad
            if iter == Niter:
                self.IsSim = False
                raise ValueError("Error: el problema no es factible")
            else:
                # Confirmar que se realizó simulación para permitir graficar resultados
                self.IsSim = True

            # Guardar resultados de voltajes en nodo
            for k, nodo in enumerate(nodosactivos):
                nodo.V = Voltajes[k]

            # Guardar resultados para cada elemento de la línea
            Perdidas = 0
            PTrenes = 0
            PSER = 0

            for elemento in self.Elementos:
                # Obtener inyecciones de subestaciones rectificadoras
                if isinstance(elemento, SER):
                    # Calcular inyecciones de subestaciones rectificadoras
                    elemento.P.append((elemento.I / elemento.Y - elemento.Nodo.V) * elemento.I)
                    # Valor de potencia instantaneo para simulaciones AC
                    PSER = PSER + (elemento.I/elemento.Y - elemento.Nodo.V)*elemento.I
                    # Actualizar pérdidas
                    Perdidas = Perdidas + (elemento.I/elemento.Y - elemento.Nodo.V)*elemento.I
                else:
                    Perdidas = Perdidas + elemento.P[t_index]
                if isinstance(elemento, Tren):
                    PTrenes = PTrenes - elemento.P[t_index]

                # Guardar resultado en diccionario de resultados según fecha de simulación
                elemento.Results[datetime.strftime(self.fechas[t_index], '%Y-%m-%d %H:%M:%S')] = {'V': elemento.Nodo.V.item(), 'P': elemento.P[t_index]}

            # Guardar indicadores generales de la línea
            if PSER >=0:
                self.PSER.append(PSER/1000000)
                self.Pexc.append(0)
                self.Perdidas.append(Perdidas/1000000)
            else:
                self.PSER.append(0)
                self.Pexc.append(PSER/1000000)
                self.Perdidas.append(0)

            self.PTrenes.append(PTrenes/1000000)


            return Admitancia

    # Función para graficar resultados
    def plotresults(self):
        if self.IsSim == True:
            # Crear leyenda para gráficos
            Leyenda_SER = [elemento.ID for elemento in self.Elementos if isinstance(elemento, SER)]
            Leyenda_PV = [elemento.ID for elemento in self.Elementos if isinstance(elemento, PV)]

            # Graficar resultados de voltajes de simulación
            plt.figure(1)
            Leyenda_voltajes = []
            for elemento in self.Elementos:
                    V = []
                    for fecha, resultados in elemento.Results.items():
                        V.append(resultados['V'])
                    plt.plot(self.t, V, elemento.marker)
                    Leyenda_voltajes.append(elemento.ID)

            plt.xlabel('Tiempo [s]')
            plt.ylabel('Voltaje [V]')
            plt.title('Evolución de voltajes')
            plt.legend(Leyenda_voltajes)
            plt.grid(True)

            plt.figure(2)
            for elemento in self.Elementos:
                    P = []
                    for fecha, resultados in elemento.Results.items():
                        P.append(resultados['P']/1000000)

                    plt.plot(self.t, P, elemento.marker)

            plt.xlabel('Tiempo [s]')
            plt.ylabel('Potencia [MW]')
            plt.title('Evolución de potencia suministrada')
            plt.legend(Leyenda_SER)
            plt.grid(True)

            plt.figure(3)
            plt.plot(self.t, self.Perdidas, '-r', linewidth=1.0)
            plt.xlabel('Tiempo [s]')
            plt.ylabel('Potencia [MW]')
            plt.title('Evolución de pérdidas')
            plt.grid(True)

            plt.figure(4)
            plt.plot(self.t, self.PTrenes, '-b', linewidth=1.0)
            plt.xlabel('Tiempo [s]')
            plt.ylabel('Potencia [MW]')
            plt.title('Evolución de consumo de trenes')
            plt.grid(True)

            plt.figure(5)
            plt.plot(self.t, self.PSER, '-g', linewidth=1.0)
            plt.xlabel('Tiempo [s]')
            plt.ylabel('Potencia [MW]')
            plt.title('Evolución de inyección de SERs')
            plt.grid(True)

            plt.figure(6)
            for elemento in self.Elementos:
                if isinstance(elemento, PV):
                    P = [P/1000000 for P in elemento.P ]
                    plt.plot(self.t, P, elemento.marker)
            plt.xlabel('Tiempo [s]')
            plt.ylabel('Potencia [MW]')
            plt.title('Evolución de potencia suministrada PV')
            plt.legend(Leyenda_PV)
            plt.grid(True)
            plt.show()
        else:
            raise ValueError("No se han realizado simulaciones para graficar y guardar resultados.")

    # Función para guardar resultados
    def saveresults(self):
        if not self.IsSim:
            raise ValueError('No se han realizado simulaciones')
        TrenesRes = dict()
        SerRes = dict()
        PVRes = dict()
        for elemento in self.Elementos:
            if elemento.Save:
                if isinstance(elemento, Tren):
                    TrenesRes[elemento.ID] = elemento.Results
                elif isinstance(elemento, SER):
                    SerRes[elemento.ID] = elemento.Results
                else:
                    PVRes[elemento.ID] = elemento.Results

        self.Results['General'] = {'PSER': self.PSER, 'Pexc': self.Pexc, 'PTrenes': self.PTrenes, 'Perdidas': self.Perdidas}
        self.Results['Trenes'] = TrenesRes
        self.Results['SER'] = SerRes
        self.Results['PV'] = PVRes

        return self.Results


############################################################
#                         CLASE VIA                        #
############################################################
class Via:
    # Constructor objeto Via
    def __init__(self, linea, ViaID, largo, resistividad, num_rieles):
        self.ID = ViaID
        self.Linea = linea
        self.Largo = largo
        self.Resistividad = resistividad
        self.NRieles = num_rieles
        self.Nodos = set()


############################################################
#                      CLASE ELEMENTO                      #
############################################################
class Elemento:
    # Constructor de objeto elemento
    def __init__(self, linea, vias, ElementoID, pos):
        self.ID = ElementoID
        self.Linea = linea
        if isinstance(vias, set):
            self.Vias = vias
        else:
            self.Vias = set()
            self.Vias.add(vias)
        # Posición del elemento en sus vías
        self.Pos = pos
        # Definir diccionario para guardar resultados de simulaciones
        self.Results = dict()
        # Inicialización de nodos para equivalente eléctrico de red DC
        self.Nodo = None
        self.oldNodo = Nodo(linea, pos)
        newnodo = self.buscarNodo(pos)
        if not newnodo:
            newnodo = Nodo(linea, pos)
        else:
            pass
        self.conectar(newnodo)
        # Flag para definir si se guardan o no resultados de simulaciones en la base de datos
        self.Save = False

    # Función para agregar nodo para este elemento
    def buscarNodo(self, pos):
        nodos = [nodo for nodo in self.Linea.Nodos if nodo.Pos == pos]
        if not nodos:
            # Si no hay nodos con la posicion especificada no se retorna nada
            return None
        else:
            # Se encuentran nodos con misma posición
            for nodo in nodos:
                if self.Vias.intersection(nodo.Vias):
                    # Se encuentra nodo con vías en común y misma posición
                    return nodo

        # Si no hay nodo con misma posición y con vías en común, no se retorna nada
        return None

    # Función para desconectar elemento en una vía
    def desconectar(self, nodo):
        # Verificar si elemento está solo
        nodo.Elementos.discard(self)
        if not nodo.Elementos:
            nodo.IsActive = False
        else:
            nodo.Vias.clear()
            for elemento in nodo.Elementos:
                nodo.Vias = nodo.Vias | elemento.Vias

    # Función para conectar nodo
    def conectar(self, nodo):
        nodo.Elementos.add(self)
        nodo.Vias = nodo.Vias | self.Vias
        if nodo.Elementos:
            nodo.IsActive = True
        self.Nodo = nodo
        for via in self.Vias:
            via.Nodos.add(nodo)

    # Función para mover elemento
    def mover(self, newpos):
        nodofound = self.buscarNodo(newpos)
        # No se encuentra un nodo existente en la posición
        if not nodofound:
            # Elemento actual comparte nodo
            if len(self.Nodo.Elementos) > 1:
                self.desconectar(self.Nodo)
                newnodo = self.oldNodo
                newnodo.move(newpos)
                self.conectar(newnodo)
            else:
                self.Nodo.move(newpos)
                if not self.Nodo.IsActive:
                    self.conectar(self.Nodo)
        else:
            self.desconectar(self.Nodo)
            if len(self.Nodo.Elementos) > 0:
                self.conectar(nodofound)
            else:
                self.oldNodo = self.Nodo
                self.conectar(nodofound)


############################################################
#                       SUBCLASE SER                       #
############################################################
class SER(Elemento):
    # Contructor clase tren
    def __init__(self, linea, vias, elementoID, pos, voltajeAC, voltaje, resistencia, TermID=None):
        super(SER, self).__init__(linea, vias, elementoID, pos)
        # Tipo de línea para graficar resultados
        self.marker = '--'
        if voltaje < 0 or resistencia < 0:
            raise ValueError("Error: se debe definir un voltaje y una resistencia con valores positivos")

        # Característica en vacío de SER para condiciones de borde para resolución numerica de red DC
        self.I = voltaje/resistencia
        self.Y = 1/resistencia

        # Definir voltaje nominal AC de SER
        self.Vnom = voltajeAC

        # Potencias instantáneas para simulaciones en lado AC
        self.P = []
        self.Q = []

        # Guardar ID de barra para conectar SER
        self.TermID = TermID


############################################################
#                       SUBCLASE TREN                      #
############################################################
class Tren(Elemento):
    # Contructor clase tren
    def __init__(self, linea, vias, elementoID, pos, posiciones=None, consumo=None):
        super(Tren, self).__init__(linea, vias, elementoID, pos)
        self.marker = '-'
        self.P = consumo
        self.posiciones = posiciones
        self.I = 0
        self.Y = 0


############################################################
#                       SUBCLASE PV                        #
############################################################
class PV(Elemento):
    # Contructor clase tren
    def __init__(self, linea, vias, elementoID, pos, Perfil=None, MPPT=None):
        super(PV, self).__init__(linea, vias, elementoID, pos)
        self.marker = '-.'
        self.P = []
        self.I = 0
        self.Y = 0
        self.MPPT = MPPT
        self.PerfilID = Perfil
        self.fechas = None
        self.t = None


############################################################
#                         CLASE NODO                       #
############################################################
class Nodo:
    # Constructor de objeto nodo
    def __init__(self, linea, pos):
        self.NodoID = len(linea.Nodos) + 1
        self.Pos = pos
        self.Elementos = set()
        self.IsActive = False
        self.Vias = set()
        self.V = None
        linea.Nodos .append(self)

    # Función para mover nodo
    def move(self, pos):
        self.Pos = pos