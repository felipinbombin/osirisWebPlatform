"use strict";

/**************************************************
* STEP 0
***************************************************/
let Station = function (name) {
    let self = this;
    self.id = null;
    self.name = ko.observable(name);
};
let Depot = function (name) {
    let self = this;
    self.id = null;
    self.name = ko.observable(name);
};
let Line = function (name) {
    let self = this;
    self.id = null;
    self.name = ko.observable(name);
    self.stations = ko.observableArray();
    self.depots = ko.observableArray();
};
let ConnectionStation = function () {
    let self = this;
    self.id = null;
    self.line = ko.observable();
    self.station = ko.observable();
};
let Connection = function (name) {
    let self = this;
    self.id = null;
    self.name = ko.observable(name);
    self.stations = ko.observableArray();
    self.avgHeight = ko.observable();
    self.avgSurface = ko.observable();
    self.consumption = ko.observable();
    self.description = ko.computed(function () {
        let name = "";
        let arrow = "<i class='fa fa-arrows-h fa-lg' aria-hidden='true'></i>";
        let stationsNumber = self.stations().length;
        for (let i = 0; i < stationsNumber; i++) {
            try {
                name += self.stations()[i].line().name() + "-" + self.stations()[i].station().name();
            } catch (err) {
                // nothing
            }
            if (i + 1 !== stationsNumber) {
                name += arrow;
            }
        }
        return name;
    });
};

let Step0ViewModel = function () {
    let self = this;

    self.lines = ko.observableArray();
    self.depotsQuantity = ko.computed(function () {
        let quantity = 0;
        $.each(self.lines(), function (i, el) {
            quantity += el.depots().length;
        });
        return quantity;
    });
    self.connections = ko.observableArray();

    /**************************************************
     * FORM TO ADD LINE
     ***************************************************/
    self.showAddLineDialog = ko.observable(false);
    let AddLineFormLogic = function () {
        let self = this;
        self.lineName = ko.observable(null);
        self.stationsQuantity = ko.observable(0);
    };
    self.addLineFormLogic = new AddLineFormLogic();
    self.openAddLineForm = function () {
        const LINE_NAME_PREFIX = "L";
        let defaultLineName = LINE_NAME_PREFIX + (self.lines().length + 1);
        self.addLineFormLogic.lineName(defaultLineName);
        self.addLineFormLogic.stationsQuantity(1);
        self.showAddLineDialog(true);
    };
    self.addLine = function () {
        const STATION_NAME_PREFIX = "S";

        if (self.isValidLineForm()) {
            let addForm = self.addLineFormLogic;
            let line = new Line(addForm.lineName());
            for (let i = 0; i < addForm.stationsQuantity(); i++) {
                let stationName = STATION_NAME_PREFIX + (i + 1);
                let station = new Station(stationName);
                line.stations.push(station);
            }
            self.lines.push(line);
            self.showAddLineDialog(false);
        }
    };
    self.removeLine = function () {
        // delete connection if has an station of the line
        let deleteConnection = false;
        for (let i = 0; i < self.connections().length; i++) {
            let connection = self.connections()[i];
            for (let j = 0; j < connection.stations().length; j++) {
                let station = connection.stations()[j];
                if (station.line() === this) {
                    deleteConnection = true;
                }
            }
            if (deleteConnection) {
                self.connections.remove(connection);
                break;
            }
        }
        self.lines.remove(this);
    };

    /**************************************************
     * FORM TO EDIT STATIONS
     ***************************************************/
    self.showEditStationsDialog = ko.observable(false);
    self.selectedStations = ko.observableArray();
    self.openEditStationsForm = function () {
        self.selectedStations.removeAll();
        let stations = this.stations();
        for (let i = 0; i < stations.length; i++) {
            self.selectedStations.push(stations[i]);
        }
        self.showEditStationsDialog(true);
    };
    /**************************************************
     * FORM TO ADD CONNECTIONS
     ***************************************************/
    self.showAddConnectionDialog = ko.observable(false);
    let addConnectionFormLogic = function () {
        let self = this;
        self.connectionName = ko.observable();
        self.connectionStations = ko.observableArray();
        self.avgHeight = ko.observable();
        self.avgSurface = ko.observable();
        self.addConnectionStation = function () {
            self.connectionStations.push(new ConnectionStation())
        };
        self.deleteConnectionStation = function () {
            self.connectionStations.remove(this);
        };
    };
    self.addConnectionFormLogic = new addConnectionFormLogic();
    self.openAddConnectionDialog = function () {
        let addForm = self.addConnectionFormLogic;
        addForm.connectionName("");
        addForm.avgHeight("");
        addForm.avgSurface("");
        addForm.connectionStations.removeAll();
        self.showAddConnectionDialog(true);
    };
    self.addConnection = function () {
        let addForm = self.addConnectionFormLogic;
        if (self.isValidConnectionForm()) {
            let connection = new Connection(addForm.connectionName());
            connection.avgHeight(addForm.avgHeight());
            connection.avgSurface(addForm.avgSurface());
            for (let i = 0; i < addForm.connectionStations().length; i++) {
                connection.stations.push(addForm.connectionStations()[i]);
            }

            self.connections.push(connection);
            self.showAddConnectionDialog(false);
        }
    };
    self.removeConnection = function () {
        self.connections.remove(this);
    };


    /**************************************************
     * FORM TO ADD DEPOTS
     ***************************************************/
    self.showAddDepotDialog = ko.observable(false);
    let addDepotFormLogic = function () {
        let self = this;
        self.name = ko.observable();
        self.line = ko.observable();

        self.updateDefaultDepotName = function (newLine) {
            let line = newLine || self.line();
            if (line === undefined) return;
            const DEPOT_NAME_PREFIX = "D";
            let defaultDepotName = DEPOT_NAME_PREFIX + (line.depots().length + 1);
            self.name(defaultDepotName);
        };
        // each time line is updated
        self.line.subscribe(self.updateDefaultDepotName);
    };
    self.addDepotFormLogic = new addDepotFormLogic();
    self.addDepot = function () {
        if (self.isValidDepotForm()) {
            let depot = new Depot(self.addDepotFormLogic.name());
            self.addDepotFormLogic.line().depots.push(depot);
            self.showAddDepotDialog(false);
            self.addDepotFormLogic.updateDefaultDepotName();
        }
    };
    self.removeDepot = function () {
        let depot = this;
        $.each(self.lines(), function () {
            this.depots.remove(depot)
        });
        self.addDepotFormLogic.updateDefaultDepotName();
    };

    /**************************************************
     * FORMS VALIDATION
     ***************************************************/
    self.isValidLineForm = function () {
        let addForm = self.addLineFormLogic;

        let reasons = [];
        let isValidLineName = true;
        let isValidStationNumber = true;

        let name = addForm.lineName();
        let stationNumber = addForm.stationsQuantity();

        if (name === null || name === "" || !name.length) {
            reasons.push("El nombre no puede ser vacío.");
            isValidLineName = false;
        }
        if (name !== null) {
            if (name.length > 50) {
                reasons.push("El nombre no puede tener un largo mayor a 50 caracteres.");
                isValidLineName = false;
            }

            for (let i = 0; i < self.lines().length; i++) {
                if (name === self.lines()[i].name()) {
                    reasons.push("Ya existe una línea con ese nombre.");
                    isValidLineName = false;
                }
            }
        }

        if (isNaN(stationNumber) || stationNumber <= 0 || 200 < stationNumber) {
            reasons.push("El número de estaciones debe estar entre 1 y 200.");
            isValidStationNumber = false;
        }

        if (isValidLineName &&
            isValidStationNumber) {
            return true;
        }

        self.showWarningList(reasons);
        return false;
    };

    self.isValidDepotForm = function () {
        let addForm = self.addDepotFormLogic;

        let reasons = [];
        let isValidName = true;

        let name = addForm.name();

        if (name === null || name === "" || !name.length) {
            reasons.push("El nombre no puede ser vacío.");
            isValidName = false;
        }
        if (name !== null) {
            if (name.length > 50) {
                reasons.push("El nombre no puede tener un largo mayor a 50 caracteres.");
                isValidName = false;
            }
            for (let i = 0; i < self.lines().length; i++) {
                if (addForm.line().name() === self.lines()[i].name()) {
                    for (let j = 0; j < self.lines()[i].depots().length; j++) {
                        if (name === self.lines()[i].depots()[j].name()) {
                            reasons.push("Ya existe un depósito con ese nombre.");
                            isValidName = false;
                        }
                    }
                }
            }
        }

        if (isValidName) {
            return true;
        }

        self.showWarningList(reasons);
        return false;
    };

    self.isValidConnectionForm = function () {
        let addForm = self.addConnectionFormLogic;

        let reasons = [];
        let isValidStationQuantity = true;
        let isValidConnectionName = true;
        let isValidAvgHeight = true;
        let isValidAvgSurface = true;
        let isValidLines = true;

        let name = addForm.connectionName();
        let stationNumber = addForm.connectionStations().length;
        let avgHeight = addForm.avgHeight();
        let avgSurface = addForm.avgSurface();
        let stations = addForm.connectionStations();

        if (name === null || name === "" || !name.length) {
            reasons.push("El nombre no puede ser vacío.");
            isValidConnectionName = false;
        }
        if (name !== null) {
            if (name.length > 50) {
                reasons.push("El nombre no puede tener un largo mayor a 50 caracteres.");
                isValidConnectionName = false;
            }
            for (let i = 0; i < self.connections().length; i++) {
                if (name === self.connections()[i].name()) {
                    reasons.push("Ya existe una conexión con ese nombre.");
                    isValidConnectionName = false;
                }
            }
        }

        if (stationNumber < 2) {
            reasons.push("La conexión debe tener una o más estaciones.");
            isValidStationQuantity = false;
        }

        if (isNaN(avgHeight) || avgHeight < 0 && 1000 < avgHeight) {
            reasons.push("La altura promedio debe ser un número entre 0 y 1.000 m.");
            isValidAvgHeight = false;
        }

        if (isNaN(avgSurface) || avgSurface < 0 && 1000000 < avgSurface) {
            reasons.push("La altura promedio debe ser un número entre 0 y 1.000.000 m<sup>2</sup>.");
            isValidAvgHeight = false;
        }

        let set = new Set();
        for (let i = 0; i < stations.length; i++) {
            set.add(stations[i].line().name());
        }
        if (set.size !== stationNumber) {
            reasons.push("Una línea no puede tener más de una estación en una conexión.");
            isValidLines = false;
        }

        if (isValidConnectionName &&
            isValidStationQuantity &&
            isValidAvgHeight &&
            isValidAvgSurface &&
            isValidLines) {
            return true;
        }

        self.showWarningList(reasons);
        return false;
    };

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
        let serialize = {
            lines: this.lines(),
            connections: this.connections(),
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
        if (self.lines().length === 0) {
            msg["message"] += "- Debe ingresar una o más líneas.<br />";
        }

        if (msg["message"] !== "") {
            showNotificationMessage(msg);
            return false;
        }
        return true;
    };

    self.update = function (data) {
        let lines = data["lines"];
        let connections = data["connections"];

        self.connections.removeAll();
        self.lines.removeAll();

        let stationList = {};

        lines.forEach(function (el) {
            let line = new Line();
            line.name(el.name);
            line.id = el.id;

            el.stations.forEach(function (el) {
                let station = new Station();
                station.name(el.name);
                station.id = el.id;
                line.stations.push(station);

                stationList[el.id] = {
                    line: line,
                    station: station
                }
            });
            el.depots.forEach(function (el) {
                let depot = new Depot();
                depot.name(el.name);
                depot.id = el.id;
                line.depots.push(depot);
            });
            self.lines.push(line);
        });

        connections.forEach(function (el) {
            let connection = new Connection(el.name);
            connection.id = el.id;
            connection.avgHeight(el.avgHeight);
            connection.avgSurface(el.avgSurface);

            el.stations.forEach(function (connStation) {
                let connectionStation = new ConnectionStation();
                connectionStation.id = connStation.id;
                connectionStation.line(stationList[connStation.station.id].line);
                connectionStation.station(stationList[connStation.station.id].station);

                connection.stations.push(connectionStation);
            });
            self.connections.push(connection);
        });
    }
};