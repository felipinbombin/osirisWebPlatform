$(document).ready(function () {
    "use strict";

    // selectors
    var SELECTED_CHART = $("#chartFilter");

    var PATH_NAME = window.location.pathname.split("/");
    var SCENE_ID = parseInt(PATH_NAME[PATH_NAME.length - 1]);
    var MODEL_DATA_URL = "/viz/energy/data/" + SCENE_ID;

    var ECHARTS_COMMON_OPTIONS = {
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
        },
        grid: {
            left: "10%",
            right: "5%",
            bottom: 75
        }
    };
    var ECHARTS_PIE_OPTIONS = {
        tooltip: {
            trigger: "item"
        },
        series: [{
            type: "pie",
            radius: "60%",
            center: ["50%", "50%"],
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
        tooltip: {
            trigger: "axis"
        },
        yAxis: [{
            type: "value",
            name: "Energía (MWh)",
            nameLocation: "end",
            nameGap: 25,
            position: "left"
        }],
        xAxis: [{
            name: "Origen",
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
            type: "bar",
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
    $.extend(true, ECHARTS_PIE_OPTIONS, ECHARTS_COMMON_OPTIONS);
    delete ECHARTS_PIE_OPTIONS.toolbox.feature.dataZoom;
    $.extend(true, ECHARTS_BAR_OPTIONS, ECHARTS_COMMON_OPTIONS);
    var pieChart = echarts.init(document.getElementById("pieChart"), theme);
    var barChart = echarts.init(document.getElementById("barChart"), theme);

    var makeAjaxCall = true;
    $("#btnUpdateChart").click(function () {
        console.log("update chart");
        var params = {
            prefix: SELECTED_CHART.val()
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

            var data = [];
            result.answer.forEach(function (group) {
                $.each(group.attributes, function (key, attr) {
                    data.push({value: attr, name: key});
                });
            });

            var pieOptions = {};
            $.extend(pieOptions, ECHARTS_PIE_OPTIONS);
            pieOptions.series[0].data = data;

            pieChart.clear();
            pieChart.setOption(pieOptions, {
                notMerge: true
            });

            var barOptions = {};
            $.extend(barOptions, ECHARTS_BAR_OPTIONS);
            barOptions.series[0].data = data.map(function (el) {
                return el.value;
            });
            barOptions.xAxis[0].data = data.map(function (el) {
                return el.name;
            });

            barChart.clear();
            barChart.setOption(barOptions, {
                notMerge: true
            });
        }).always(function () {
            makeAjaxCall = true;
            button.html(previousMessage);
        });
    });
    $(window).resize(function () {
        pieChart.resize();
        barChart.resize();
    });
    $("#menu_toggle").click(function () {
        pieChart.resize();
        barChart.resize();
    });
});