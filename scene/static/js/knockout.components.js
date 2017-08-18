"use strict";

/**************************************************
* CUSTOM COMPONENTS
***************************************************/

// field form to populate form
ko.components.register("field-form", {
    template:
    "<div class='form-group'>" +
        "<label class='control-label col-md-4 col-sm-4 col-xs-12' data-bind='html: label'></label>" +
        "<div class='col-md-8 col-sm-8 col-xs-12'>" +
            "<!-- ko ifnot: unit -->" +
              "<input class='form-control' data-bind='value: source, attr: { type: type, placeholder: placeholder }' />" +
            "<!-- /ko -->" +
            "<!-- ko if: unit -->" +
            "<div class='input-group'>" +
                "<input class='form-control' data-bind='value: source, attr: { type: type, placeholder:placeholder }' />" +
                "<span class='input-group-addon' data-bind='visible: unit, html: unit'></span>" +
            "</div>" +
            "<!-- /ko -->" +
        "</div>" +
    "</div>",
    viewModel: function(params){
        let self = this;
        self.source = params.source;
        self.label = params.label;
        self.type = params.type || "number";
        self.unit = params.unit || "";
        self.placeholder = params.placeholder || "";
    }
});
ko.components.register("small-fields-form", {
    template:
    "<!-- ko foreach: fields -->" +
    "<label class='control-label col-md-1 col-sm-1 col-xs-4' data-bind='html: label'></label>" +
    "<div class='col-md-3 col-sm-3 col-xs-8'>" +
        "<div class='input-group'>" +
            "<input class='form-control' data-bind='value: source, attr: { type: type }' />" +
            "<span class='input-group-addon' data-bind='visible: unit, html: unit'></span>" +
        "</div>" +
    "</div>" +
    "<!-- /ko -->",
    viewModel: function(params) {
        let self = this;
        self.fields = params.fields.map(function(el){
            el.type = el.type || "number";
            el.unit = el.unit || "";
            return el;
        });
    }
});

/**************************************************
* CUSTOM BINDING HANDLERS
***************************************************/
ko.bindingHandlers.modal = {
    init: function (element, valueAccessor) {
        $(element).modal({
            show: false
        });

        let value = valueAccessor();
        if (typeof value === "function") {
            $(element).on("hide.bs.modal", function () {
                value(false);
            });
        }
        ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
            $(element).modal("destroy");
        });
    },
    update: function (element, valueAccessor) {
        let value = valueAccessor();
        if (ko.utils.unwrapObservable(value)) {
            $(element).modal("show");
        } else {
            $(element).modal("hide");
        }
    }
};