$(document).ready(function () {
    "use strict";

    // selectors
    var UPDATE_BUTTON = $("#btnUpdateChart");
    UPDATE_BUTTON.addClass("disabled");

    var SELECTED_LINE = $("#lineFilter");
    var SELECTED_DIRECTION = $("#directionFilter");
    var SELECTED_OPERATION_PERIOD = $("#operationPeriodFilter");

    var PATH_NAME = window.location.pathname.split("/");
    var SCENE_ID = parseInt(PATH_NAME[PATH_NAME.length - 1]);
    var MODEL_DATA_URL = "/viz/strong/data/" + SCENE_ID;
    var SCENE_DATA_URL = "/admin/scene/panel/data/" + SCENE_ID;

    var ECHARTS_OPTIONS = {
        yAxis: [{
            type: "value",
            name: "Potencia (W)",
            nameLocation: "end",
            nameGap: 25,
            position: "left"
        }],
        tooltip: {
            trigger: "axis"
        },
        grid: {
            left: "10%",
            right: "5%",
            bottom: 75
        },
        toolbox: {
            show: true,
            feature: {
                saveAsImage: {
                    show: true,
                    title: "Guardar imagen",
                    name: "Potencia a lo largo de línea " + SELECTED_LINE.val()
                },
                dataZoom: {yAxisIndex: false, title: {zoom: "zoom", back: "volver"}}
            },
            left: "center",
            bottom: "15px"
        }
    };
    var chart = echarts.init(document.getElementById("chart"), theme);
    var linesInfo = {};
    var DIRECTION_GOING = "g";
    var DIRECTION_REVERSE = "r";

    // retrieve scene data
    $.getJSON(SCENE_DATA_URL, function (sceneData) {
        sceneData.lines.forEach(function (metroLineData) {
            linesInfo[metroLineData.name] = {
                directionNames: metroLineData.directionNames
            };
        });
        $("#lineFilter").change(function () {
            SELECTED_DIRECTION.empty();
            var directionNames = linesInfo[SELECTED_LINE.val()].directionNames;
            [DIRECTION_GOING, DIRECTION_REVERSE].forEach(function (key) {
                var option = $("<option></option>").attr("value", key).text(directionNames[key]);
                SELECTED_DIRECTION.append(option);
            });
        });
        UPDATE_BUTTON.removeClass("disabled");
    });

    var makeAjaxCall = true;
    $("#btnUpdateChart").click(function () {
        console.log("update chart");

        var attributes = ["Tiempo_", "Potencia_drive_", "Potencia_ESS_"];
        attributes = attributes.map(function (el) {
            return el + (SELECTED_DIRECTION.val() === DIRECTION_GOING ? "LR" : "RL");
        });
        // get data
        var params = {
            direction: SELECTED_DIRECTION.val(),
            operationPeriod: SELECTED_OPERATION_PERIOD.val(),
            metroLineName: SELECTED_LINE.val(),
            attributes: attributes
        };

        if (makeAjaxCall) {
            makeAjaxCall = false;
            var loadingIcon = " " + $("<i>").addClass("fa fa-cog fa-spin fa-2x fa-fw")[0].outerHTML;
            var previousMessage = $(this).html();
            var button = $(this).append(loadingIcon);
        } else {
            return;
        }
        $.getJSON(MODEL_DATA_URL, params, function (result) {
            var series = [];
            var names = [];

            if ("status" in result) {
                showNotificationMessage(result.status);
                return;
            }
            var xData = null;
            result.answer.forEach(function (line) {
                xData = line.attributes[attributes[0]];
                attributes.slice(1).forEach(function (attr) {
                    var serie = {
                        type: "line",
                        name: attr,
                        data: line.attributes[attr],
                        yAxisIndex: 0,
                        smooth: true,
                        showSymbol: false
                    };
                    series.push(serie);
                    names.push(attr);
                });
            });

            var options = {
                legend: {
                    data: names
                },
                series: series,
                xAxis: [{
                    name: "Tiempo (seg.)",
                    type: "category",
                    nameLocation: "middle",
                    nameTextStyle: {
                        padding: 5
                    },
                    splitLine: {
                        show: false
                    },
                    data: xData
                }]
            };
            $.extend(options, ECHARTS_OPTIONS);

            chart.clear();
            chart.setOption(options, {
                notMerge: true
            });
        }).always(function () {
            makeAjaxCall = true;
            button.html(previousMessage);
        });
    });
    $(window).resize(function () {
        chart.resize();
    });
    $("#menu_toggle").click(function () {
        chart.resize();
    });
});