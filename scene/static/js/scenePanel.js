"use strict";

$(document).ready(function () {
    const PATH_NAME = window.location.pathname.split("/");
    const SCENE_ID = parseInt(PATH_NAME[PATH_NAME.length - 1]);
    const URL_DATA = "/admin/scene/wizard/getSceneData/" + SCENE_ID;
    const URL_CHANGE_NAME = "/admin/scene/panel/changeName/" + SCENE_ID;
    const URL_DELETE_SCENE = "/admin/scene/panel/delete/" + SCENE_ID;
    const URL_SCENE_ADMIN = "/admin/scene/scene/";

    // knockout scene object
    let Scene = function () {
        let self = this;

        self.name = ko.observable();

        // retrieve scene data
        $.get(URL_DATA, function (data) {
            self.name(data["name"]);
        });

        /**************************************************
         * FORM TO CHANGE SCENE NAME
         ***************************************************/
        self.showChangeNameDialog = ko.observable(false);
        let changeNameFormLogic = function () {
            let self = this;
            self.name = ko.observable(null);
        };
        self.changeNameFormLogic = new changeNameFormLogic();
        self.openForm = function () {
            self.changeNameFormLogic.name(self.name());
            self.showChangeNameDialog(true);
        };
        self.changeName = function () {
            let newName = self.changeNameFormLogic.name();
            if (newName !== null && newName !== "") {
                // retrieve scene data
                let csrf = Cookies.get("csrftoken");
                let data = {
                    "new_name": newName
                };

                // activate spinjs
                spinner.spin(spinnerParentDOM);
                $.ajax({
                    url: URL_CHANGE_NAME,
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
            let csrf = Cookies.get("csrftoken");

            // activate spinjs
            spinner.spin(spinnerParentDOM);
            $.ajax({
                url: URL_DELETE_SCENE,
                type: "post",
                headers: {
                    "X-CSRFToken": csrf
                },
                success: function (response) {
                    self.showDeleteDialog(false);
                    showNotificationMessage(response["status"]);
                    // redirect
                    window.location.replace("http://" + window.location.host + URL_SCENE_ADMIN);
                },
                complete: function () {
                    spinner.stop();
                }
            });
        };
    };
    let stepDOM = document.getElementById("content-main");
    let viewModel = new Scene();
    ko.applyBindings(viewModel, stepDOM);
});