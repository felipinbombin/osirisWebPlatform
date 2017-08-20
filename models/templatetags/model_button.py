# -*- coding: utf-8 -*-
from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def model_button(model_label, column, state="available"):
    # states: [available, running, disabled]

    button_icon = u"""
        <i class="fa fa-play fa-3x"></i>
        <br><h1>{1}</h1>
        """
    disabled = ""
    vis_label = u"Resultados"
    button_class = "btn-info"

    if state == "disabled":
        disabled = u"disabled"
    elif state == "running":
        button_class = "btn-danger"
        model_label = "Detener"
        button_icon = u"""
            <span class="fa-stack fa-2x">
                <i class="fa fa-stop fa-stack-1x"></i>
                <i class="fa fa-circle-o-notch fa-spin fa-stack-2x"></i>
            </span>
            <br><h2>{1}</h2>
            """
    else:
        pass

    field= u"""
        <div class="col-md-{0} col-sm-{0} col-xs-12">
            <button class="btn {4} btn-lg btn-block" {3}>
                """ + button_icon + """
            </button>
            <button class="btn btn-success btn-block" {3}>
                <h2><i class="fa fa-eye fa-lg"></i> {2}</h2>
            </button>
        </div>"""

    return format_html(field, column, model_label, vis_label, disabled, button_class)