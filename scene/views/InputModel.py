from collections import defaultdict
from scene.models import Scene
from scene.models import MetroLineMetric, OperationPeriodForMetroStation, OperationPeriodForMetroTrack, \
    OperationPeriodForMetroLine

from cmmmodel.models import ModelExecutionHistory

import numpy as np
import datetime
import json
import pickle


class ModelInputDoesNotExistException(Exception):
    pass


class InputModel:

    def __init__(self, scene_obj, model_id):
        """ constructor """
        self.model_id = model_id
        self.scene_obj = scene_obj

    def get_input(self):
        """ retrieve input data """

        if self.model_id == 999:
            # for testing purpose
            input = {
                "seconds": 60
            }
            input = pickle.dumps(input, protocol=pickle.HIGHEST_PROTOCOL)
        elif self.model_id == 1:
            # speed model
            input = speed_model_input(self.scene_obj)
            input = pickle.dumps(input, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            previous_model = self.model_id - 1
            model_obj = ModelExecutionHistory.objects.filter(status=ModelExecutionHistory.OK,
                                                             scene=self.scene_obj,
                                                             model_id=previous_model).order_by("-end").first()
            if model_obj is None:
                raise ModelInputDoesNotExistException

            with open(model_obj.answer.path, mode="rb") as answer_file:
                input = answer_file.read()

        return input

def serialize_input(dictionary):
    """ serialize input model """

    class MyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, datetime.time):
                return str(obj)
            else:
                return super(MyEncoder, self).default(obj)

    dictionary = json.dumps(dictionary, ensure_ascii=False, cls=MyEncoder)
    dictionary = json.loads(dictionary)
    """
    a = json.dumps(response["inputModel"]["top"], ensure_ascii=False, cls=MyEncoder)
    b = json.dumps(response["inputModel"]["sist"], ensure_ascii=False, cls=MyEncoder)
    c = json.dumps(response["inputModel"]["oper"], ensure_ascii=False, cls=MyEncoder)
    print(a)
    print(b)
    print(c)
    """
    return dictionary


def speed_model_input(scene_id):
    """ make input data for speed model """

    scene = Scene.objects.prefetch_related("metroline_set__metrostation_set__operationperiodformetrostation_set",
                                           "metroline_set__metrodepot_set",
                                           "metroline_set__metrolinemetric_set",
                                           "metroline_set__metrotrack_set__operationperiodformetrotrack_set",
                                           "metroline_set__operationperiodformetroline_set",
                                           "metroconnection_set__metroconnectionstation_set__metroStation",
                                           "systemicparams_set").get(id=scene_id)

    inputModel = {"oper": {}, "top": {}, "sist": {}}

    lineNumber = scene.metroline_set.all().count()
    connectionNumber = scene.metroconnection_set.all().count()

    metroConnections = scene.metroconnection_set.all().order_by("id")
    metroLines = scene.metroline_set.all().order_by("id")

    inputModel["top"]["nLines"] = lineNumber
    inputModel["top"]["nConnections"] = connectionNumber

    inputModel["top"]["nStations"] = np.empty([lineNumber, 1], dtype=np.int32)
    inputModel["top"]["nDepots"] = [0] * lineNumber  # np.empty([lineNumber, 1])
    for index, line in enumerate(metroLines):
        inputModel["top"]["nStations"][index] = len(line.metrostation_set.all())
        inputModel["top"]["nDepots"][index] = len(line.metrodepot_set.all())

    if connectionNumber:
        conStations = [[None], [None]] * connectionNumber
        for i in range(0, connectionNumber):
            for j, metroConnectionStation in enumerate(
                    metroConnections[i].metroconnectionstation_set.all().order_by("id")):
                conStations[j][i] = metroConnectionStation.metroStation.name
        inputModel["top"]["connections.stations"] = conStations

        inputModel["top"]["connections.avHeight"] = np.empty([connectionNumber, 1])
        inputModel["top"]["connections.f2Height"] = np.empty([connectionNumber, 1])
        for i in range(0, connectionNumber):
            inputModel["top"]["connections.avHeight"][i] = metroConnections[i].avgHeight
            inputModel["top"]["connections.f2Height"][i] = metroConnections[i].avgSurface
    else:
        inputModel["top"]["connections.stations"] = []
        inputModel["top"]["connections.avHeight"] = []
        inputModel["top"]["connections.f2Height"] = []

    # PAGE PER LINE -----------------------------------------------------------
    inputModel["top"]["lines"] = defaultdict(dict)
    for index, metroLine in enumerate(metroLines):
        inputModel["top"]["lines"][index]["geometry"] = defaultdict(dict)

        metrics = defaultdict(list)
        for metric in metroLine.metrolinemetric_set.all().order_by("id"):
            metricId = metric.metric + str(metric.direction)
            metrics[metricId].append([metric.start, metric.end, metric.value])

        slopeLRId = MetroLineMetric.SLOPE + MetroLineMetric.GOING
        slopeLR = np.zeros([len(metrics[slopeLRId]), 3])
        for i in range(len(metrics[slopeLRId])):
            slopeLR[i, 0] = metrics[slopeLRId][i][0]  # start
            slopeLR[i, 1] = metrics[slopeLRId][i][1]  # end
            slopeLR[i, 2] = metrics[slopeLRId][i][2]  # value

        slopeRLId = MetroLineMetric.SLOPE + MetroLineMetric.REVERSE
        slopeRL = np.zeros([len(metrics[slopeRLId]), 3])
        for i in range(len(metrics[slopeRLId])):
            slopeRL[i, 0] = metrics[slopeRLId][i][0]  # start
            slopeRL[i, 1] = metrics[slopeRLId][i][1]  # end
            slopeRL[i, 2] = metrics[slopeRLId][i][2]  # value

        inputModel["top"]["lines"][index]["geometry"]["slopeLR"] = slopeLR
        inputModel["top"]["lines"][index]["geometry"]["slopeRL"] = slopeRL

        curveLRId = MetroLineMetric.CURVE_RADIUS + MetroLineMetric.GOING
        curveLR = np.zeros([len(metrics[curveLRId]), 3])
        for i in range(len(metrics[curveLRId])):
            curveLR[i, 0] = metrics[curveLRId][i][0]  # start
            curveLR[i, 1] = metrics[curveLRId][i][1]  # end
            curveLR[i, 2] = metrics[curveLRId][i][2]  # value

        curveRLId = MetroLineMetric.CURVE_RADIUS + MetroLineMetric.REVERSE
        curveRL = np.zeros([len(metrics[curveRLId]), 3])
        for i in range(len(metrics[curveRLId])):
            curveRL[i, 0] = metrics[curveRLId][i][0]  # start
            curveRL[i, 1] = metrics[curveRLId][i][1]  # end
            curveRL[i, 2] = metrics[curveRLId][i][2]  # value

        inputModel["top"]["lines"][index]["geometry"]["curvLR"] = curveLR
        inputModel["top"]["lines"][index]["geometry"]["curvRL"] = curveRL

        speedLimitLRId = MetroLineMetric.SPEED_LIMIT + MetroLineMetric.GOING
        speedLimitLR = np.zeros([len(metrics[speedLimitLRId]), 3])
        for i in range(len(metrics[speedLimitLRId])):
            speedLimitLR[i, 0] = metrics[speedLimitLRId][i][0]  # start
            speedLimitLR[i, 1] = metrics[speedLimitLRId][i][1]  # end
            speedLimitLR[i, 2] = metrics[speedLimitLRId][i][2]  # value

        speedLimitRLId = MetroLineMetric.SPEED_LIMIT + MetroLineMetric.REVERSE
        speedLimitRL = np.zeros([len(metrics[speedLimitRLId]), 3])
        for i in range(len(metrics[speedLimitRLId])):
            speedLimitRL[i, 0] = metrics[speedLimitRLId][i][0]  # start
            speedLimitRL[i, 1] = metrics[speedLimitRLId][i][1]  # end
            speedLimitRL[i, 2] = metrics[speedLimitRLId][i][2]  # value

        inputModel["top"]["lines"][index]["geometry"]["spBoundsLR"] = speedLimitLR
        inputModel["top"]["lines"][index]["geometry"]["spBoundsRL"] = speedLimitRL

        groundId = MetroLineMetric.GROUND + "None"
        grounds = np.zeros([len(metrics[groundId]), 3])
        for i in range(len(metrics[groundId])):
            grounds[i, 0] = metrics[groundId][i][0]  # start
            grounds[i, 1] = metrics[groundId][i][1]  # end
            grounds[i, 2] = metrics[groundId][i][2]  # value

        groundByMeter = np.empty([int(grounds[-1][1]), 2])
        for ground in grounds:
            i0 = round(ground[0]) + 1
            i1 = round(ground[1]) - 1
            for i in range(int(i0), int(i1)):
                groundByMeter[i] = [i, ground[2]]
        inputModel["top"]["lines"][index]["geometry"]["underabove"] = groundByMeter

        metroTracks = metroLine.metrotrack_set.all().order_by("id")
        metroStations = metroLine.metrostation_set.all().order_by("id")

        inputModel["top"]["lines"][index]["stations"] = {}
        inputModel["top"]["lines"][index]["tracks"] = {}
        inputModel["top"]["lines"][index]["stations"]["length"] = np.empty([len(metroStations), 1])
        inputModel["top"]["lines"][index]["stations"]["f2avHeight"] = np.empty([len(metroStations), 1])
        inputModel["top"]["lines"][index]["stations"]["f2surfHeight"] = np.empty([len(metroStations), 1])
        inputModel["top"]["lines"][index]["stations"]["platSection"] = np.empty([len(metroStations), 1])
        inputModel["top"]["lines"][index]["stations"]["platAvPerim"] = np.empty([len(metroStations), 1])
        inputModel["top"]["lines"][index]["tracks"]["length"] = np.empty([len(metroTracks), 1])
        inputModel["top"]["lines"][index]["tracks"]["crossSection"] = np.empty([len(metroTracks), 1])
        inputModel["top"]["lines"][index]["tracks"]["avPerim"] = np.empty([len(metroTracks), 1])

        for i, metroStation in enumerate(metroStations):
            inputModel["top"]["lines"][index]["stations"]["length"][i] = metroStation.length
            inputModel["top"]["lines"][index]["stations"]["f2avHeight"][i] = metroStation.secondLevelAverageHeight
            inputModel["top"]["lines"][index]["stations"]["f2surfHeight"][i] = metroStation.secondLevelFloorSurface
            inputModel["top"]["lines"][index]["stations"]["platSection"][i] = metroStation.platformSection
            inputModel["top"]["lines"][index]["stations"]["platAvPerim"][i] = metroStation.platformAveragePerimeter

        for i, metroTrack in enumerate(metroTracks):
            inputModel["top"]["lines"][index]["tracks"]["length"][i] = metroTrack.length
            inputModel["top"]["lines"][index]["tracks"]["crossSection"][i] = metroTrack.crossSection
            inputModel["top"]["lines"][index]["tracks"]["avPerim"][i] = metroTrack.averagePerimeter

    # SYSTEMIC ----------------------------------------------------------------
    # PAGE LINES CHARACTERISTICS ----------------------------------------------
    sys = scene.systemicparams_set.all()[0]

    inputModel["sist"]["trainMass"] = sys.mass
    inputModel["sist"]["inercialMass"] = sys.inercialMass
    inputModel["sist"]["maxAcc"] = sys.maxAccelerationAllowed
    inputModel["sist"]["maxStartForce"] = sys.maxStartingForceAllowed
    inputModel["sist"]["maxBrakeForce"] = sys.maxBrakingForceAllowed
    inputModel["sist"]["regimeChange"] = sys.speedOfMotorRegimeChange
    inputModel["sist"]["maxPower"] = sys.maxPower
    inputModel["sist"]["maxSpeed"] = sys.maxSpeedAllowed

    inputModel["sist"]["Davis"] = {}
    inputModel["sist"]["Davis"]["A"] = sys.davisParameterA
    inputModel["sist"]["Davis"]["B"] = sys.davisParameterB
    inputModel["sist"]["Davis"]["C"] = sys.davisParameterC
    inputModel["sist"]["Davis"]["D"] = sys.davisParameterD
    inputModel["sist"]["Davis"]["E"] = sys.davisParameterE

    inputModel["sist"]["tractEff"] = sys.tractionSystemEfficiency / 100
    inputModel["sist"]["brakeEff"] = sys.brakingSystemEfficiency / 100
    # inputModel["sist"]["receptivity"] = fslc(15+1,1)
    inputModel["sist"]["electBrakeT.p1"] = sys.electricalBrakeTreshold
    inputModel["sist"]["electBrakeT.p2"] = sys.electroMechanicalBrakeThreshold
    # --------------------------------------------------------------

    inputModel["sist"]["trainHVACConsumption"] = sys.hvacConsumption
    inputModel["sist"]["trainAuxConsumption"] = sys.auxiliariesConsumption
    inputModel["sist"]["trainTerminalsResistence"] = sys.trainsTerminalResistance
    inputModel["sist"]["trainPotencial"] = sys.voltageDCTrainsTerminals

    inputModel["sist"]["trainLength"] = sys.length
    inputModel["sist"]["trainCars"] = sys.numberOfCars
    inputModel["sist"]["car_width"] = sys.carWidth
    inputModel["sist"]["car_height"] = sys.carHeight
    inputModel["sist"]["car_thick"] = sys.vehicleWallThickness
    inputModel["sist"]["car_lambda"] = sys.heatConductivityOfTheVehicleWall
    inputModel["sist"]["car_factor"] = sys.cabinVolumeFactor
    inputModel["sist"]["passenger_capacity"] = sys.trainPassengerCapacity

    setPoints = np.zeros([5, 2])
    setPoints[0, 0] = sys.point1Tin
    setPoints[0, 1] = sys.point1Tout
    setPoints[1, 0] = sys.point2Tin
    setPoints[1, 1] = sys.point2Tout
    setPoints[2, 0] = sys.point3Tin
    setPoints[2, 1] = sys.point3Tout
    setPoints[3, 0] = sys.point4Tin
    setPoints[3, 1] = sys.point4Tout
    setPoints[4, 0] = sys.point5Tin
    setPoints[4, 1] = sys.point5Tout

    inputModel["sist"]["SetPoints"] = setPoints

    inputModel["sist"]["ExtraPowerHRS"] = sys.hrsExtraPower
    inputModel["sist"]["isOBESS"] = sys.onBoardEnergyStorageSystem
    inputModel["sist"]["OBESScapacity"] = sys.storageCapacityWeighting

    ####CMM traction####
    inputModel["sist"]["charge_eff"] = sys.obessChargeEfficiency / 100
    inputModel["sist"]["discharge_eff"] = sys.obessDischargeEfficiency / 100
    inputModel["sist"]["OBESS_usable"] = sys.obessUsableEnergyContent
    inputModel["sist"]["OBESS_peak_power"] = sys.maxDischargePower
    inputModel["sist"]["OBESS_max_saving"] = sys.maxEnergySavingPossiblePerHour
    inputModel["sist"]["OBESS_power_limit"] = sys.powerLimitToFeed

    aux = np.array([])
    for metroConnection in metroConnections:
        aux = np.append(aux, metroConnection.consumption)
    inputModel["sist"]["interConsumption"] = aux

    # PAGE PER LINE -----------------------------------------------------------
    inputModel["sist"]["lines"] = defaultdict(dict)
    for index, metroLine in enumerate(metroLines):

        inputModel["sist"]["lines"][index]["SESSusableEnergyContent"] = metroLine.usableEnergyContent
        inputModel["sist"]["lines"][index]["SESSchargingEfficiency"] = metroLine.chargingEfficiency
        inputModel["sist"]["lines"][index]["SESSdischargingEfficiency"] = metroLine.dischargingEfficiency
        inputModel["sist"]["lines"][index]["SESSpeakPower"] = metroLine.peakPower
        inputModel["sist"]["lines"][index]["SESSmaxEnergySaving"] = metroLine.maximumEnergySavingPossiblePerHour
        inputModel["sist"]["lines"][index]["SESSenergySavingMode"] = metroLine.energySavingMode
        inputModel["sist"]["lines"][index]["SESSpowerLimitFeed"] = metroLine.powerLimitToFeed

        metroStations = metroLine.metrostation_set.all().order_by("id")

        inputModel["sist"]["lines"][index]["stationsMinAuxConsumption"] = np.empty([len(metroStations), 1])
        inputModel["sist"]["lines"][index]["stationsMaxAuxConsumption"] = np.empty([len(metroStations), 1])
        inputModel["sist"]["lines"][index]["stationsMinHVACConsumption"] = np.empty([len(metroStations), 1])
        inputModel["sist"]["lines"][index]["stationsMaxHVACConsumption"] = np.empty([len(metroStations), 1])
        inputModel["sist"]["lines"][index]["stationsTauConsumption"] = np.empty([len(metroStations), 1])

        for i in range(0, len(metroStations)):
            inputModel["sist"]["lines"][index]["stationsMinAuxConsumption"][i] = metroStations[i].minAuxConsumption
            inputModel["sist"]["lines"][index]["stationsMaxAuxConsumption"][i] = metroStations[i].maxAuxConsumption
            inputModel["sist"]["lines"][index]["stationsMinHVACConsumption"][i] = metroStations[
                i].minHVACConsumption
            inputModel["sist"]["lines"][index]["stationsMaxHVACConsumption"][i] = metroStations[
                i].maxHVACConsumption
            inputModel["sist"]["lines"][index]["stationsTauConsumption"][i] = metroStations[i].tau

        metroDepots = metroLine.metrodepot_set.all().order_by("id")

        inputModel["sist"]["lines"][index]["depotsAuxConsumption"] = np.empty(len(metroDepots))
        inputModel["sist"]["lines"][index]["depotsVentConsumption"] = np.empty(len(metroDepots))
        inputModel["sist"]["lines"][index]["depotsDCConsumption"] = np.empty(len(metroDepots))

        for i, metroDepot in enumerate(metroDepots):
            inputModel["sist"]["lines"][index]["depotsAuxConsumption"][i] = metroDepot.auxConsumption
            inputModel["sist"]["lines"][index]["depotsVentConsumption"][i] = metroDepot.ventilationConsumption
            inputModel["sist"]["lines"][index]["depotsDCConsumption"][i] = metroDepot.dcConsumption

        metroTracks = metroLine.metrotrack_set.all().order_by("id")
        inputModel["sist"]["lines"][index]["tracksAuxConsumption"] = np.empty(len(metroTracks))
        inputModel["sist"]["lines"][index]["tracksVentConsumption"] = np.empty(len(metroTracks))
        for i, metroTrack in enumerate(metroTracks):
            inputModel["sist"]["lines"][index]["tracksAuxConsumption"][i] = metroTracks[i].auxiliariesConsumption
            inputModel["sist"]["lines"][index]["tracksVentConsumption"][i] = metroTracks[i].ventilationConsumption

    # OPERATIONAL -------------------------------------------------------------
    # PAGE LINES CHARACTERISTICS ----------------------------------------------

    operationPeriods = scene.operationperiod_set.all().order_by("id")

    inputModel["oper"]["numberHours"] = len(operationPeriods)
    inputModel["oper"]["massPerson"] = scene.averageMassOfAPassanger
    inputModel["oper"]["avTemp"] = scene.annualTemperatureAverage

    inputModel["oper"]["detHours"] = np.empty([len(operationPeriods), 2], dtype="object")
    inputModel["oper"]["tempHours"] = np.empty([len(operationPeriods), 1])
    inputModel["oper"]["humeHours"] = np.empty([len(operationPeriods), 1])
    inputModel["oper"]["CO2"] = np.empty([len(operationPeriods), 1])
    inputModel["oper"]["Rad"] = np.empty([len(operationPeriods), 1])
    inputModel["oper"]["Ele"] = np.empty([len(operationPeriods), 1])

    for i, opPeriod in enumerate(operationPeriods):
        inputModel["oper"]["detHours"][i][0] = opPeriod.start
        inputModel["oper"]["detHours"][i][1] = opPeriod.end
        inputModel["oper"]["tempHours"][i] = opPeriod.temperature
        inputModel["oper"]["humeHours"][i] = opPeriod.humidity
        inputModel["oper"]["CO2"][i] = opPeriod.co2Concentration
        inputModel["oper"]["Rad"][i] = opPeriod.solarRadiation
        inputModel["oper"]["Ele"][i] = opPeriod.sunElevationAngle

    # PAGE PER LINE -----------------------------------------------------------
    inputModel["oper"]["lines"] = defaultdict(dict)
    for i, metroLine in enumerate(metroLines):

        metroStations = metroLine.metrostation_set.all().order_by("id")
        metroTracks = metroLine.metrotrack_set.all().order_by("id")

        nsta = len(metroStations)
        ntra = len(metroTracks)
        nhours = inputModel["oper"]["numberHours"]

        inputModel["oper"]["lines"][i]["ventFl"] = np.empty([nsta, nhours])
        inputModel["oper"]["lines"][i]["passStLR"] = np.empty([nsta, nhours])
        inputModel["oper"]["lines"][i]["passStRL"] = np.empty([nsta, nhours])
        inputModel["oper"]["lines"][i]["dwellLR"] = np.empty([nsta, nhours])
        inputModel["oper"]["lines"][i]["dwellRL"] = np.empty([nsta, nhours])

        inputModel["oper"]["lines"][i]["passLR"] = np.empty([ntra, nhours])
        inputModel["oper"]["lines"][i]["passRL"] = np.empty([ntra, nhours])
        inputModel["oper"]["lines"][i]["maxTimeLR"] = np.empty([ntra, nhours])
        inputModel["oper"]["lines"][i]["maxTimeRL"] = np.empty([ntra, nhours])

        inputModel["oper"]["lines"][i]["frecLR"] = np.empty([nhours, 1])
        inputModel["oper"]["lines"][i]["frecRL"] = np.empty([nhours, 1])

        inputModel["oper"]["lines"][i]["percentajeDCDistLossesLR"] = np.empty([nhours, 1])
        inputModel["oper"]["lines"][i]["percentajeDCDistLossesRL"] = np.empty([nhours, 1])
        inputModel["oper"]["lines"][i]["percentajeACSubstationLossesEntireSystemLR"] = np.empty([nhours, 1])
        inputModel["oper"]["lines"][i]["percentajeACSubstationLossesEntireSystemRL"] = np.empty([nhours, 1])
        inputModel["oper"]["lines"][i]["percentajeACSubstationLossesACSystemLR"] = np.empty([nhours, 1])
        inputModel["oper"]["lines"][i]["percentajeACSubstationLossesACSystemRL"] = np.empty([nhours, 1])
        inputModel["oper"]["lines"][i]["percentajeDCSubstationLossesLR"] = np.empty([nhours, 1])
        inputModel["oper"]["lines"][i]["percentajeDCSubstationLossesRL"] = np.empty([nhours, 1])
        inputModel["oper"]["lines"][i]["receptivity"] = np.empty([nhours, 1])

        for j, metroStation in enumerate(metroStations):
            opMetrics = metroStation.operationperiodformetrostation_set.all().order_by("operationPeriod_id")

            metrics = defaultdict(list)
            for metric in opMetrics:
                metricId = metric.metric + str(metric.direction)
                metrics[metricId].append(metric.value)

            dwellLRId = OperationPeriodForMetroStation.DWELL_TIME + MetroLineMetric.GOING
            dwellRLId = OperationPeriodForMetroStation.DWELL_TIME + MetroLineMetric.REVERSE
            passStLRId = OperationPeriodForMetroStation.PASSENGERS_IN_STATION + MetroLineMetric.GOING
            passStRLId = OperationPeriodForMetroStation.PASSENGERS_IN_STATION + MetroLineMetric.REVERSE
            ventFlId = OperationPeriodForMetroStation.VENTILATION_FLOW + "None"

            inputModel["oper"]["lines"][i]["dwellLR"][j] = metrics[dwellLRId]
            inputModel["oper"]["lines"][i]["dwellRL"][j] = metrics[dwellRLId]
            inputModel["oper"]["lines"][i]["passStLR"][j] = metrics[passStLRId]
            inputModel["oper"]["lines"][i]["passStRL"][j] = metrics[passStRLId]
            inputModel["oper"]["lines"][i]["ventFl"][j] = metrics[ventFlId]

        for j, metroTrack in enumerate(metroTracks):
            opMetrics = metroTrack.operationperiodformetrotrack_set.all().order_by("id")

            metrics = defaultdict(list)
            for metric in opMetrics:
                metricId = metric.metric + metric.direction
                metrics[metricId].append(metric.value)

            passLRId = OperationPeriodForMetroTrack.PASSENGERS_TRAVELING_BETWEEN_STATION + MetroLineMetric.GOING
            passRLId = OperationPeriodForMetroTrack.PASSENGERS_TRAVELING_BETWEEN_STATION + MetroLineMetric.REVERSE
            maxTimeLRId = OperationPeriodForMetroTrack.MAX_TRAVEL_TIME_BETWEEN_STATION + MetroLineMetric.GOING
            maxTimeRLId = OperationPeriodForMetroTrack.MAX_TRAVEL_TIME_BETWEEN_STATION + MetroLineMetric.REVERSE

            inputModel["oper"]["lines"][i]["passLR"][j] = metrics[passLRId]
            inputModel["oper"]["lines"][i]["passRL"][j] = metrics[passRLId]
            inputModel["oper"]["lines"][i]["maxTimeLR"][j] = metrics[maxTimeLRId]
            inputModel["oper"]["lines"][i]["maxTimeRL"][j] = metrics[maxTimeRLId]

        metrics = defaultdict(list)
        for metric in metroLine.operationperiodformetroline_set.all().order_by("operationPeriod_id"):
            metricId = metric.metric + str(metric.direction)
            metrics[metricId].append(metric.value)

        frecLRId = OperationPeriodForMetroLine.FREQUENCY + MetroLineMetric.GOING
        frecRLId = OperationPeriodForMetroLine.FREQUENCY + MetroLineMetric.REVERSE
        percDCDistLossesLRId = OperationPeriodForMetroLine.PERC_DC_DISTRIBUTION_LOSSES + MetroLineMetric.GOING
        percDCDistLossesRLId = OperationPeriodForMetroLine.PERC_DC_DISTRIBUTION_LOSSES + MetroLineMetric.REVERSE
        percACSubstationLossesEntireSystemLRId = OperationPeriodForMetroLine.PERC_AC_SUBSTATION_LOSSES_FEED_ENTIRE_SYSTEM + MetroLineMetric.GOING
        percACSubstationLossesEntireSystemRLId = OperationPeriodForMetroLine.PERC_AC_SUBSTATION_LOSSES_FEED_ENTIRE_SYSTEM + MetroLineMetric.REVERSE
        percACSubstationLossesACSystemLRId = OperationPeriodForMetroLine.PERC_AC_SUBSTATION_LOSSES_FEED_AC_ELEMENTS + MetroLineMetric.GOING
        percACSubstationLossesACSystemRLId = OperationPeriodForMetroLine.PERC_AC_SUBSTATION_LOSSES_FEED_AC_ELEMENTS + MetroLineMetric.REVERSE
        percDCSubstationLossesLRId = OperationPeriodForMetroLine.PERC_DC_SUBSTATION_LOSSES + MetroLineMetric.GOING
        percDCSubstationLossesRLId = OperationPeriodForMetroLine.PERC_DC_SUBSTATION_LOSSES + MetroLineMetric.REVERSE
        receptivityId = OperationPeriodForMetroLine.RECEPTIVITY + "None"

        for j in range(nhours):
            inputModel["oper"]["lines"][i]["frecLR"][j] = metrics[frecLRId][j]
            inputModel["oper"]["lines"][i]["frecRL"][j] = metrics[frecRLId][j]

            inputModel["oper"]["lines"][i]["percentajeDCDistLossesLR"][j] = metrics[percDCDistLossesLRId][j] / 100
            inputModel["oper"]["lines"][i]["percentajeDCDistLossesRL"][j] = metrics[percDCDistLossesRLId][j] / 100
            inputModel["oper"]["lines"][i]["percentajeACSubstationLossesEntireSystemLR"][j] = metrics[
                                                                                                  percACSubstationLossesEntireSystemLRId][
                                                                                                  j] / 100
            inputModel["oper"]["lines"][i]["percentajeACSubstationLossesEntireSystemRL"][j] = metrics[
                                                                                                  percACSubstationLossesEntireSystemRLId][
                                                                                                  j] / 100
            inputModel["oper"]["lines"][i]["percentajeACSubstationLossesACSystemLR"][j] = \
                metrics[percACSubstationLossesACSystemLRId][j] / 100
            inputModel["oper"]["lines"][i]["percentajeACSubstationLossesACSystemRL"][j] = \
                metrics[percACSubstationLossesACSystemRLId][j] / 100
            inputModel["oper"]["lines"][i]["percentajeDCSubstationLossesLR"][j] = \
                metrics[percDCSubstationLossesLRId][j] / 100
            inputModel["oper"]["lines"][i]["percentajeDCSubstationLossesRL"][j] = \
                metrics[percDCSubstationLossesRLId][j] / 100

            inputModel["oper"]["lines"][i]["receptivity"][j] = metrics[receptivityId][j] / 100

    return inputModel