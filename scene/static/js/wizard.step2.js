"use strict";

/**************************************************
* STEP 2
***************************************************/

let TrainForces = function () {
    let self = this;
    self.mass = null;
    self.inercialMass = null;
    self.maxAccelerationAllowed = null;
    self.maxStartingForceAllowed = null;
    self.maxBrakingForceAllowed = null;
    self.speedOfMotorRegimeChange = null;
    self.maxPower = null;
    self.maxSpeedAllowed = null;

    self.davisParameterA = null;
    self.davisParameterB = null;
    self.davisParameterC = null;
    self.davisParameterD = null;
    self.davisParameterE = null;
};

let TrainTraction = function(){
    let self = this;
    self.tractionSystemEfficiency = ko.observable();
    self.brakingSystemEfficiency = ko.observable();
    self.electricalBrakeTreshold = ko.observable();
    self.electroMechanicalBrakeThreshold = ko.observable();
};

let TrainStructure = function(){
    let self = this;
    self.length = ko.observable();
    self.numberOfCars = ko.observable();
    self.carWidth = ko.observable();
    self.carHeight = ko.observable();
    self.vehicleWallThickness = ko.observable();
    self.heatConductivityOfTheVehicleWall = ko.observable();
    self.cabinVolumeFactor = ko.observable();
    self.trainPassengerCapacity = ko.observable();
    // HVAC set points
    self.point1Tin = ko.observable();
    self.point2Tin = ko.observable();
    self.point3Tin = ko.observable();
    self.point4Tin = ko.observable();
    self.point5Tin = ko.observable();
    self.point1Tout = ko.observable();
    self.point2Tout = ko.observable();
    self.point3Tout = ko.observable();
    self.point4Tout = ko.observable();
    self.point5Tout = ko.observable();

    self.hrsExtraPower = ko.observable();
    self.onBoardEnergyStorageSystem = ko.observable();
    self.storageCapacityWeighting = ko.observable();
};
let TrainCMMTractionModel = function(){
    let self = this;
    self.obessChargeEfficiency = ko.observable();
    self.obessDischargeEfficiency = ko.observable();
    self.obessUsableEnergyContent = ko.observable();
    self.maxDischargePower = ko.observable();
    self.maxEnergySavingPossiblePerHour = ko.observable();
    self.powerLimitToFeed = ko.observable();
};
let TrainEnergy = function(){
    let self = this;
    self.hvacConsumption = ko.observable();
    self.auxiliariesConsumption = ko.observable();
    self.trainsTerminalResistance = ko.observable();
    self.voltageDCTrainsTerminals = ko.observable();
};

let Step2ViewModel = function () {
    let self = this;

    self.trainForces = new TrainForces();
    self.trainTraction = new TrainTraction();
    self.trainStructure = new TrainStructure();
    self.trainCMMTractionModel = new TrainCMMTractionModel();
    self.trainEnergy = new TrainEnergy();

    self.connections = ko.observableArray();

    /**************************************************
     * VALIDATION LOGIC
     ***************************************************/
    self.showWarningList = function (reasons) {
        let message = "Hemos detectado los siguientes problemas:";
        message += "<ul>";
        for (let i = 0; i < reasons.length; i++) {
            message += "<li>" + reasons[i] + "</li>";
        }
        message += "</ul>";

        self.showMessage(message, "Advertencia", "warning");
    };

    self.showMessage = function (message, title, type) {
        let msg = {
            message: message,
            title: title,
            type: type
        };
        showNotificationMessage(msg);
    };

    /**************************************************
     * EXTERNAL VALIDATION LOGIC
     ***************************************************/
    self.serialize = function () {
        let systemicParams = Object.assign({}, self.trainForces, self.trainTraction, self.trainStructure,
            self.trainCMMTractionModel, self.trainEnergy);
        let serialize = {
            systemicParams: systemicParams,
            connections: self.connections
        };
        return ko.toJSON(serialize);
    };

    self.isValid = function () {
        let msg = {
            message: "",
            title: "Error",
            type: "error"
        };

        if (msg["message"] !== "") {
            showNotificationMessage(msg);
            return false;
        }
        return true;
    };

    self.update = function (data) {
        let connections = data['connections'];
        let sysParams = data['systemicParams'];

        let trainForces = new TrainForces();
        for(let attr in trainForces){
            trainForces[attr] = sysParams[attr];
        }
        let trainTraction = new TrainTraction();
        for(let attr in trainTraction){
            trainTraction[attr](sysParams[attr]);
        }
        let trainStructure = new TrainStructure();
        for(let attr in trainStructure){
            trainStructure[attr](sysParams[attr])
        }
        let trainCMMTractionModel = new TrainCMMTractionModel();
        for(let attr in trainCMMTractionModel){
            trainCMMTractionModel[attr](sysParams[attr])
        }
        let trainEnergy = new TrainEnergy();
        for(let attr in trainEnergy){
            trainEnergy[attr](sysParams[attr])
        }

        self.trainForces = trainForces;
        self.trainTraction = trainTraction;
        self.trainStructure = trainStructure;
        self.trainCMMTractionModel = trainCMMTractionModel;
        self.trainEnergy = trainEnergy;

        self.connections.removeAll();
        connections.forEach(function (el) {
            let connection = {
                id: el.id,
                consumption: el.consumption
            };

            let description = [];
            let separator = "<i class='fa fa-arrows-h fa-lg' aria-hidden='true'></i>";
            el.stations.forEach(function (connStation) {
                description.push(connStation.station.lineName + "-" + connStation.station.name);
            });
            connection.description = description.join(separator);
            self.connections.push(connection);
        });
    }
};