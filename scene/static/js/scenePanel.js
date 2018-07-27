"use strict";

$(document).ready(function () {
    const PATH_NAME = window.location.pathname.split("/");
    const SCENE_ID = parseInt(PATH_NAME[PATH_NAME.length - 1]);
    const DATE_URL = "/admin/scene/wizard/getSceneData/" + SCENE_ID;
    const CHANGE_NAME_URL = "/admin/scene/panel/changeName/" + SCENE_ID;
    const DELETE_SCENE_URL = "/admin/scene/panel/delete/" + SCENE_ID;
    const SCENE_ADMIN_URL = "/admin/scene/scene/";
    const MODEL_INFO_URL = "/models/status/";
    const RUN_MODEL_URL = "/models/run/";
    const STOP_MODEL_URL = "/models/stop/";

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
            var spinnerDOM = $("#stopModelDialog")[0];
            spinner.spin(spinnerDOM);
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
        self.showRunModelDialog = ko.observable(false);
        self.model = {
            name: ko.observable(""),
            id: ko.observable(""),
            follow: ko.observableArray([])
        };
        self.models = ko.observableArray([]);

        self.updateButtonsView = function(models) {
            var labels = {
                BUTTON_MODEL_RUN: "Ejecutar",
                BUTTON_MODEL_STOP: "Detener"
            };
            //console.log(response);
            self.models.removeAll();
            models.forEach(function(model){
               var modelButton = $("#model-" + model.id);
               var runButton = $(":button:eq(0)", modelButton);
               var visButton = $(":button:eq(1)", modelButton);
               var runSkin = "<i class='fa fa-play fa-3x'></i><br><h1>" + labels.BUTTON_MODEL_RUN + "</h1>";
               var runningSkin = "<span class='fa-stack fa-2x'><i class='fa fa-stop fa-stack-1x'></i><i class='fa fa-circle-o-notch fa-spin fa-stack-2x'></i></span><br><h2>" + labels.BUTTON_MODEL_STOP + "</h2>";
               switch (model.status) {
                   case "available":
                       runButton.prop("disabled", false).addClass("btn-info").removeClass("btn-danger").html(runSkin);
                       visButton.prop("disabled", false);
                       break;
                   case "disabled":
                       runButton.prop("disabled", true).addClass("btn-info").removeClass("btn-danger").html(runSkin);
                       visButton.prop("disabled", true);
                       break;
                   case "running":
                       runButton.prop("disabled", false).addClass("btn-danger").removeClass("btn-info").html(runningSkin);
                       visButton.prop("disabled", false);
                       break;
               }

               if("lastExecutionInfo" in model){
                   var startDate = (new Date(model.lastExecutionInfo.start)).toLocaleString();
                   var endDate = "";
                   if (model.lastExecutionInfo.end !== null) {
                       endDate = (new Date(model.lastExecutionInfo.end)).toLocaleString();
                   }
                   $(".startDate", modelButton).html(startDate);
                   $(".endDate", modelButton).html(endDate);
                   $(".duration", modelButton).html(model.lastExecutionInfo.duration);
                   $(".status", modelButton).html(model.lastExecutionInfo.status);
               }
               // add checkbox interaction for each follow model
               model.follow.forEach(function(nextModel) {
                   nextModel.checked = ko.observable(false);
               });
               self.models.push(model);
            });
        };
        self.updateModelButtonState = function() {
            // activate spinjs
            //spinner.spin(spinnerParentDOM);
            // retrieve model data
            var data = {
                scene_id: SCENE_ID
            };
            $.get(MODEL_INFO_URL, data, function(response) {
                self.updateButtonsView(response);
            }).always(function () {
                //spinner.stop();
            });
        };
        self.makeAjax = true;
        self.modelRun = function() {
            if(!self.makeAjax) {
                return;
            }
            self.makeAjax = false;
            var model = this;
            var modelId = model.id();
            var nextModelIds = [];
            model.follow().forEach(function(v){
                if (v.checked()) {
                    nextModelIds.push(v.id);
                }
            });
            var data = {
                scene_id: SCENE_ID,
                model_id: modelId,
                next_model_ids: nextModelIds
            };
            // activate spinjs
            var spinnerDOM = $("#runModelDialog")[0];
            spinner.spin(spinnerDOM);

            // run model
            $.post(RUN_MODEL_URL, data, function(response) {
                showNotificationMessage(response.status);
                if("models" in response) {
                    self.updateButtonsView(response.models);
                }
                self.showRunModelDialog(false);
            }).always(function () {
                self.makeAjax = false;
                spinner.stop();
            });
        };

        self.showStopModelDialog = ko.observable(false);
        self.modelStop = function() {
            var model = this;
            var modelId = model.id();
            var nextModelIds = [];
            model.follow().forEach(function(v){
                if (v.checked()) {
                    nextModelIds.push(v.id);
                }
            });
            var data = {
                scene_id: SCENE_ID,
                model_id: modelId
            };
            // activate spinjs
            spinner.spin(spinnerParentDOM);
            // retrieve model data
            $.post(STOP_MODEL_URL, data, function(response) {
                showNotificationMessage(response.status);
                if("models" in response) {
                    self.updateButtonsView(response.models);
                }
                self.showStopModelDialog(false);
            }).always(function () {
                spinner.stop();
            });
        };
    };
    var panelDOM = document.getElementById("content-main");
    var viewModel = new Scene();
    viewModel.updateModelButtonState();
    ko.applyBindings(viewModel, panelDOM);

    $("[id^=model-] :button:even").click(function(){
        var button = $(this).parent();
        var modelId = button.attr("id").split("-")[1];

        viewModel.model.name(viewModel.models()[modelId-1].name);
        viewModel.model.id(modelId);
        viewModel.model.follow.removeAll();
        viewModel.models()[modelId-1].follow.forEach(function(f) {
            viewModel.model.follow.push(f);
        });

        if(viewModel.models()[modelId-1].status !== "running"){
            viewModel.showRunModelDialog(true);
        } else {
            viewModel.showStopModelDialog(true);
        }
    });

    setInterval(function(){
        viewModel.updateModelButtonState();
    }, 15*1000);
});