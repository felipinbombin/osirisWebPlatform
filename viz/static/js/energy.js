$(document).ready(function () {
    "use strict";

    // selectors
    var SELECTED_CHART = $("#chartFilter");

    var PATH_NAME = window.location.pathname.split("/");
    var SCENE_ID = parseInt(PATH_NAME[PATH_NAME.length - 1]);
    var MODEL_DATA_URL = "/viz/energy/data/" + SCENE_ID;

    var ECHARTS_PIE_OPTIONS = {
        tooltip: {
            trigger: "item"
        },
        series: [{
            type: "pie",
            radius: "60%",
            center: ["50%", "60%"],
            data: [],
            animationType: "scale",
            animationEasing: "elasticOut",
            animationDelay: function () {
                return Math.random() * 200;
            },
            label: {
                normal: {
                    formatter: function (params) {
                        var number = Number(params.value).toLocaleString();
                        return params.data.name + "\n" + params.percent + "% (" + number + ")";
                    }
                }
            }
        }]
    };
    var ECHARTS_BAR_OPTIONS = {
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
                    name: SELECTED_CHART.val()
                },
                dataZoom: {yAxisIndex: false, title: {zoom: "zoom", back: "volver"}}
            },
            left: "center",
            bottom: "15px"
        }
    };
    var chart = echarts.init(document.getElementById("chart"), theme);

    var makeAjaxCall = true;
    $("#btnUpdateChart").click(function () {
        console.log("update chart");

        var chartId = SELECTED_CHART.val();
        // get data
        var params = {
            prefix: chartId
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
            result.answer.forEach(function (group) {
                xData = line.attributes[attributes[0]];
                attributes.forEach(function (attr) {
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