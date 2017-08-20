"use strict";

$(document).ready(function () {
    const PATH_NAME = window.location.pathname.split("/");
    const SCENE_ID = parseInt(PATH_NAME[PATH_NAME.length - 1]);
    const DATE_URL = "/admin/scene/wizard/getSceneData/" + SCENE_ID;
    const CHANGE_NAME_URL = "/admin/scene/panel/changeName/" + SCENE_ID;
    const DELETE_SCENE_URL = "/admin/scene/panel/delete/" + SCENE_ID;
    const SCENE_ADMIN_URL = "/admin/scene/scene/";
    const MODEL_INFO_URL = "/models/status/";

    // knockout scene object
    var Scene = function () {
        var self = this;

        self.name = ko.observable();

        // retrieve scene data
        $.get(DATE_URL, function (data) {
            self.name(data["name"]);

        });

        /**************************************************
         * FORM TO CHANGE SCENE NAME
         ***************************************************/
        self.showChangeNameDialog = ko.observable(false);
        var changeNameFormLogic = function () {
            var self = this;
            self.name = ko.observable(null);
        };
        self.changeNameFormLogic = new changeNameFormLogic();
        self.openForm = function () {
            self.changeNameFormLogic.name(self.name());
            self.showChangeNameDialog(true);
        };
        self.changeName = function () {
            var newName = self.changeNameFormLogic.name();
            if (newName !== null && newName !== "") {
                // retrieve scene data
                var csrf = Cookies.get("csrftoken");
                var data = {
                    "new_name": newName
                };

                // activate spinjs
                spinner.spin(spinnerParentDOM);
                $.ajax({
                    url: CHANGE_NAME_URL,
                    type: "post",
                    data: data,
                    headers: {
                        "X-CSRFToken": csrf
                    },
                    success: function (response) {
                        self.name(newName);
                        self.showChangeNameDialog(false);
                        showNotificationMessage(response["status"]);
                    },
                    complete: function () {
                        spinner.stop();
                    }
                });
            }
        };

        /**************************************************
         * FORM TO DELETE SCENE
         ***************************************************/
        self.showDeleteDialog = ko.observable(false);
        self.delete = function () {
            // retrieve scene data
            var csrf = Cookies.get("csrftoken");

            // activate spinjs
            spinner.spin(spinnerParentDOM);
            $.ajax({
                url: DELETE_SCENE_URL,
                type: "post",
                headers: {
                    "X-CSRFToken": csrf
                },
                success: function (response) {
                    self.showDeleteDialog(false);
                    showNotificationMessage(response["status"]);
                    // redirect
                    window.location.replace("http://" + window.location.host + SCENE_ADMIN_URL);
                },
                complete: function () {
                    spinner.stop();
                }
            });
        };

        /**************************************************
         * MANAGE MODEL EXECUTION
         ***************************************************/
        self.updateModelButtonState = function() {
            var labels = {
                BUTTON_MODEL_RUN: "Ejecutar",
                BUTTON_MODEL_STOP: "Detener"
            };
            // activate spinjs
            spinner.spin(spinnerParentDOM);
            // retrieve model data
            $.get(MODEL_INFO_URL, {"sceneId": SCENE_ID},
                function(response) {
                    response.forEach(function(v){
                       var modelButton = $("#model-"+v.id);
                       var runButton = $(":button:eq(0)", modelButton);
                       var visButton = $(":button:eq(1)", modelButton);
                       var runSkin = "<i class='fa fa-play fa-3x'></i><br><h1>" + labels.BUTTON_MODEL_RUN + "</h1>";
                       var runningSkin = "<span class='fa-stack fa-2x'><i class='fa fa-stop fa-stack-1x'></i><i class='fa fa-circle-o-notch fa-spin fa-stack-2x'></i></span><br><h2>" + labels.BUTTON_MODEL_STOP + "</h2>";
                       switch (v.status) {
                           case "available":
                               runButton.prop("disabled", false).addClass("btn-info").removeClass("btn-danger").html(runSkin);
                               visButton.prop("disabled", false);
                               break;
                           case "disabled":
                               runButton.prop("disabled", true).addClass("btn-info").removeClass("btn-danger").html(runSkin);
                               visButton.prop("disabled", true);
                               break;
                           case "running":
                               runButton.prop("disabled", true).addClass("btn-danger").removeClass("btn-info").html(runningSkin);
                               visButton.prop("disabled", false);
                               break;
                       }
                    });
                }).always(function () {
                    spinner.stop();
                });
        }
    };
    var stepDOM = document.getElementById("content-main");
    var viewModel = new Scene();
    ko.applyBindings(viewModel, stepDOM);
    setInterval(function(){
        viewModel.updateModelButtonState();
    }, 15*1000);
});