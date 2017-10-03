$(document).ready(function(){
    "use strict";

    var PATH_NAME = window.location.pathname.split("/");
    var SCENE_ID = parseInt(PATH_NAME[PATH_NAME.length - 1]);
    var MODEL_DATA_URL = "/viz/speed/data/" + SCENE_ID;
    var SCENE_DATA_URL = "/admin/scene/panel/data/" + SCENE_ID;

    var ECHARTS_OPTIONS = {
        title: {
            text: "Velocidad VS tiempo"
        },
        yAxis: [{
             type: "value",
             name: "Velocidad KM/H",
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
        $("#lineFilter").change(function(){
            var SELECTED_LINE = $("#lineFilter").val();
            var ORIGIN_STATION = $("#originStationFilter");
            var DESTINATION_STATION = $("#destinationStationFilter");

            ORIGIN_STATION.empty();
            DESTINATION_STATION.empty();
            linesInfo[SELECTED_LINE].stations.forEach(function(station){
                var option = $("<option></option>").attr("value", station).text(station);
                ORIGIN_STATION.append(option);
                DESTINATION_STATION.prepend(option.clone());
            });
            DESTINATION_STATION[0].selectedIndex = 0;
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
            var names = [];

            result.answer.forEach(function(track){
                var name = track.startStation + " -> " + track.endStation;
                if (direction === "r"){
                    name = track.endStation + " -> " + track.startStation;
                }

                var attributes = track.attributes;
                var trackData = [];
                attributes.Time.forEach(function(timeData, index){
                    trackData.push([timeData, attributes.velDist[index]*3.6]);
                });
                var serie = {
                    type: "line",
                    name: name,
                    data: trackData,
                    yAxisIndex: 0,
                    smooth: false,
                    showSymbol: false
                };
                series.push(serie);
                names.push(name);
            });

            var options = {
                legend: {
                    data: names
                },
                series: series,
                xAxis: [{
                    name: "Tiempo (segundos)",
                    type: "value"
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