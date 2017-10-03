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
    var linesInfo = {};

    // retrieve scene data
    $.getJSON(SCENE_DATA_URL, function (sceneData) {
        sceneData.lines.forEach(function(metroLineData){
            linesInfo[metroLineData.name] = {
                stations: [],
                tracks: []
            };
            metroLineData.stations.forEach(function(station){
                linesInfo[metroLineData.name].stations.push(station.name);
            });
            linesInfo[metroLineData.name].tracks = metroLineData.tracks;
        });
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
        var station1Index = linesInfo[SELECTED_LINE].stations.indexOf(ORIGIN_STATION);
        var station2Index = linesInfo[SELECTED_LINE].stations.indexOf(DESTINATION_STATION);

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

        // identify tracks to retrieve
        var tracksPositions = [];
        if (direction === "g") {
            for (var i = station1Index; i < station2Index; i++) {
                tracksPositions.push(linesInfo[SELECTED_LINE].tracks[i].id);
            }
        // reverse
        } else {
            for (var i = station1Index - 1; i >= station2Index; i--) {
                tracksPositions.push(linesInfo[SELECTED_LINE].tracks[i].id);
            }
        }

        // get data
        var params = {
            direction: direction,
            operationPeriod: OPERATION,
            metroLineName: SELECTED_LINE,
            tracks: tracksPositions
        };
        switch (CHART_TYPE) {
            case 1:
                // speed attribute
                params.attributes = ["velDist", "Speedlimit"];
                break;
        }

        $.getJSON(MODEL_DATA_URL, params, function(result) {
            var series = [];
            var xData = [];

            for (var attribute in result.answer) {
                var attributeValue = result.answer[attribute];

                console.log(attribute);
                console.log(attributeValue);
                if (attribute === "Distance") {
                    console.log("dist");
                } else if  (attribute === "Time") {
                    attributeValue.forEach(function(track) {
                        xData = xData.concat(track.data);
                    });
                } else {
                    // lines
                    attributeValue.forEach(function(track) {
                        var serie = {
                            type: "line",
                            name: track.name,
                            data: track.data
                        };
                        series.push(serie);
                    });
                }
            }

            var options = {
                series: series,
                xAxis: [{
                    type: "category",
                    data: xData
                }]
            };
            $.extend(options, ECHARTS_OPTIONS);

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