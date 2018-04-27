# -*- coding: utf-8 -*-

import RedLineas
import numpy
import math
import matplotlib.pyplot as plt
from pypower import loadcase
from pypower import runpf
from datetime import datetime

############################################################
#                        CLASE LINEA                       #
############################################################
class RedAC:
    # Constructor objeto Linea
    def __init__(self, RedID, Data):
        # ID de la red en la base de datos
        self.ID = RedID
        # Conjunto de líneas suministradas por esta red AC (sin repeticiones)
        self.Lineas = set()
        # Inicilizar vector de fechas de datos
        self.fechas = None
        # Inicializar vector de tiempo para la simulación
        self.t = None
        # Lista de terminales para flujo AC con pypower
        self.Terminales = []
        # Lista de conectores para flujo AC con pypower
        self.Branch = []
        # Lista de generadores para suministrar metro
        self.genMatrix = numpy.array([])
        # Lista de barras para suministrar metro
        self.busMatrix = numpy.array([])
        # Lista de ramas para suministrar metro
        self.branchMatrix = numpy.array([])
        # Resultados power flow PYPOWER
        self.ACresults = dict()
        # Diccionario de resultados generales
        self.Results = dict()
        # CDC de línea
        self.CDC = None
        # Lista de cargas AC
        self.SAF = []
        # Lista de paneles en red AC
        self.PVAC = []
        # fecha inicial de simulaciones
        self.Fecha_ini = None
        # Flag para verificar si se cagaron datos de escenario de simulación
        self.IsSimDefine = False
        # Flag para verificar si se corrieron simulaciones para graficar resultados
        self.IsSim = False
        # Cargar datos y construir objetos que definen la red
        self.CargarDatos(Data)

    # Función para conectar líneas a la red AC
    def addLinea(self, linea):
        self.Lineas.add(linea)
        ListaSER = [ser for ser in linea.Elementos if isinstance(ser, RedLineas.SER)]
        for ser in ListaSER:
            TermID = ser.TermID
            Terminal = set(term for term in self.Terminales if term.Name == TermID).pop()
            Terminal.Elementos.append(ser)
        linea.RedAC = self

    # Función para agregar Terminales
    def addTerm(self, TermID, voltaje):
        newTerm = Term(self, TermID, voltaje)
        return newTerm

    # Función para agregar CDC
    def addCDC(self, voltaje, Snom, Terminal=None):
        newCDC = CDC(self, voltaje, Snom, Terminal)
        self.CDC = newCDC
        return newCDC

    # Función para agregar SAF
    def addSAF(self, SAFID, voltaje, capacidad, P, Q, ConsumoID=None, Terminal=None):
        newSAF = SAF(self, SAFID, voltaje, capacidad, P, Q, ConsumoID, Terminal)
        self.SAF.append(newSAF)
        return newSAF

    # Función para agregar módulo PV en red AC
    def addPVAC(self, PVacID, voltaje, capacidad, Perfil_P=None, Perfil_Q=None, Perfil=None, cosphi=None, Terminal=None):
        newPVAC = PVAC(self, PVacID, voltaje, capacidad, Perfil_P, Perfil_Q, Perfil, cosphi, Terminal)
        self.PVAC.append(newPVAC)
        return newPVAC

    # Función para agregar Trafo en red AC
    def addTrafo(self, TrafoID, capacidad, resistencia, reactancia, TermHV=None, TermLV=None):
        newTrafo = Trafo(self, TrafoID, capacidad, resistencia, reactancia, TermHV, TermLV)
        return newTrafo

    # Función para agregar cable en red AC
    def addCable(self,CableID, capacidad, largo, resistencia, reactancia, capacitancia, Term1=None, Term2=None):
        newCable = Cable(self, CableID, capacidad, largo, resistencia, reactancia, capacitancia, Term1, Term2)
        return newCable

    # Construir objetos de la red AC
    def CargarDatos(self, Data):
        # leer datos de diccionario para crear objetos
        # Crear terminales de red AC
        for TermID, TermData in Data['Atributos']['TermData'].items():
            newTerm = self.addTerm(TermID, TermData['Vnom'])
            newTerm.Save = TermData['Save']

        # Crear trafos de red AC
        for TrafoID, TrafoData in Data['Atributos']['TrafoData'].items():
            TermHV = set(term for term in self.Terminales if term.Name == TrafoData['HV']).pop()
            TermLV = set(term for term in self.Terminales if term.Name == TrafoData['LV']).pop()
            newTrafo = self.addTrafo(TrafoID, TrafoData['Snom'], TrafoData['R'], TrafoData['X'], TermHV, TermLV)
            newTrafo.Save = TrafoData['Save']

        # Crear SAF de red AC
        for SAFID, SAFData in Data['Atributos']['SAFData'].items():
            Term = set(term for term in self.Terminales if term.Name == SAFData['TermID']).pop()
            self.addSAF(SAFID, SAFData['Vac'], SAFData['Snom'], None, None, SAFData['Consumo'], Term)

        # Crear CDC de red AC
        for CDCID, CDCData in Data['Atributos']['CDCData'].items():
            Term = set(term for term in self.Terminales if term.Name == CDCData['TermID']).pop()
            self.addCDC(CDCData['Vac'], CDCData['Snom'], Term)

        # Crear módulos PV de red AC
        for PVacID, PVacData in Data['Atributos']['PVacData'].items():
            Term = set(term for term in self.Terminales if term.Name == PVacData['TermID']).pop()
            self.addPVAC(PVacID, PVacData['Vac'], PVacData['Snom'], None, None, PVacData['Perfil'], PVacData['cosphi'], Term)

        # Crear cables para conectar terminales de red AC
        for CabelID, CablesData in Data['Atributos']['CablesData'].items():
            Term1 = set(term for term in self.Terminales if term.Name == CablesData['Term1']).pop()
            Term2 = set(term for term in self.Terminales if term.Name == CablesData['Term2']).pop()
            newCable = self.addCable(CabelID, CablesData['Snom'], CablesData['L'], CablesData['r'], CablesData['x'], CablesData['c'], Term1, Term2)
            newCable.Save = CablesData['Save']

    # Función para definir simulación
    def DefinirSimulacion(self, SimData):
        # Recuperar fechas para simulaciones
        Fechas = []
        # Definir perfiles de consumo de SAF para simulaciones
        for SAF in self.SAF:
            SAFID = SAF.ID
            # Recuperar diccionario con perfil de consumo de cada SAF
            PerfilSAF = SimData['Escenario']['Perfiles_SAF'][SAFID]
            # Crear listas de potencia activa y reactiva
            Consumo_P = list()
            Consumo_Q = list()
            newFechas = list()
            for Fecha, Consumo in PerfilSAF.items():
                newFechas.append(Fecha)
                Consumo_P.append(Consumo['P'])
                Consumo_Q.append(Consumo['Q'])
            # Asignar consumos respectivos a cada objeto SAF de la red
            SAF.fechas = newFechas
            SAF.Consumo_P = Consumo_P
            SAF.Consumo_Q = Consumo_Q
            SAF.t = [(fecha-newFechas[0]).total_seconds() for fecha in newFechas]
            # Recuperar fechas definidas en cada perfil de consumo SAF
            newFechas = [fecha for fecha in PerfilSAF.keys()]
            # Quedarse con vector de fechas con mayor cantidad de datos
            if len(newFechas) > len(Fechas):
                Fechas = newFechas
        # Definir perfiles de inyecciones de módulos PV para simulaciones
        for PVac in self.PVAC:
            PVacID = PVac.ID
            cosphi = PVac.cosphi
            # Recuperar diccionario con perfil de inyección de potencia de cada PV
            PerfilPVac = SimData['Escenario']['Perfiles_PV'][PVacID]
            # Crear listas de potencia activa y reactiva
            Perfil_P = list()
            Perfil_Q = list()
            newFechas = list()
            for fecha, Perfil in PerfilPVac.items():
                Perfil_P.append(Perfil['P'])
                Perfil_Q.append(Perfil['P']*math.tan(math.acos(cosphi)))
                newFechas.append(fecha)
            # Asignar inyecciones respectivos a cada objeto SAF de la red
            PVac.fechas = newFechas
            PVac.Perfil_P = Perfil_P
            PVac.Perfil_Q = Perfil_Q
            PVac.t = [(fecha - newFechas[0]).total_seconds() for fecha in newFechas]
            # Recuperar fechas definidas en cada perfil de consumo SAF
            newFechas = [fecha for fecha in PerfilPVac.keys()]
            # Quedarse con vector de fechas con mayor cantidad de datos
            if len(newFechas) > len(Fechas):
                Fechas = newFechas
        # Guardar Fechas como atributo de la red
        self.fechas = Fechas
        self.Fecha_ini = self.fechas[0]
        # Flag para confirmar que perfiles de escenario están cargados para simulación
        self.IsSimDefine = True

    # Función para simular comportamiento de red AC en el tiempo así como sus líneas
    def simular(self, Sbase):
        # Verificar que se cargó un escenario de simulación para la línea
        if not self.IsSimDefine:
            raise ValueError('No se definió un escenario de simulación para la red AC')
        # Resetear resultados previos de la línea y verificar que se cargaron datos para simulación
        SimDates = self.fechas
        Interpolar = False
        for linea in self.Lineas:
            if not linea.IsSimDefine:
                raise ValueError('No se definió un escenario de simulación para la línea')
            linea.Reset()
            # Comparar vectores de fechas entre líneas y red, conservar aquel que tiene más datos
            # los vectores restantes para tener vectores de tiempo para simulaciones
            if len(linea.fechas) > len(SimDates):
                SimDates = linea.fechas
                Interpolar = True
        # Crear vector de tiempo decimal de simulación
        SimTime = [(fecha-SimDates[0]).total_seconds() for fecha in SimDates]
        self.fechas = SimDates
        self.t = SimTime
        # interpolar linealmente vectores de consumos de elementos AC para simulaciones
        if Interpolar:
            for SAF in self.SAF:
                SAF.P = numpy.interp(self.t, SAF.t, SAF.Consumo_P)
                SAF.Q = numpy.interp(self.t, SAF.t, SAF.Consumo_Q)
            for PVac in self.PVAC:
                PVac.P = numpy.interp(self.t, PVac.t, PVac.Perfil_P)
                PVac.Q = numpy.interp(self.t, PVac.t, PVac.Perfil_Q)
            for linea in self.Lineas:
                linea.t = SimTime
                for PVdc in linea.Elementos:
                    if isinstance(PVdc, RedLineas.PV):
                        PVdc.P = numpy.interp(self.t, PVdc.t, PVdc.MPPT)
        # Si no es necesario interpolar, consumos de simulaciones son iguales a perfiles de consumo
        else:
            for SAF in self.SAF:
                SAF.P = SAF.Consumo_P
                SAF.Q = SAF.Consumo_Q
            for PVac in self.PVAC:
                PVac.P = PVac.Perfil_P
                PVac.Q = PVac.Perfil_Q
            for linea in self.Lineas:
                for PVdc in linea.Elementos:
                    if isinstance(PVdc, RedLineas.PV):
                        PVdc.P = PVdc.MPPT
        # Resetear diccionario de resultados generales
        self.Results = dict()
        # Simulación para cada instante de tiempo
        for i, now in enumerate(self.t, start=0):
            # Resolver estado de cada línea conectada a la red AC
            for linea in self.Lineas:
                # Resolver flujo de red DC
                linea.simular(i)
            # Resolver flujo AC
            self.FlujosAC(Sbase, i)
        # Confirmar que se realizó simulación para permitir graficar resultados
        self.IsSim = True

    # Función para obtener resultados AC y consumo total de línea
    def FlujosAC(self, Sbase, t_index):

        for PVAC in self.PVAC:
            # Actualizar matriz de generación con valores interpolados
            self.genMatrix[PVAC.indice - 1, 1] = PVAC.P[t_index] / (Sbase*1000000)
            self.genMatrix[PVAC.indice - 1, 2] = PVAC.Q[t_index] / (Sbase*1000000)

            self.busMatrix = numpy.array([])
            self.branchMatrix = numpy.array([])

        for bus in self.Terminales:
            bus.actualizar(t_index, Sbase)
            self.busMatrix = numpy.concatenate(
                (self.busMatrix, [bus.ID, bus.Tipo, bus.P, bus.Q, 0, 0, 1, 1, 0, bus.Vnom, 1, 1.1, 0.9]), 0)
        i = 0
        for branch in self.Branch:
            self.branchMatrix = numpy.concatenate((self.branchMatrix,
                                            [branch.Term1.ID, branch.Term2.ID, branch.R, branch.X, branch.Y,
                                            branch.Snom, branch.Snom, branch.Snom, branch.Turns, 0, 1, -360,
                                            360]), 0)
            branch.branchindex = i
            i = i + 1

        # Crear caso para cargalo usando PYPOWER y correr flujos AC
        RedACdict = dict()
        RedACdict['baseMVA'] = Sbase
        RedACdict['bus'] = self.busMatrix.reshape((len(self.Terminales), 13))
        RedACdict['branch'] = self.branchMatrix.reshape((len(self.Branch), 13))
        RedACdict['gen'] = self.genMatrix.reshape((len(self.PVAC) + 1, 21))

        # Cargar caso de pypower con matrices actualizadas
        caseRedAC = loadcase.loadcase(RedACdict)

        # Correr flujo de potencia con PYPOWER
        self.ACresults = runpf.runpf(caseRedAC)

        fecha = datetime.strftime(self.fechas[t_index], '%Y-%m-%d %H:%M:%S')

        # Guardar resultados de flujos para terminales
        for bus in self.Terminales:
            # Recuperar índice de bus en matriz de buses de pypower con resultados
            busindex = numpy.where(self.ACresults[0]['bus'][:,0] == bus.ID)[0].item()
            # Guardar resultados respectivos
            bus.Results[fecha] = {'V': self.ACresults[0]['bus'][busindex,7].item(), 'delta': self.ACresults[0]['bus'][busindex,8].item(), 'P': self.ACresults[0]['bus'][busindex,2].item(), 'Q': self.ACresults[0]['bus'][busindex,3].item()}

        # Guardar resultados de flujos para líneas y trafos
        for branch in self.Branch:
            # Recuperar potencias de entrada y salida de la rama
            Pf = self.ACresults[0]['branch'][branch.branchindex, 13].item()
            Qf = self.ACresults[0]['branch'][branch.branchindex, 14].item()
            Pt = self.ACresults[0]['branch'][branch.branchindex, 15].item()
            Qt = self.ACresults[0]['branch'][branch.branchindex, 16].item()

            # Calcular pérdidas y cargabilidad de cada rama
            Ploss= math.fabs(Pf-Pt)
            Qloss = math.fabs(Qf-Qt)
            Loading = math.sqrt(math.pow(Pf,2)+math.pow(Qf,2))*100/branch.Snom

            # Guardar resultados respectivos
            branch.Results[fecha] = {'Pf': Pf,
                                  'Qf': Qf,
                                  'Ploss': Ploss,
                                  'Qloss': Qloss,
                                  'Loading': Loading}

        self.CDC.Results[fecha] = {'P': self.ACresults[0]['gen'][0, 1].item(), 'Q':self.ACresults[0]['gen'][0, 2].item()}

    # Función para graficar resultados
    def plotresults(self):

        if self.IsSim == True:
            # Graficar resultados de voltajes de simulación
            # Gráfico de potencia activa suministrada desde CDC
            plt.figure(1)
            plt.plot(self.t, [self.CDC.Results[key]['P'] for key in self.CDC.Results.keys()], '-r', linewidth=1.0)
            plt.xlabel('Tiempo [s]')
            plt.ylabel('Potencia [MW]')
            plt.title('Evolución de inyección de CDC')
            plt.grid(True)
            # Gráfico de potencia reactiva suministrada desde CDC
            plt.figure(2)
            plt.plot(self.t, [self.CDC.Results[key]['Q'] for key in self.CDC.Results.keys()], linewidth=1.0)
            plt.xlabel('Tiempo [s]')
            plt.ylabel('Potencia [MVAr]')
            plt.title('Evolución de inyección de CDC')
            plt.grid(True)

            plt.show()
        else:
            raise ValueError("No se han realizado simulaciones para graficar y guardar resultados.")

    # Función para guardar resultados en base de datos
    def saveresults(self):
        # Verificar que se realizó una simulación para guardar resultados
        if not self.IsSim:
            raise ValueError('No se han realizado simulaciones')

        # Guardar resultados de flujos para terminales
        BusRes = dict()
        for bus in self.Terminales:
            if bus.Save:
                # Guardar resultados de bus en datos generales
                BusRes[bus.Name] = bus.Results
        self.Results['Terminales'] = BusRes

        # Guardar resultados de flujos para ramas
        BranchRes = dict()
        for branch in self.Branch:
            if branch.Save:
                BranchRes[branch.ID] = branch.Results
        self.Results['Ramas'] = BranchRes

        LineasRes = dict()
        for linea in self.Lineas:
            if linea.IsSim:
                LineasRes[linea.ID] = linea.saveresults()

        if LineasRes:
            self.Results['Lineas'] = LineasRes

        return self.Results


############################################################
#                     CLASE TERMINAL                       #
############################################################
class Term:
    # Constructor objeto terminal
    def __init__(self, linea, Term_ID, voltaje):
        # ID como nombre identificador en base de datos (string, etc...)
        self.Name = Term_ID
        #  ID para PYPOWER
        self.ID = len(linea.Terminales) + 1
        # Agregar nuevo terminal a lista de terminales de la red
        linea.Terminales.append(self)
        # Inicializar valores de potencias para simulaciones
        self.P = 0
        self.Q = 0
        # Voltaje en [kV]
        self.Vnom = voltaje
        # Barra PV por defecto
        self.Tipo = 2
        # Inicializar lista de elementos conectados al terminal creado
        self.Elementos = []
        # Definir diccionario para guardar resultados de simulaciones
        self.Results = dict()
        # Flag para definir si se guardan o no resultados de simulaciones en la base de datos
        self.Save = False

    # Función para actualizar valores de pótencias de elementos conectados para simulación
    def actualizar(self, t_index, Sbase):
        # Resetear valores de potencias del terminal en caso de que ya hubieran datos definidos
        self.P = 0
        self.Q = 0
        # Sumar consumos de elementos conectados a terminal para definir demandas en PYPOWER
        for elemento in self.Elementos:
            if isinstance(elemento, CDC):
                # Si CDC está conectado en terminal, entonces este se define como barra slack
                self.Tipo = 3
            elif isinstance(elemento, RedLineas.SER):
                self.P = self.P + elemento.P[t_index]/(Sbase*1000000)
            else:
                self.P = self.P + elemento.P[t_index]/(Sbase*1000000)
                self.Q = self.Q + elemento.Q[t_index]/(Sbase*1000000)

        # Si hay consumo de potencia reactiva entonces se define como barra PQ
        if self.Q != 0 and self.Tipo != 3:
            self.Tipo = 1


############################################################
#                      CLASE BRANCH                        #
############################################################
class Branch:
    # Constructor objeto branch (trafos, cables, etc...)
    def __init__(self, linea, BranchID, capacidad, resistencia, reactancia, capacitancia, Term1=None, Term2=None):
        self.ID = BranchID
        # Definir capacidad de rama en [MVA]
        self.Snom = capacidad
        # Definir parámetros en [p.u.] de la rama
        self.R = resistencia
        self.X = reactancia
        self.Y = capacitancia
        # Asignar terminales especificados por el usuario
        self.Term1 = Term1
        self.Term2 = Term2

        # Diferenciados entre trafos y líneas para PYPOWER si es que se especifican los terminales
        if Term1 != None and Term2 != None:
            if Term1.Vnom != Term2.Vnom:
                # Se elementan terminales con diferentes voltajes (Trafo)
                self.Turns = 1
            else:
                # Se conectan terminales con mismos voltajes (Cable)
                self.Turns = 0
        else:
            # No se especificaron terminales en constructor
            self.Turns = None

        # Agregar a lista de conectores de línea
        linea.Branch.append(self)
        # Guardar índice de línea o trafo en matriz de ramas de pypower
        self.branchindex = None
        # Definir diccionario para guardar resultados de simulaciones
        self.Results = dict()
        # Flag para definir si se guardan o no resultados de simulaciones en la base de datos
        self.Save = False

    # Función para interconectar dos terminales
    def interconectar(self, Term1, Term2):
        self.Term1 = Term1
        self.Term2 = Term2

        if Term1.Vnom != Term2.Vnom:
            self.Turns = 1
        else:
            self.Turns = 0


############################################################
#                     SUBCLASE TRAFO                       #
############################################################
class Trafo(Branch):
    # Constructor objeto transformador
    def __init__(self, linea, TrafoID, capacidad, resistencia, reactancia, TermHV=None, TermLV=None):
        # Llamar constructor de clase branch por herencia
        super(Trafo, self).__init__(linea, TrafoID, capacidad, resistencia, reactancia, 0, TermHV, TermLV)

        # En este caso por construcción se sabe que es trafo
        self.Turns = 1


############################################################
#                     SUBCLASE CABLE                       #
############################################################
class Cable(Branch):
    # Constructor de objeto cable
    def __init__(self, linea, CableID, capacidad, largo, resistencia, reactancia, capacitancia, Term1=None, Term2=None):
        # Verificar que voltajes de terminales son iguales para interconexión
        if Term1 != None and Term2 != None and Term1.Vnom != Term2.Vnom:
            raise ValueError('Se intentó interconectar terminales de diferentes voltajes mediante un cable.')

        # Llamar constructor de clase branch por herencia
        super(Cable, self).__init__(linea, CableID, capacidad, largo*resistencia, largo*reactancia, largo*capacitancia, Term1, Term2)

        # Guardar largo del cable en [m]
        self.largo = largo
        # En este caso por construcción se sabe que es línea
        self.Turns = 0


############################################################
#                    CLASE ELEMENTO AC                     #
############################################################
class ElementoAC:
    # Constructor objeto Elemento AC
    def __init__(self, Red, voltaje, capacidad, Terminal=None):
        self.Red = Red
        self.Vnom = voltaje
        self.Pnom = capacidad
        # Inicializar listas de perfiles de potencia que se cargan para hacer simulaciones
        self.P = []
        self.Q = []
        # Terminal de conexión del elemento AC
        self.Term = None

        if Terminal != None and Terminal.Vnom != self.Vnom:
            # Verificar que voltaje del terminal entregado como argumento coincide con el del elemento
            raise ValueError("Se intetó conectar el panel a un terminal con un voltaje diferente.")
        else:
            self.conectar(Terminal)

    # Función para conectar elemento a terminal
    def conectar(self, Terminal):
        # Verificar concordancia de voltaje
        if self.Vnom != Terminal.Vnom:
            raise ValueError("Se intentaron conectar elementos con diferentes voltajes")

        self.Term = Terminal
        Terminal.Elementos.append(self)


############################################################
#                      SUBCLASE CDC                        #
############################################################
class CDC(ElementoAC):
    # Constructor objeto CDC
    def __init__(self, Red, voltaje, capacidad, Terminal=None):
        # Llamar constructor de clase elemento AC por herencia
        super(CDC, self).__init__(Red, voltaje, capacidad, Terminal)

        # Definir diccionario de resultados de simulaciones
        self.Results = dict()
        # Agregar CDC como generador irrestricto en capacidad
        Red.genMatrix = numpy.concatenate((Red.genMatrix,[self.Term.ID, 0, 0, 9999, -9999, 1, self.Pnom, 1, self.Pnom, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),0)


############################################################
#                      SUBCLASE SAF                        #
############################################################
class SAF(ElementoAC):
    # Constructor clase SAF
    def __init__(self, Red, SAFID, voltaje, capacidad, Consumo_P, Consumo_Q, ConsumoID = None, Terminal=None):
        # Llamar constructor de clase elemento AC por herencia
        super(SAF, self).__init__(Red, voltaje, capacidad, Terminal)
        # ID de SAF
        self.ID = SAFID
        # ID de consumo en base de datos
        self.ConsumoID = ConsumoID
        # Perfil de consumo
        self.Consumo_P = Consumo_P
        self.Consumo_Q = Consumo_Q
        # Vectores de tiempo para simulaciones
        self.fechas = None
        self.t = None

############################################################
#                      SUBCLASE PVAC                       #
############################################################
class PVAC(ElementoAC):
    # Constructor objeto PV an lado AC
    def __init__(self, Red, PVacID, voltaje, capacidad , Perfil_P=None, Perfil_Q=None, PerfilID=None, cosphi=None, Terminal=None):
        # Llamar constructor de clase elemento AC por herencia
        super(PVAC, self).__init__(Red, voltaje, capacidad, Terminal)
        # ID del módulo
        self.ID = PVacID
        # ID Perfil en base de datos
        self.PerfilID = PerfilID
        # Perfil de generación (diccionario horario)
        self.Perfil_P = Perfil_P
        self.Perfil_Q = Perfil_Q
        # Vectores de tiempo para simulaciones
        self.fechas = None
        self.t = None
        # Definir factor de potencia para inyección de Q de módulo PV
        if cosphi == None:
            # Tomar cosphi de 0.95 por defecto
            self.cosphi = 0.95
        else:
            self.cosphi = cosphi
        # Agregar panel como generador para resolver flujo AC usando PYPOWER
        Red.genMatrix = numpy.vstack((Red.genMatrix, [self.Term.ID, 0, 0, 0, 0, 1, self.Pnom, 1, self.Pnom, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))
        # Guardar índice de panel PV en matriz de generadores para actualizar valores de potencia en simulaciones
        self.indice = Red.genMatrix.shape[0]