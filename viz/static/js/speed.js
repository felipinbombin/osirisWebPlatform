$(document).ready(function(){
    "use strict";

    var PATH_NAME = window.location.pathname.split("/");
    var SCENE_ID = parseInt(PATH_NAME[PATH_NAME.length - 1]);
    var DATA_URL = "/viz/speed/data/" + SCENE_ID;

    var ECHARTS_OPTIONS = {

    };

    // retrieve scene data
    $.get(DATA_URL, function (data) {
        var data = data["answer"];

        var SELECTED_LINE = $("#lineFilter").val();
        var ORIGIN_STATION = $("#originStationFilter").val();
        var DESTINATION_STATION = $("#destinationStationFilter").val();
        var OPERATION = $("#operationPeriodFilter").val();
        var CHART_TYPE = $("#chartTypeFilter").val();

        console.log(SELECTED_LINE);
        console.log(data);
    });
    $("#btnUpdateChart").click(function () {
        console.log("asdasd");


        _barChart.clear();
        _barChart.setOption(options, {
            notMerge: true
        });
    });
    $(window).resize(function() {
        app.resizeCharts();
    });
});