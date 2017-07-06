$(document).ready(function() {
    /**************************************************
     * DROPZONE CONFIGURATION
     ***************************************************/
    // Disable auto discover for all elements:
    Dropzone.autoDiscover = false;

    let dropzoneDict = {
        dictDefaultMessage: "<h1>Arrastra tu archivo topológico aquí.</h1>",
        dictFallbackMessage: "<h1>Tu navegador no acepta el arrastre de archivos. Haz clic aquí</h1>",
        dictFileTooBig: "Archivo con tamaño mayor a {{maxFilesize}}MiB.",
        dictInvalidFileType: "No puedes subir archivos de este tipo.",
        dictMaxFilesExceeded: "No puedes subir más archivos.",
        dictRemoveFile: "Quitar archivo",
        dictCancelUpload: "Cancelar",
        dictCancelUploadConfirmation: "¿Estás seguro que quieres cancelar la carga del archivo?"
    };

    function init() {
        this.on("success", function (file, serverResponse) {
            console.log("success event");
            let status = serverResponse["status"];
            showNotificationMessage(status);
            if (status.code !== 200) {
                this.removeFile(file);
                console.log("file removed");
            }
        });
        this.on("addedfile", function (file) {
            let status = {
                title: "Error",
                message: "",
                type: "error",
            };
            console.log(file);
            if (file.size > 2 * Math.pow(10, 6)) {
                status["message"] = "Archivo debe tener un tamaño inferior a 2MB.";
                showNotificationMessage(status);
                this.removeFile(file);
            } else if (!file.name.endsWith(".xlsx")) {
                status["message"] = "Archivo debe tener formato Excel.";
                showNotificationMessage(status);
                this.removeFile(file);
            } else if (this.files.length > 1) {
                let response = confirm("El nuevo archivo reemplazará al anterior ¿está seguro?");
                if (response) {
                    this.removeFile(this.files[0]);
                } else {
                    this.removeFile(file);
                }
            }
            let url = "http://icons.iconarchive.com/icons/carlosjj/microsoft-office-2013/128/Excel-icon.png";
            $(file.previewElement).find(".dz-image img").attr("src", url);
            console.log("addedfile");
        });
    }

    let csrf = Cookies.get("csrftoken");
    let dropzoneOpts = {
        maxFiles: 1,
        acceptedFiles: ".xlsx",
        maxFilesize: 2,
        init: init,
        headers: {
            "X-CSRFToken": csrf,
        },
    };
    $.extend(dropzoneOpts, dropzoneDict);
    // create dropzone instance
    $("#step2form").dropzone(dropzoneOpts);
    $("#step4form").dropzone(dropzoneOpts);
    $("#step6form").dropzone(dropzoneOpts);
    $("#step7form").dropzone(dropzoneOpts);
});
