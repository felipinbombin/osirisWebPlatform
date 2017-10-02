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
    $.get(SCENE_DATA_URL, function (sceneData) {
        sceneData["lines"].forEach(function(metroLineData){
            linesInfo[metroLineData.name] = [];
            metroLineData.stations.forEach(function(station){
                linesInfo[metroLineData.name].push(station.name);
            });
        });
    });
    $.get(MODEL_DATA_URL, function (serverData) {
        data = serverData.answer;
    });
    $("#btnUpdateChart").click(function () {
        console.log("update chart");

        var SELECTED_LINE = $("#lineFilter").val();
        var ORIGIN_STATION = $("#originStationFilter").val();
        var DESTINATION_STATION = $("#destinationStationFilter").val();
        var OPERATION = $("#operationPeriodFilter").val();
        var CHART_TYPE = $("#chartTypeFilter").val();

        // detect direction
        var direction = "g"; //going
        var station1 = linesInfo[SELECTED_LINE].indexOf(ORIGIN_STATION);
        var station2 = linesInfo[SELECTED_LINE].indexOf(DESTINATION_STATION);

        if (station2 - station1 === 0){
            var status = {
                message: "La estación de origen y la estación de destino deben ser distintas.",
                title: "Error",
                type: "error"
            };
            showNotificationMessage(status);
            return;
        }else if (station2 - station1 < 0) {
            direction = "r" // reverse
        }

        // get data¿
        var series = [];
        var distanceTrackList = data[OPERATION][SELECTED_LINE]["Distance"][direction];
        var speedTrackList = data[OPERATION][SELECTED_LINE]["Distance"][direction]; //velDist
        //var speedLimitTrackList = data[OPERATION][SELECTED_LINE]["Speedlimit"][direction]; //velDist

        distanceTrackList.forEach(function(el, index){
            if (direction==="g"){
                if (station1 <= index && index <= station2){
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
    $(window).resize(function() {
        chart.resize();
    });
});