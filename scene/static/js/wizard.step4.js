"use strict";

/**************************************************
* STEP 4
***************************************************/
let OperationPeriod = function (internalId) {
    let self = this;
    self.id = ko.observable();
    self.name = ko.observable();
    self.start = ko.observable();
    self.end = ko.observable();

    // ambient condition
    self.temperature = ko.observable();
    self.humidity = ko.observable();
    self.co2Concentration = ko.observable();
    self.solarRadiation = ko.observable();
    self.sunElevationAngle= ko.observable();

    // to track editions
    internalId = internalId || null;
    self.internalId = ko.observable(internalId);
};

let Step4ViewModel = function () {
    let self = this;

    // general characteristics
    self.averageMassOfAPassanger = ko.observable();
    self.annualTemperatureAverage = ko.observable();

    self.operationPeriods = ko.observableArray();

    /**************************************************
     * LOGIC TO ADD TIME PERIOD
     *************************************************/
    self.showDialog = ko.observable(false);
    // record used to edit
    self.record = new OperationPeriod();
    // copy attributes from one object to another
    self.copyAttr = function(originObj, destObj){
        for(let attr in originObj){
            destObj[attr](originObj[attr]());
        }
    };

    // button name in dialog
    self.dialogButton = ko.observable();
    // open dialog to add new operation period
    self.openAddRecordForm = function (){
        // clean form
        for(let attr in self.record){
            self.record[attr](null);
        }
        let periodsNumber = self.operationPeriods().length;
        if(periodsNumber){
            self.record["start"](self.operationPeriods()[periodsNumber-1]["end"]());
        }
        self.dialogButton("Crear");
        self.showDialog(true);
    };
    // save new data (create or edit)
    self.addOperationPeriod = function () {
        if (self.isValidOperationPeriodForm()){
            let internalId = self.record.internalId();
            if (internalId === null){
                // create element
                let newRecord = new OperationPeriod(self.getInternalId());
                self.copyAttr(self.record, newRecord);
                self.operationPeriods.push(newRecord);
            }else{
                // update element
                let row = self.operationPeriods().filter(el => el.internalId() === internalId)[0];
                self.copyAttr(self.record, row);
            }
            self.showDialog(false);
        }
    };
    self.removeOperationPeriod = function(){
        self.operationPeriods.remove(this);
    };

    /**************************************************
     * LOGIC TO EDIT TIME PERIOD
     *************************************************/
    self.lastInternalIdGiven = 1;
    self.getInternalId = function(){
        return self.lastInternalIdGiven++;
    };
    self.openEditOperationPeriodForm = function () {
        self.copyAttr(this, self.record);
        self.dialogButton("Guardar");
        self.showDialog(true);
    };

    /**************************************************
     * FORM VALIDATION
     *************************************************/
    self.isValidName = function(name, errorMessage){
        let reasons = [];
        if (name === undefined || name === null || name === "" || !name.length) {
            reasons.push(errorMessage);
        }
        if (name !== null && name !== undefined) {
            let characterQuantity = 50;
            if (name.length > characterQuantity) {
                reasons.push("El campo no puede tener un largo mayor a " + characterQuantity + " caracteres.");
            }
        }
        return reasons;
    };
    self.isValidNumber = function(value, errorMessage, minValue, maxValue) {
        let reasons = [];
        if (isNaN(value) || value < minValue && maxValue < value) {
            reasons.push(errorMessage.replace("{0}", minValue).replace("{1}", maxValue));
        }
        return reasons;
    };
    self.isValidOperationPeriodForm = function () {
        let operationPeriod = self.record;

        let reasons = [];

        let name = operationPeriod.name();
        let start = operationPeriod.start();
        let end = operationPeriod.end();
        let temperature = operationPeriod.temperature();
        let humidity = operationPeriod.humidity();
        let co2Concentration = operationPeriod.co2Concentration();
        let solarRadiation = operationPeriod.solarRadiation();
        let sunElevationAngle = operationPeriod.sunElevationAngle();

        reasons = reasons.concat(self.isValidName(name, "El nombre no puede ser vacío."));
        reasons = reasons.concat(self.isValidName(start, "La hora de inicio no puede ser vacía."));
        reasons = reasons.concat(self.isValidName(end, "La hora de fin no puede ser vacía."));
        reasons = reasons.concat(self.isValidNumber(temperature, "La temperatura estar entre {0} y {1} °C", 0, 500));
        reasons = reasons.concat(self.isValidNumber(humidity, "La humidad debe estar entre {0} y {1} %", 0, 100));
        reasons = reasons.concat(self.isValidNumber(co2Concentration, "La concentración de CO<sub>2</sub> debe estar entre {0} y {1} ppm.", 0, 1000));
        reasons = reasons.concat(self.isValidNumber(solarRadiation, "La radiación solar debe estar entre {0} y {1} W/m<sup>2<sup>", 0, 500));
        reasons = reasons.concat(self.isValidNumber(sunElevationAngle, "El ángulo de elevación del sol debe estar entre {0}° y {1}°", 0, 500));

        let response = true;
        if(reasons.length){
            self.showWarningList(reasons);
            response = false;
        }
        return response;
    };

    /**************************************************
     * VALIDATION LOGIC
     ***************************************************/
    self.showWarningList = function (reasons) {
        let message = "Hemos detectado los siguientes problemas:";
        message += "<ul>";
        for(let i = 0; i < reasons.length; i++){
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
    self.serialize = function(){
        let serialize = {
            averageMassOfAPassanger: self.averageMassOfAPassanger(),
            annualTemperatureAverage: self.annualTemperatureAverage(),
            operationPeriods: self.operationPeriods()
        };
        return ko.toJSON(serialize);
    };

    self.isValid = function () {
        let msg = {
            message: "",
            title: "Error",
            type: "error"
        };

        // exist lines
        if (self.operationPeriods().length === 0) {
            msg["message"] += "- Debe ingresar uno o más períodos.<br />";
        }

        if (msg["message"] !== "") {
            showNotificationMessage(msg);
            return false;
        }
        return true;
    };

    self.update = function (data) {
        let operationData = data["operation"];

        self.averageMassOfAPassanger(operationData["averageMassOfAPassanger"]);
        self.annualTemperatureAverage(operationData["annualTemperatureAverage"]);

        let operationPeriods = operationData["periods"];
        self.operationPeriods.removeAll();
        operationPeriods.forEach(function(el){
            let operationPeriod = new OperationPeriod(self.getInternalId());
            for(let attr in el) {
                operationPeriod[attr](el[attr]);
            }
            self.operationPeriods.push(operationPeriod);
        });
    }
};