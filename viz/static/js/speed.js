$(document).ready(function(){
    "use strict";

    var PATH_NAME = window.location.pathname.split("/");
    var SCENE_ID = parseInt(PATH_NAME[PATH_NAME.length - 1]);
    var MODEL_DATA_URL = "/viz/speed/data/" + SCENE_ID;
    var SCENE_DATA_URL = "/admin/scene/panel/data/" + SCENE_ID;

    var ECHARTS_OPTIONS = {
        legend: {
           show: true
        },
        title: {
            text: "Velocidad VS tiempo"
        },
        yAxis: [{
             type: "value",
             name: "Velocidad",
             position: "left"
        }],
        tooltip: {
            trigger: "axis"
        }
    };
    var chart = echarts.init(document.getElementById("chart"), theme);
    var data = null;
    var linesInfo = {};
    var timeAxis = null;
    var distanceAxis = null;

    // retrieve scene data
    $.getJSON(SCENE_DATA_URL, function (sceneData) {
        sceneData["lines"].forEach(function(metroLineData){
            linesInfo[metroLineData.name] = [];
            metroLineData.stations.forEach(function(station){
                linesInfo[metroLineData.name].push(station.name);
            });
        });
    });
    $.getJSON(MODEL_DATA_URL, {attributes: ["Distance", "Time"]}, function (serverData) {
        timeAxis = serverData.answer.Time;
        distanceAxis = serverData.answer.Distance;
    });
    $("#btnUpdateChart").click(function () {
        console.log("update chart");

        var SELECTED_LINE = $("#lineFilter").val();
        var ORIGIN_STATION = $("#originStationFilter").val();
        var DESTINATION_STATION = $("#destinationStationFilter").val();
        var OPERATION = $("#operationPeriodFilter").val();
        var CHART_TYPE = parseInt($("#chartTypeFilter").val());

        // detect direction
        var direction = "g"; // default direction: going
        var station1Index = linesInfo[SELECTED_LINE].indexOf(ORIGIN_STATION);
        var station2Index = linesInfo[SELECTED_LINE].indexOf(DESTINATION_STATION);

        if (station2Index - station1Index === 0) {
            var status = {
                message: "La estación de origen y la estación de destino deben ser distintas.",
                title: "Error",
                type: "error"
            };
            showNotificationMessage(status);
            return;
        } else if (station2Index - station1Index < 0) {
            direction = "r"; // reverse
        }

        // get data¿
        var params = {
            direction: direction,
            operationPeriod: OPERATION,
            metroLineName: SELECTED_LINE
        };
        switch (CHART_TYPE) {
            case 1:
                // speed attribute
                params.attributes = ["velDist", "Speedlimit"];
                break;
        }

        $.getJSON(MODEL_DATA_URL, params, function(result) {
            var series = [];

            for (var attribute in result) {
                var attributeValue = result[attribute];

            }

            var distanceTrackList = data[OPERATION][SELECTED_LINE]["Distance"][direction];
            var speedTrackList = data[OPERATION][SELECTED_LINE]["Distance"][direction]; //velDist
            //var speedLimitTrackList = data[OPERATION][SELECTED_LINE]["Speedlimit"][direction]; //velDist

            distanceTrackList.forEach(function (el, index) {
                if (direction === "g") {
                    if (station1Index <= index && index <= station2Index) {
                        var serie = {
                            type: "line",
                            name: el.name,
                            data: el.value
                        };
                        series.push(serie);
                    }
                }
            });
            var options = {
                series: series,
                xAxis: [{
                    type: "category",
                    data: [1,2,3]
                }]
            };
            $.extend(options, ECHARTS_OPTIONS);
            console.log(options);
            chart.clear();
            chart.setOption(options, {
                notMerge: true
            });
        });
    });
    $(window).resize(function() {
        chart.resize();
    });
});