from collections import defaultdict
from scene.models import Scene
from scene.models import MetroLineMetric, OperationPeriodForMetroStation, OperationPeriodForMetroTrack, \
    OperationPeriodForMetroLine

import numpy as np


def first_input(scene_id):
    """ make input data for speed model """

    scene = Scene.objects.prefetch_related("metroline_set__metrostation_set__operationperiodformetrostation_set",
                                           "metroline_set__metrodepot_set",
                                           "metroline_set__metrolinemetric_set",
                                           "metroline_set__metrotrack_set__operationperiodformetrotrack_set",
                                           "metroline_set__operationperiodformetroline_set",
                                           "metroconnection_set__metroconnectionstation_set__metroStation",
                                           "systemicparams_set").get(id=scene_id)

    input_model = {"oper": {}, "top": {}, "sist": {}}

    line_number = scene.metroline_set.all().count()
    connection_number = scene.metroconnection_set.all().count()

    metro_connections = scene.metroconnection_set.all().order_by("id")
    metro_lines = scene.metroline_set.all().order_by("id")

    input_model["top"]["nLines"] = line_number
    input_model["top"]["nConnections"] = connection_number

    input_model["top"]["nStations"] = np.empty([line_number, 1], dtype=np.int32)
    input_model["top"]["nDepots"] = [0] * line_number  # np.empty([lineNumber, 1])
    for index, line in enumerate(metro_lines):
        input_model["top"]["nStations"][index] = len(line.metrostation_set.all())
        input_model["top"]["nDepots"][index] = len(line.metrodepot_set.all())

    if connection_number:
        con_stations = [[None], [None]] * connection_number
        for i in range(0, connection_number):
            for j, metro_connection_station in enumerate(
                    metro_connections[i].metroconnectionstation_set.all().order_by("id")):
                con_stations[j][i] = metro_connection_station.metroStation.name
        input_model["top"]["connections.stations"] = con_stations

        input_model["top"]["connections.avHeight"] = np.empty([connection_number, 1])
        input_model["top"]["connections.f2Height"] = np.empty([connection_number, 1])
        for i in range(0, connection_number):
            input_model["top"]["connections.avHeight"][i] = metro_connections[i].avgHeight
            input_model["top"]["connections.f2Height"][i] = metro_connections[i].avgSurface
    else:
        input_model["top"]["connections.stations"] = []
        input_model["top"]["connections.avHeight"] = []
        input_model["top"]["connections.f2Height"] = []

    # PAGE PER LINE -----------------------------------------------------------
    input_model["top"]["lines"] = defaultdict(dict)
    for index, metro_line in enumerate(metro_lines):
        input_model["top"]["lines"][index]["geometry"] = defaultdict(dict)

        metrics = defaultdict(list)
        for metric in metro_line.metrolinemetric_set.all().order_by("id"):
            metric_id = metric.metric + str(metric.direction)
            metrics[metric_id].append([metric.start, metric.end, metric.value])

        slope_lr_id = MetroLineMetric.SLOPE + MetroLineMetric.GOING
        slope_lr = np.zeros([len(metrics[slope_lr_id]), 3])
        for i in range(len(metrics[slope_lr_id])):
            slope_lr[i, 0] = metrics[slope_lr_id][i][0]  # start
            slope_lr[i, 1] = metrics[slope_lr_id][i][1]  # end
            slope_lr[i, 2] = metrics[slope_lr_id][i][2]  # value

        slope_rl_id = MetroLineMetric.SLOPE + MetroLineMetric.REVERSE
        slope_rl = np.zeros([len(metrics[slope_rl_id]), 3])
        for i in range(len(metrics[slope_rl_id])):
            slope_rl[i, 0] = metrics[slope_rl_id][i][0]  # start
            slope_rl[i, 1] = metrics[slope_rl_id][i][1]  # end
            slope_rl[i, 2] = metrics[slope_rl_id][i][2]  # value

        input_model["top"]["lines"][index]["geometry"]["SlopeLR"] = slope_lr
        input_model["top"]["lines"][index]["geometry"]["SlopeRL"] = slope_rl

        curve_lr_id = MetroLineMetric.CURVE_RADIUS + MetroLineMetric.GOING
        curve_lr = np.zeros([len(metrics[curve_lr_id]), 3])
        for i in range(len(metrics[curve_lr_id])):
            curve_lr[i, 0] = metrics[curve_lr_id][i][0]  # start
            curve_lr[i, 1] = metrics[curve_lr_id][i][1]  # end
            curve_lr[i, 2] = metrics[curve_lr_id][i][2]  # value

        curve_rl_id = MetroLineMetric.CURVE_RADIUS + MetroLineMetric.REVERSE
        curve_rl = np.zeros([len(metrics[curve_rl_id]), 3])
        for i in range(len(metrics[curve_rl_id])):
            curve_rl[i, 0] = metrics[curve_rl_id][i][0]  # start
            curve_rl[i, 1] = metrics[curve_rl_id][i][1]  # end
            curve_rl[i, 2] = metrics[curve_rl_id][i][2]  # value

        input_model["top"]["lines"][index]["geometry"]["CurvLR"] = curve_lr
        input_model["top"]["lines"][index]["geometry"]["CurvRL"] = curve_rl

        speed_limit_lr_id = MetroLineMetric.SPEED_LIMIT + MetroLineMetric.GOING
        speed_limit_lr = np.zeros([len(metrics[speed_limit_lr_id]), 3])
        for i in range(len(metrics[speed_limit_lr_id])):
            speed_limit_lr[i, 0] = metrics[speed_limit_lr_id][i][0]  # start
            speed_limit_lr[i, 1] = metrics[speed_limit_lr_id][i][1]  # end
            speed_limit_lr[i, 2] = metrics[speed_limit_lr_id][i][2]  # value

        speed_limit_rl_id = MetroLineMetric.SPEED_LIMIT + MetroLineMetric.REVERSE
        speed_limit_rl = np.zeros([len(metrics[speed_limit_rl_id]), 3])
        for i in range(len(metrics[speed_limit_rl_id])):
            speed_limit_rl[i, 0] = metrics[speed_limit_rl_id][i][0]  # start
            speed_limit_rl[i, 1] = metrics[speed_limit_rl_id][i][1]  # end
            speed_limit_rl[i, 2] = metrics[speed_limit_rl_id][i][2]  # value

        input_model["top"]["lines"][index]["geometry"]["SpBoundsLR"] = speed_limit_lr
        input_model["top"]["lines"][index]["geometry"]["SpBoundsRL"] = speed_limit_rl

        ground_id = MetroLineMetric.GROUND + "None"
        grounds = np.zeros([len(metrics[ground_id]), 3])
        for i in range(len(metrics[ground_id])):
            grounds[i, 0] = metrics[ground_id][i][0]  # start
            grounds[i, 1] = metrics[ground_id][i][1]  # end
            grounds[i, 2] = metrics[ground_id][i][2]  # value

        ground_by_meter = np.empty([int(grounds[-1][1]), 2])
        for ground in grounds:
            i0 = round(ground[0]) + 1
            i1 = round(ground[1]) - 1
            for i in range(int(i0), int(i1)):
                ground_by_meter[i] = [i, ground[2]]
        input_model["top"]["lines"][index]["geometry"]["underabove"] = ground_by_meter

        metro_tracks = metro_line.metrotrack_set.all().order_by("id")
        metro_stations = metro_line.metrostation_set.all().order_by("id")

        input_model["top"]["lines"][index]["stations"] = {}
        input_model["top"]["lines"][index]["tracks"] = {}
        input_model["top"]["lines"][index]["stations"]["length"] = np.empty([len(metro_stations), 1])
        input_model["top"]["lines"][index]["stations"]["f2avHeight"] = np.empty([len(metro_stations), 1])
        input_model["top"]["lines"][index]["stations"]["f2surfHeight"] = np.empty([len(metro_stations), 1])
        input_model["top"]["lines"][index]["stations"]["platSection"] = np.empty([len(metro_stations), 1])
        input_model["top"]["lines"][index]["stations"]["platAvPerim"] = np.empty([len(metro_stations), 1])
        input_model["top"]["lines"][index]["tracks"]["length"] = np.empty([len(metro_tracks), 1])
        input_model["top"]["lines"][index]["tracks"]["crossSection"] = np.empty([len(metro_tracks), 1])
        input_model["top"]["lines"][index]["tracks"]["avPerim"] = np.empty([len(metro_tracks), 1])

        for i, metro_station in enumerate(metro_stations):
            input_model["top"]["lines"][index]["stations"]["length"][i] = metro_station.length
            input_model["top"]["lines"][index]["stations"]["f2avHeight"][i] = metro_station.secondLevelAverageHeight
            input_model["top"]["lines"][index]["stations"]["f2surfHeight"][i] = metro_station.secondLevelFloorSurface
            input_model["top"]["lines"][index]["stations"]["platSection"][i] = metro_station.platformSection
            input_model["top"]["lines"][index]["stations"]["platAvPerim"][i] = metro_station.platformAveragePerimeter

        for i, metro_track in enumerate(metro_tracks):
            input_model["top"]["lines"][index]["tracks"]["length"][i] = metro_track.length
            input_model["top"]["lines"][index]["tracks"]["crossSection"][i] = metro_track.crossSection
            input_model["top"]["lines"][index]["tracks"]["avPerim"][i] = metro_track.averagePerimeter

    # SYSTEMIC ----------------------------------------------------------------
    # PAGE LINES CHARACTERISTICS ----------------------------------------------
    sys = scene.systemicparams_set.all()[0]

    input_model["sist"]["trainMass"] = sys.mass
    input_model["sist"]["inercialMass"] = sys.inercialMass
    input_model["sist"]["maxAcc"] = sys.maxAccelerationAllowed
    input_model["sist"]["maxStartForce"] = sys.maxStartingForceAllowed
    input_model["sist"]["maxBrakeForce"] = sys.maxBrakingForceAllowed
    input_model["sist"]["regimeChange"] = sys.speedOfMotorRegimeChange
    input_model["sist"]["maxPower"] = sys.maxPower
    input_model["sist"]["maxSpeed"] = sys.maxSpeedAllowed

    input_model["sist"]["Davis"] = {}
    input_model["sist"]["Davis"]["A"] = sys.davisParameterA
    input_model["sist"]["Davis"]["B"] = sys.davisParameterB
    input_model["sist"]["Davis"]["C"] = sys.davisParameterC
    input_model["sist"]["Davis"]["D"] = sys.davisParameterD
    input_model["sist"]["Davis"]["E"] = sys.davisParameterE

    input_model["sist"]["tractEff"] = sys.tractionSystemEfficiency / 100
    input_model["sist"]["brakeEff"] = sys.brakingSystemEfficiency / 100
    # inputModel["sist"]["receptivity"] = fslc(15+1,1)
    input_model["sist"]["electBrakeT.p1"] = sys.electricalBrakeTreshold
    input_model["sist"]["electBrakeT.p2"] = sys.electroMechanicalBrakeThreshold
    # --------------------------------------------------------------

    input_model["sist"]["trainHVACConsumption"] = sys.hvacConsumption
    input_model["sist"]["trainAuxConsumption"] = sys.auxiliariesConsumption
    input_model["sist"]["trainTerminalsResistence"] = sys.trainsTerminalResistance
    input_model["sist"]["trainPotencial"] = sys.voltageDCTrainsTerminals

    input_model["sist"]["trainLength"] = sys.length
    input_model["sist"]["trainCars"] = sys.numberOfCars
    input_model["sist"]["car_width"] = sys.carWidth
    input_model["sist"]["car_height"] = sys.carHeight
    input_model["sist"]["car_thick"] = sys.vehicleWallThickness
    input_model["sist"]["car_lambda"] = sys.heatConductivityOfTheVehicleWall
    input_model["sist"]["car_factor"] = sys.cabinVolumeFactor
    input_model["sist"]["passenger_capacity"] = sys.trainPassengerCapacity

    set_points = np.zeros([5, 2])
    set_points[0, 0] = sys.point1Tin
    set_points[0, 1] = sys.point1Tout
    set_points[1, 0] = sys.point2Tin
    set_points[1, 1] = sys.point2Tout
    set_points[2, 0] = sys.point3Tin
    set_points[2, 1] = sys.point3Tout
    set_points[3, 0] = sys.point4Tin
    set_points[3, 1] = sys.point4Tout
    set_points[4, 0] = sys.point5Tin
    set_points[4, 1] = sys.point5Tout

    input_model["sist"]["SetPoints"] = set_points

    input_model["sist"]["ExtraPowerHRS"] = sys.hrsExtraPower
    input_model["sist"]["isOBESS"] = sys.onBoardEnergyStorageSystem
    input_model["sist"]["OBESScapacity"] = sys.storageCapacityWeighting

    # ###CMM traction####
    input_model["sist"]["charge_eff"] = sys.obessChargeEfficiency / 100
    input_model["sist"]["discharge_eff"] = sys.obessDischargeEfficiency / 100
    input_model["sist"]["OBESS_usable"] = sys.obessUsableEnergyContent
    input_model["sist"]["OBESS_peak_power"] = sys.maxDischargePower
    input_model["sist"]["OBESS_max_saving"] = sys.maxEnergySavingPossiblePerHour
    input_model["sist"]["OBESS_power_limit"] = sys.powerLimitToFeed

    aux = np.array([])
    for metro_connection in metro_connections:
        aux = np.append(aux, metro_connection.consumption)
    input_model["sist"]["interConsumption"] = aux

    # PAGE PER LINE -----------------------------------------------------------
    input_model["sist"]["lines"] = defaultdict(dict)
    for index, metro_line in enumerate(metro_lines):

        input_model["sist"]["lines"][index]["SESSusableEnergyContent"] = metro_line.usableEnergyContent
        input_model["sist"]["lines"][index]["SESSchargingEfficiency"] = metro_line.chargingEfficiency
        input_model["sist"]["lines"][index]["SESSdischargingEfficiency"] = metro_line.dischargingEfficiency
        input_model["sist"]["lines"][index]["SESSpeakPower"] = metro_line.peakPower
        input_model["sist"]["lines"][index]["SESSmaxEnergySaving"] = metro_line.maximumEnergySavingPossiblePerHour
        input_model["sist"]["lines"][index]["SESSenergySavingMode"] = metro_line.energySavingMode
        input_model["sist"]["lines"][index]["SESSpowerLimitFeed"] = metro_line.powerLimitToFeed

        metro_stations = metro_line.metrostation_set.all().order_by("id")

        input_model["sist"]["lines"][index]["stationsMinAuxConsumption"] = np.empty([len(metro_stations), 1])
        input_model["sist"]["lines"][index]["stationsMaxAuxConsumption"] = np.empty([len(metro_stations), 1])
        input_model["sist"]["lines"][index]["stationsMinHVACConsumption"] = np.empty([len(metro_stations), 1])
        input_model["sist"]["lines"][index]["stationsMaxHVACConsumption"] = np.empty([len(metro_stations), 1])
        input_model["sist"]["lines"][index]["stationsTauConsumption"] = np.empty([len(metro_stations), 1])

        for i in range(0, len(metro_stations)):
            input_model["sist"]["lines"][index]["stationsMinAuxConsumption"][i] = metro_stations[i].minAuxConsumption
            input_model["sist"]["lines"][index]["stationsMaxAuxConsumption"][i] = metro_stations[i].maxAuxConsumption
            input_model["sist"]["lines"][index]["stationsMinHVACConsumption"][i] = metro_stations[
                i].minHVACConsumption
            input_model["sist"]["lines"][index]["stationsMaxHVACConsumption"][i] = metro_stations[
                i].maxHVACConsumption
            input_model["sist"]["lines"][index]["stationsTauConsumption"][i] = metro_stations[i].tau

        metro_depots = metro_line.metrodepot_set.all().order_by("id")

        input_model["sist"]["lines"][index]["depotsAuxConsumption"] = np.empty(len(metro_depots))
        input_model["sist"]["lines"][index]["depotsVentConsumption"] = np.empty(len(metro_depots))
        input_model["sist"]["lines"][index]["depotsDCConsumption"] = np.empty(len(metro_depots))

        for i, metroDepot in enumerate(metro_depots):
            input_model["sist"]["lines"][index]["depotsAuxConsumption"][i] = metroDepot.auxConsumption
            input_model["sist"]["lines"][index]["depotsVentConsumption"][i] = metroDepot.ventilationConsumption
            input_model["sist"]["lines"][index]["depotsDCConsumption"][i] = metroDepot.dcConsumption

        metro_tracks = metro_line.metrotrack_set.all().order_by("id")
        input_model["sist"]["lines"][index]["tracksAuxConsumption"] = np.empty(len(metro_tracks))
        input_model["sist"]["lines"][index]["tracksVentConsumption"] = np.empty(len(metro_tracks))
        for i, metro_track in enumerate(metro_tracks):
            input_model["sist"]["lines"][index]["tracksAuxConsumption"][i] = metro_tracks[i].auxiliariesConsumption
            input_model["sist"]["lines"][index]["tracksVentConsumption"][i] = metro_tracks[i].ventilationConsumption

    # OPERATIONAL -------------------------------------------------------------
    # PAGE LINES CHARACTERISTICS ----------------------------------------------

    operation_periods = scene.operationperiod_set.all().order_by("id")

    input_model["oper"]["numberHours"] = len(operation_periods)
    input_model["oper"]["massPerson"] = scene.averageMassOfAPassanger
    input_model["oper"]["avTemp"] = scene.annualTemperatureAverage

    input_model["oper"]["detHours"] = np.empty([len(operation_periods), 2], dtype="object")
    input_model["oper"]["tempHours"] = np.empty([len(operation_periods), 1])
    input_model["oper"]["humeHours"] = np.empty([len(operation_periods), 1])
    input_model["oper"]["CO2"] = np.empty([len(operation_periods), 1])
    input_model["oper"]["Rad"] = np.empty([len(operation_periods), 1])
    input_model["oper"]["Ele"] = np.empty([len(operation_periods), 1])

    for i, opPeriod in enumerate(operation_periods):
        input_model["oper"]["detHours"][i][0] = opPeriod.start
        input_model["oper"]["detHours"][i][1] = opPeriod.end
        input_model["oper"]["tempHours"][i] = opPeriod.temperature
        input_model["oper"]["humeHours"][i] = opPeriod.humidity
        input_model["oper"]["CO2"][i] = opPeriod.co2Concentration
        input_model["oper"]["Rad"][i] = opPeriod.solarRadiation
        input_model["oper"]["Ele"][i] = opPeriod.sunElevationAngle

    # PAGE PER LINE -----------------------------------------------------------
    input_model["oper"]["lines"] = defaultdict(dict)
    for i, metro_line in enumerate(metro_lines):

        metro_stations = metro_line.metrostation_set.all().order_by("id")
        metro_tracks = metro_line.metrotrack_set.all().order_by("id")

        nsta = len(metro_stations)
        ntra = len(metro_tracks)
        nhours = input_model["oper"]["numberHours"]

        input_model["oper"]["lines"][i]["ventFl"] = np.empty([nsta, nhours])
        input_model["oper"]["lines"][i]["passStLR"] = np.empty([nsta, nhours])
        input_model["oper"]["lines"][i]["passStRL"] = np.empty([nsta, nhours])
        input_model["oper"]["lines"][i]["dwellLR"] = np.empty([nsta, nhours])
        input_model["oper"]["lines"][i]["dwellRL"] = np.empty([nsta, nhours])

        input_model["oper"]["lines"][i]["passLR"] = np.empty([ntra, nhours])
        input_model["oper"]["lines"][i]["passRL"] = np.empty([ntra, nhours])
        input_model["oper"]["lines"][i]["maxTimeLR"] = np.empty([ntra, nhours])
        input_model["oper"]["lines"][i]["maxTimeRL"] = np.empty([ntra, nhours])

        input_model["oper"]["lines"][i]["frecLR"] = np.empty([nhours, 1])
        input_model["oper"]["lines"][i]["frecRL"] = np.empty([nhours, 1])

        input_model["oper"]["lines"][i]["percentajeDCDistLossesLR"] = np.empty([nhours, 1])
        input_model["oper"]["lines"][i]["percentajeDCDistLossesRL"] = np.empty([nhours, 1])
        input_model["oper"]["lines"][i]["percentajeACSubstationLossesEntireSystemLR"] = np.empty([nhours, 1])
        input_model["oper"]["lines"][i]["percentajeACSubstationLossesEntireSystemRL"] = np.empty([nhours, 1])
        input_model["oper"]["lines"][i]["percentajeACSubstationLossesACSystemLR"] = np.empty([nhours, 1])
        input_model["oper"]["lines"][i]["percentajeACSubstationLossesACSystemRL"] = np.empty([nhours, 1])
        input_model["oper"]["lines"][i]["percentajeDCSubstationLossesLR"] = np.empty([nhours, 1])
        input_model["oper"]["lines"][i]["percentajeDCSubstationLossesRL"] = np.empty([nhours, 1])
        input_model["oper"]["lines"][i]["receptivity"] = np.empty([nhours, 1])

        for j, metro_station in enumerate(metro_stations):
            op_metrics = metro_station.operationperiodformetrostation_set.all().order_by("operationPeriod_id")

            metrics = defaultdict(list)
            for metric in op_metrics:
                metric_id = metric.metric + str(metric.direction)
                metrics[metric_id].append(metric.value)

            dwell_lr_id = OperationPeriodForMetroStation.DWELL_TIME + MetroLineMetric.GOING
            dwell_rl_id = OperationPeriodForMetroStation.DWELL_TIME + MetroLineMetric.REVERSE
            pass_st_lr_id = OperationPeriodForMetroStation.PASSENGERS_IN_STATION + MetroLineMetric.GOING
            pass_st_rl_id = OperationPeriodForMetroStation.PASSENGERS_IN_STATION + MetroLineMetric.REVERSE
            vent_fl_id = OperationPeriodForMetroStation.VENTILATION_FLOW + "None"

            input_model["oper"]["lines"][i]["dwellLR"][j] = metrics[dwell_lr_id]
            input_model["oper"]["lines"][i]["dwellRL"][j] = metrics[dwell_rl_id]
            input_model["oper"]["lines"][i]["passStLR"][j] = metrics[pass_st_lr_id]
            input_model["oper"]["lines"][i]["passStRL"][j] = metrics[pass_st_rl_id]
            input_model["oper"]["lines"][i]["ventFl"][j] = metrics[vent_fl_id]

        for j, metro_track in enumerate(metro_tracks):
            op_metrics = metro_track.operationperiodformetrotrack_set.all().order_by("id")

            metrics = defaultdict(list)
            for metric in op_metrics:
                metric_id = metric.metric + metric.direction
                metrics[metric_id].append(metric.value)

            pass_lr_id = OperationPeriodForMetroTrack.PASSENGERS_TRAVELING_BETWEEN_STATION + MetroLineMetric.GOING
            pass_rl_id = OperationPeriodForMetroTrack.PASSENGERS_TRAVELING_BETWEEN_STATION + MetroLineMetric.REVERSE
            max_time_lr_id = OperationPeriodForMetroTrack.MAX_TRAVEL_TIME_BETWEEN_STATION + MetroLineMetric.GOING
            max_time_rl_id = OperationPeriodForMetroTrack.MAX_TRAVEL_TIME_BETWEEN_STATION + MetroLineMetric.REVERSE

            input_model["oper"]["lines"][i]["passLR"][j] = metrics[pass_lr_id]
            input_model["oper"]["lines"][i]["passRL"][j] = metrics[pass_rl_id]
            input_model["oper"]["lines"][i]["maxTimeLR"][j] = metrics[max_time_lr_id]
            input_model["oper"]["lines"][i]["maxTimeRL"][j] = metrics[max_time_rl_id]

        metrics = defaultdict(list)
        for metric in metro_line.operationperiodformetroline_set.all().order_by("operationPeriod_id"):
            metric_id = metric.metric + str(metric.direction)
            metrics[metric_id].append(metric.value)

        frec_lr_id = OperationPeriodForMetroLine.FREQUENCY + MetroLineMetric.GOING
        frec_rl_id = OperationPeriodForMetroLine.FREQUENCY + MetroLineMetric.REVERSE
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
            input_model["oper"]["lines"][i]["frecLR"][j] = metrics[frec_lr_id][j]
            input_model["oper"]["lines"][i]["frecRL"][j] = metrics[frec_rl_id][j]

            input_model["oper"]["lines"][i]["percentajeDCDistLossesLR"][j] = metrics[percDCDistLossesLRId][j] / 100
            input_model["oper"]["lines"][i]["percentajeDCDistLossesRL"][j] = metrics[percDCDistLossesRLId][j] / 100
            input_model["oper"]["lines"][i]["percentajeACSubstationLossesEntireSystemLR"][j] = metrics[
                                                                                                  percACSubstationLossesEntireSystemLRId][
                                                                                                  j] / 100
            input_model["oper"]["lines"][i]["percentajeACSubstationLossesEntireSystemRL"][j] = metrics[
                                                                                                  percACSubstationLossesEntireSystemRLId][
                                                                                                  j] / 100
            input_model["oper"]["lines"][i]["percentajeACSubstationLossesACSystemLR"][j] = \
                metrics[percACSubstationLossesACSystemLRId][j] / 100
            input_model["oper"]["lines"][i]["percentajeACSubstationLossesACSystemRL"][j] = \
                metrics[percACSubstationLossesACSystemRLId][j] / 100
            input_model["oper"]["lines"][i]["percentajeDCSubstationLossesLR"][j] = \
                metrics[percDCSubstationLossesLRId][j] / 100
            input_model["oper"]["lines"][i]["percentajeDCSubstationLossesRL"][j] = \
                metrics[percDCSubstationLossesRLId][j] / 100

            input_model["oper"]["lines"][i]["receptivity"][j] = metrics[receptivityId][j] / 100

    return input_model
