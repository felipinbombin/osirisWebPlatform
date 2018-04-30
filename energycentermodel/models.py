# -*- coding: utf-8 -*-

from django.db import models


# Tablas para redes de tracción DC


class Atributos_Lineas(models.Model):
    """
    Almacena los nombres identificadores o ID de todas las líneas DC que se encuentran definidas en la base de datos,
    y que se desean simular. La tabla posee los siguientes campos:
    """
    Linea_ID = models.CharField(max_length=100)
    # identificador de la línea
    Vnom = models.FloatField()
    # voltaje operacional nominal de cada línea, el cual se usa como punto de partida para la resolución numérica
    # de la operación de la línea


class Atributos_Vias(models.Model):
    """
    Almacena los IDs de las vías que conforman cada línea, así como sus propiedades físicas.
    Cada línea puede estar definida por varias vías con trenes viajando en diferentes direcciones de forma simultánea.
    Dado que la potencia es suministrada a los motores mediantes los rieles de cada vía, su largo, resistividad y
    número de rieles en paralelo define la matriz de admitancia del equivalente nodal de cada línea de tracción.
    """
    Via_ID = models.CharField(max_length=100)
    Linea_ID = models.CharField(max_length=100)
    Largo = models.FloatField()
    # en metros
    Resistividad = models.FloatField()
    # Ω/m
    Nrieles = models.IntegerField()


class Lista_Elementos_DC(models.Model):
    """
    Registro de todos los elementos que forman parte de cada línea DC. Entre estos elementos se encuentran trenes,
    SERs y módulos fotovoltaicos, cada cual identificado por un tipo que puede ser “Tren”, “SER” o PVdc” respectivamente
    """
    Elemento_ID = models.CharField(max_length=100)
    Linea_ID = models.CharField(max_length=100)
    Tipo = models.CharField(max_length=100)
    En_operacion = models.BooleanField()
    # define si se encuentra o no en operación
    Save = models.BooleanField()
    # True si se desea guardar los resultados de las simulaciones


class Atributos_Trenes(models.Model):
    """
    Almacena las IDs de los trenes de cada línea de tracción, la vía en la cual realizan su viaje y si se encuentran
    operacionales
    """
    Tren_ID = models.CharField(max_length=100)
    Linea_ID = models.CharField(max_length=100)
    Via_ID = models.CharField(max_length=100)
    En_operacion = models.BooleanField()
    # define si se encuentra o no en operación
    Save = models.BooleanField()
    # True si se desea guardar los resultados de las simulaciones
    x0 = models.FloatField()
    p0 = models.IntegerField()


class Atributos_SER(models.Model):
    """
    Se identifican cada una de la subestaciones rectificadores que suministran la potencia necesaria para la operación
    de cada línea, a partir de su conexión con una red de suministro en media tensión AC
    """
    SER_ID = models.CharField(max_length=100)
    Linea_ID = models.CharField(max_length=100)
    Via_ID = models.CharField(max_length=100)
    Term_ID = models.CharField(max_length=100)
    # terminal de conexión a su red de suministro AC
    En_operacion = models.BooleanField()
    PosVia = models.FloatField()
    # [m]
    Resistencia = models.FloatField()
    # [Ω]
    Vdc = models.FloatField()
    # [V]
    Vac = models.FloatField()
    # [kV]
    Save = models.BooleanField()


class Atributos_PVdc(models.Model):
    """
    Identifica cada uno de los módulos fotovoltaicos conectados en una línea de tracción DC
    """
    PVdc_ID = models.CharField(max_length=100)
    Linea_ID = models.CharField(max_length=100)
    Via = models.CharField(max_length=100)
    PosVia = models.FloatField()
    En_operacion = models.BooleanField()
    PerfilPV = models.CharField(max_length=100)
    Save = models.BooleanField()


# Tablas para redes de suministro en media tensión AC


class Atributos_Terminales(models.Model):
    """
    Identifica todos los terminales de conexión que forman una red de suministro en media tensión AC. Los terminales
    de conexión corresponden a los puntos de conexión de elementos como generadores (CDC o módulos fotovoltaicos) y
    consumos (SAF y SER).
    """
    Term_ID = models.CharField(max_length=100)
    Red_ID = models.CharField(max_length=100)
    Vnom = models.FloatField()
    Save = models.BooleanField()


class Atributos_Trafos(models.Model):
    """

    """
    Trafo_ID = models.CharField(max_length=100)
    Red_ID = models.CharField(max_length=100)
    En_operacion = models.BooleanField()
    Snom = models.FloatField()
    HVTerm_ID = models.CharField(max_length=100)
    LVTerm_ID = models.CharField(max_length=100)
    Resistencia = models.FloatField()
    Reactancia = models.FloatField()
    Save = models.BooleanField()


class Atributos_SAF(models.Model):
    """

    """
    SAF_ID = models.CharField(max_length=100)
    Red_ID = models.CharField(max_length=100)
    Term_ID = models.CharField(max_length=100)
    En_operacion = models.BooleanField()
    Vac = models.FloatField()
    Snom = models.FloatField()
    Consumo_ID = models.CharField(max_length=100)


class Atributos_CDC(models.Model):
    """

    """
    CDC_ID = models.CharField(max_length=100)
    Red_ID = models.CharField(max_length=100)
    Term_ID = models.CharField(max_length=100)
    Vnom = models.FloatField()
    Snom = models.FloatField()
    Save = models.BooleanField()


class Atributos_PVAC(models.Model):
    """

    """
    PVac_ID = models.CharField(max_length=100)
    Red_ID = models.CharField(max_length=100)
    Term_ID = models.CharField(max_length=100)
    En_operacion = models.BooleanField()
    Vnom = models.FloatField()
    Snom = models.FloatField()
    PerfilPV = models.CharField(max_length=100)
    cosphi = models.FloatField()


class Atributos_Cables(models.Model):
    """

    """
    Cable_ID = models.CharField(max_length=100)
    Red_ID = models.CharField(max_length=100)
    En_operacion = models.BooleanField()
    Term_ID1 = models.CharField(max_length=100)
    Term_ID2 = models.CharField(max_length=100)
    Largo = models.FloatField()
    Snom = models.FloatField()
    Resistencia = models.FloatField()
    Reactancia = models.FloatField()
    Capacitancia = models.FloatField()
    Save = models.BooleanField()


# Tablas para escenarios de simulación


class Bitacora_trenes(models.Model):
    """

    """
    Tren_ID = models.CharField(max_length=100)
    Linea_ID = models.CharField(max_length=100)
    Fecha = models.DateTimeField()
    Via = models.CharField(max_length=100)
    Posicion = models.FloatField()
    Velocidad = models.FloatField()
    Aceleracion = models.FloatField()
    Potencia = models.FloatField()


class Perfiles_PV(models.Model):
    """

    """
    Perfil_ID = models.CharField(max_length=100)
    Fecha = models.DateTimeField()
    P = models.FloatField()


class Perfiles_SAF(models.Model):
    """

    """
    Consumo_ID = models.CharField(max_length=100)
    Fecha = models.DateTimeField()
    P = models.FloatField()
    Q = models.FloatField()


# tablas para almacenar resultados

class Resumen_Simulaciones_DC(models.Model):
    """

    """
    sim_id = models.CharField(max_length=100)
    e_ser = models.FloatField()
    e_trenes = models.FloatField()
    e_perdidas = models.FloatField()
    e_almacenable = models.FloatField()


class Resultados_Elementos_DC(models.Model):
    """

    """
    sim_id = models.CharField(max_length=100)
    fecha = models.DateTimeField()
    elemento_id = models.CharField(max_length=100)
    linea_id = models.CharField(max_length=100)
    v = models.FloatField()
    p = models.FloatField()



class Resultados_Terminales(models.Model):
    """

    """
    sim_id = models.CharField(max_length=100)
    fecha = models.DateTimeField()
    term_id = models.CharField(max_length=100)
    red_id = models.CharField(max_length=100)
    v = models.FloatField()
    delta = models.FloatField()
    p = models.FloatField()
    q = models.FloatField()


class Resultados_Branch(models.Model):
    """

    """
    sim_id = models.CharField(max_length=100)
    fecha = models.DateTimeField()
    branch_id = models.CharField(max_length=100)
    red_id = models.CharField(max_length=100)
    pf = models.FloatField()
    qf = models.FloatField()
    ploss = models.FloatField()
    qloss = models.FloatField()
    loading = models.FloatField()

