$(document).ready(function () {
    "use strict";

    // selectors
    var SELECTED_CHART = $("#chartFilter");
    var SELECTED_LINE = $("#lineFilter");

    var PATH_NAME = window.location.pathname.split("/");
    var SCENE_ID = parseInt(PATH_NAME[PATH_NAME.length - 1]);
    var MODEL_DATA_URL = "/viz/heat/data/" + SCENE_ID;

    var ECHARTS_COMMON_OPTIONS = {
        toolbox: {
            show: true,
            feature: {
                saveAsImage: {
                    show: true,
                    title: "Guardar imagen",
                    name: SELECTED_CHART.val()
                }
                //dataZoom: {yAxisIndex: false, title: {zoom: "zoom", back: "volver"}}
            },
            left: "center",
            bottom: "15px"
        },
        grid: {
            left: "10%",
            right: "5%",
            bottom: 75,
            top: 60
        }
    };
    var ECHARTS_HEATMAP_OPTIONS = {
        title: {
            text: "put title here",
            left: "center"
        },
        grid: {
            height: "70%",
            y: "10%"
        },
        xAxis: {
            type: "category",
            data: [],
            splitArea: {
                show: true
            },
            position: "top"
        },
        yAxis: {
            type: "category",
            data: [],
            inverse: true,
            splitArea: {
                show: true
            }
        },
        series: [{
            type: "heatmap",
            data: [],
            label: {
                normal: {
                    show: true
                }
            },
            itemStyle: {
                borderWidth: 1,
                borderColor: "black",
                emphasis: {
                    shadowBlur: 10,
                    shadowColor: "rgba(0, 0, 0, 0.5)"
                }
            }
        }]
    };
    var ECHARTS_LINE_OPTIONS = {
        tooltip: {
            trigger: "axis"
        },
        yAxis: [{
            type: "value",
            name: "Energía (kWh)",
            nameLocation: "end",
            nameGap: 25,
            position: "left"
        }],
        xAxis: [{
            //name: "Origen",
            type: "category",
            nameLocation: "middle",
            nameTextStyle: {
                padding: 5
            },
            splitLine: {
                show: false
            },
            data: []
        }],
        series: [{
            type: "line",
            data: [],
            yAxisIndex: 0,
            smooth: true,
            showSymbol: false,
            itemStyle: {
                normal: {
                    color: "#f2ee13"
                }
            }
        }]
    };
    $.extend(true, ECHARTS_LINE_OPTIONS, ECHARTS_COMMON_OPTIONS);
    $.extend(true, ECHARTS_HEATMAP_OPTIONS, ECHARTS_COMMON_OPTIONS);
    var lineChart = echarts.init(document.getElementById("barChart"), theme);
    var heatmapChart = echarts.init(document.getElementById("heatmapChart"), theme);

    var makeAjaxCall = true;
    $("#btnUpdateChart").click(function () {
        console.log("update chart");
        var prefix = SELECTED_CHART.val();
        var lineId = SELECTED_LINE.val();
        var params = {
            prefix: prefix,
            lineId: lineId
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
            if ("status" in result) {
                showNotificationMessage(result.status);
                return;
            }

            if (prefix.startsWith("average")) {
                var charts = [lineChart, heatmapChart];
                result.answer.forEach(function (table, i) {
                    var heatmapOptions = {};
                    $.extend(heatmapOptions, ECHARTS_HEATMAP_OPTIONS);
                    heatmapOptions.title.text = table.group;
                    var data = [];
                    var yLabels = [];
                    $.each(table.opPeriods, function (j, obj) {
                        yLabels.push(obj.name);
                        obj.values.forEach(function (value, k) {
                            data.push([k, j, value.toFixed(2)]);
                        });
                    });
                    heatmapOptions.series[0].data = data;
                    heatmapOptions.yAxis.data = yLabels;
                    heatmapOptions.xAxis.data = table.row;

                    charts[i].clear();
                    charts[i].setOption(heatmapOptions, {
                        notMerge: true
                    });
                });
            } else {
                // it is a line chart
                var lineOptions = {};
                $.extend(lineOptions, ECHARTS_LINE_OPTIONS);

                result.answer.forEach(function (line, i) {
                    lineOptions.series[i].data = line.x;
                    lineOptions.xAxis[i].data = line.y;
                });

                lineChart.clear();
                lineChart.setOption(lineOptions, {
                    notMerge: true
                });
            }
        }).always(function () {
            makeAjaxCall = true;
            button.html(previousMessage);
        });
    });
    $(window).resize(function () {
        lineChart.resize();
    });
    $("#menu_toggle").click(function () {
        lineChart.resize();
    });
});