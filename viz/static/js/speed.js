$(document).ready(function(){
    "use strict";

    // selectors
    var SELECTED_LINE = $("#lineFilter");
    var ORIGIN_STATION = $("#originStationFilter");
    var DESTINATION_STATION = $("#destinationStationFilter");
    var SELECTED_OPERATION_PERIOD = $("#operationPeriodFilter");

    var PATH_NAME = window.location.pathname.split("/");
    var SCENE_ID = parseInt(PATH_NAME[PATH_NAME.length - 1]);
    var MODEL_DATA_URL = "/viz/speed/data/" + SCENE_ID;
    var SCENE_DATA_URL = "/admin/scene/panel/data/" + SCENE_ID;

    var ECHARTS_OPTIONS = {
        yAxis: [{
             type: "value",
             name: "Velocidad (km/h)",
             nameLocation: "middle",
             nameGap: 25,
             position: "left"
        }],
        tooltip: {
            trigger: "axis"
        },
        grid: {
            left: "5%",
            right: "5%",
            bottom: 75
        },
        toolbox: {
            show: true,
            feature: {
                saveAsImage: {show: true, title: "Guardar imagen", name: "velocidad entre estaciones"},
                dataZoom: {yAxisIndex: false, title: {zoom: "zoom", back: "volver"}}
            },
            left: "center",
            bottom: "15px"
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
            ORIGIN_STATION.empty();
            DESTINATION_STATION.empty();
            linesInfo[SELECTED_LINE.val()].stations.forEach(function(station){
                var option = $("<option></option>").attr("value", station).text(station);
                ORIGIN_STATION.append(option);
                DESTINATION_STATION.prepend(option.clone());
            });
            DESTINATION_STATION[0].selectedIndex = 0;
        });
    });

    $("#btnUpdateChart").click(function () {
        console.log("update chart");

        var DIRECTION_GOING = "g";
        var DIRECTION_REVERSE = "r";
        var selectedLine = SELECTED_LINE.val();

        // detect direction
        var direction = DIRECTION_GOING; // default direction: going
        var station1Index = linesInfo[selectedLine].stations.indexOf(ORIGIN_STATION.val());
        var station2Index = linesInfo[selectedLine].stations.indexOf(DESTINATION_STATION.val());

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
        if (direction === DIRECTION_GOING) {
            for (var i = station1Index; i < station2Index; i++) {
                tracksPositions.push(linesInfo[selectedLine].tracks[i].id);
            }
        // reverse
        } else {
            for (var i = station1Index - 1; i >= station2Index; i--) {
                tracksPositions.push(linesInfo[selectedLine].tracks[i].id);
            }
        }

        // get data
        var params = {
            direction: direction,
            operationPeriod: SELECTED_OPERATION_PERIOD.val(),
            metroLineName: selectedLine,
            tracks: tracksPositions,
            attributes: ["velDist", "Speedlimit"]
        };

        $.getJSON(MODEL_DATA_URL, params, function(result) {
            var series = [];
            var names = [];
            var trackTimes = [];

            var delta = 0;
            var maxSpeed = 0;
            result.answer.forEach(function(track, trackIndex){
                var name = track.startStation + " -> " + track.endStation;
                if (direction === DIRECTION_REVERSE){
                    name = track.endStation + " -> " + track.startStation;
                }

                var trackData = [];
                delta += trackIndex !== 0?trackTimes[trackIndex - 1].length:0;
                track.attributes.velDist.forEach(function(speedData, index){
                    speedData = speedData * 3.6;
                    if (speedData > maxSpeed) {
                        maxSpeed = speedData;
                    }
                    trackData.push([delta + index, speedData]);
                });
                var speedLimit = track.attributes.Speedlimit[1] * 3.6;
                if (speedLimit > maxSpeed) {
                    maxSpeed = speedLimit;
                }

                var length = track.attributes.velDist.length;
                var duration = track.attributes.Time[length-1];
                var serie = {
                    type: "line",
                    name: name,
                    data: trackData,
                    yAxisIndex: 0,
                    smooth: true,
                    showSymbol: false,
                    markLine: {
                        silent: true,
                        symbol: "circle",
                        lineStyle: {
                            normal: {
                                color: "red"
                            }
                        },
                        label: {
                            normal: {
                                position: "middle"
                            }
                        },
                        data:[
                            [
                                {name: speedLimit + " km/h", coord: [delta, speedLimit]},
                                {coord: [delta + length, speedLimit]}
                            ]
                        ]
                    }
                };
                series.push(serie);
                names.push(name);
                trackTimes.push({
                    name: name,
                    time: duration,
                    startStation: track.startStation,
                    endStation: track.endStation,
                    length: length
                });
            });

            var options = {
                legend: {
                    data: names
                },
                series: series,
                xAxis: [{
                    name: "Distancia (metros)",
                    type: "value",
                    nameLocation: "middle",
                    nameTextStyle: {
                        padding: 5
                    },
                    splitLine: {
                        show: false
                    }
                }]
            };
            $.extend(options, ECHARTS_OPTIONS);
            if (direction === DIRECTION_REVERSE) {
                options.legend.data = options.legend.data.reverse();
                options.xAxis[0].inverse = true;
                options.yAxis[0].position = "right";
            }
            options.yAxis[0]["max"] = maxSpeed;

            chart.clear();
            chart.setOption(options, {
                notMerge: true
            });

            // update table
            var totalTime = 0;
            var tableBody = $("#timeTable tbody");
            tableBody.empty();
            trackTimes.forEach(function(track, index){
                var startStationRow = ("<tr><td>" + track.startStation + "</td><td>" + result.dwellTime[track.startStation].toFixed(2) + "</td></tr>");
                var trackRow = $("<tr><td>" + track.name + "</td><td>" + track.time.toFixed(2) + "</td></tr>");
                tableBody.append(startStationRow);
                tableBody.append(trackRow);
                totalTime += result.dwellTime[track.startStation] + track.time;
                if (index+1 === trackTimes.length){
                    var endStationRow = ("<tr><td>" + track.endStation + "</td><td>" + result.dwellTime[track.endStation].toFixed(2) + "</td></tr>");
                    tableBody.append(endStationRow);
                    totalTime += result.dwellTime[track.endStation];
                }
            });
            tableBody.append($("<tr><td><strong>Tiempo total:</strong></td><td><strong>" + totalTime.toFixed(2) + "</strong></td></tr>"));
        });
    });
    $(window).resize(function() {
        chart.resize();
    });
    $("#menu_toggle").click(function() {
        chart.resize();
    });
});