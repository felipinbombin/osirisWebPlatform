"use strict";

$(document).ready(function(){
    /**************************************************
    * WIZARD LOGIC
    ***************************************************/
    let pathname = window.location.pathname.split("/");
    const sceneId = parseInt(pathname[pathname.length-1]);
    const sceneDataURL = "/admin/scene/wizard/getSceneData/" + sceneId;

    /**
     * return view model of step 'id'
     * */
    let getViewModel = function(id, StepViewModel){
        let stepId = "step-" + (id + 1);
        let stepDOM = document.getElementById(stepId);
        let viewModel = ko.dataFor(stepDOM);

        if (viewModel === undefined) {
            viewModel = new StepViewModel();
            ko.applyBindings(viewModel, stepDOM);
        }

        return viewModel;
    };

    // Initialize the leaveStep event
    let wizard = $("#wizard");
    wizard.on("leaveStep", function(e, anchorObject, stepNumber, stepDirection) {
        return true;
    });

    // Initialize the showStep event
    wizard.on("showStep", function(e, anchorObject, stepNumber, stepDirection, stepPosition) {

        init_sidebar();
        console.log("You are on step " + stepNumber + " now " + stepPosition);

        let currentStepViewModel = null;
        switch (stepNumber) {
            case 0:
                currentStepViewModel = getViewModel(stepNumber, Step0ViewModel);
                break;
            case 2:
                currentStepViewModel = getViewModel(stepNumber, Step2ViewModel);
                break;
            case 4:
                currentStepViewModel = getViewModel(stepNumber, Step4ViewModel);
                break;
        }

        switch (stepNumber) {
            case 0:
            case 2:
            case 4:
                //retrieve data from server
                $.get(sceneDataURL, function (data) {
                    currentStepViewModel.update(data);
                    console.log("data of step " + stepNumber + " retrieved successfully");
                });
                break;
        }
    });

    let nextLogic = function(){

        let getUrl = function(stepId){
            const validateURL = "/admin/scene/wizard/validate/";
            return validateURL + stepId + "/" + sceneId;
        };

        let currentStepViewModel = null;
        let currentStep = parseInt(window.location.hash.split("-")[1]) - 1;

        // what to do it depends of the step
        // 0, 2, 4 => get step view model
        // 1, 3, 5, 6 => check if file was loaded successfully
        switch(currentStep){
            case 0:
                currentStepViewModel = getViewModel(currentStep, Step0ViewModel);
                break;
            case 2:
                currentStepViewModel = getViewModel(currentStep, Step2ViewModel);
                break;
            case 4:
                // ask to server if file was uploaded
                $("#wizard").smartWizard("next");
                break;
            case 1:
            case 3:
            case 5:
            case 6:
                // ask to server if file was uploaded
                $.post(getUrl(currentStep), function(answer){
                    // success
                    if(answer.status.code === 200){
                        $("#wizard").smartWizard("next");
                    }else{
                        showNotificationMessage(answer.status);
                    }
                });
                break;
        }

        // steps 0, 2, 4 => validate inputs and send to server
        switch(currentStep){
            case 0:
            case 2:
            case 4:
                if(currentStepViewModel.isValid()){
                    let data = currentStepViewModel.serialize();
                    console.log(data);
                    $.post(getUrl(currentStep), data, function(answer){
                        // success
                        if(answer.status.code === 200){
                            $("#wizard").smartWizard("next");
                        }
                        showNotificationMessage(answer.status);
                    });
                }
                break;
        }
    };
    let finalButton = $("<button></button>").text("Finalizar")
                      .addClass("btn btn-dark")
                      .on("click", function(){
                        alert("Finish button click");
                        console.log(this);
                      });
    let prevButton = $("<button></button>").text("Anterior")
                      .addClass("btn btn-default")
                      .on("click", function(){
                        $("#wizard").smartWizard("prev");
                      });
    let nextButton = $("<button></button>").text("Siguiente")
                      .addClass("btn btn-default")
                      .css("padding-right", "5px")
                      .on("click", nextLogic);

    // get scene info
    $.get(sceneDataURL, function(data){
        // set wizard
        wizard.smartWizard({
            selected: data.currentStep,
            autoAdjustHeight: false,
            markAllPreviousStepsAsDone: true,
            theme: "dots",
            toolbarSettings: {
            showNextButton: false,
            showPreviousButton: false,
            toolbarPosition: "top",
            toolbarExtraButtons: [
              prevButton,
              nextButton,
              finalButton
            ],
            },
        });
    });

});