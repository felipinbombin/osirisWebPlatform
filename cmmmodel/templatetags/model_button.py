# -*- coding: utf-8 -*-
from django import template
from django.utils.html import format_html
from django.utils import timezone

from datetime import timedelta

register = template.Library()

@register.simple_tag
def model_button(model_label, column, id, last_execution_info, status="available", vis_url=""):
    # states: [available, running, disabled]

    button_icon = u"""
        <i class="fa fa-play fa-3x"></i>
        <br><h1>{5}</h1>
        """
    disabled = ""
    vis_label = u"Resultados"
    button_class = u"btn-info"
    button_label = u"Ejecutar"

    if status == "disabled":
        disabled = u"disabled"
    elif status == "running":
        button_class = u"btn-danger"
        button_label = u"Detener"
        button_icon = u"""
            <span class="fa-stack fa-2x">
                <i class="fa fa-stop fa-stack-1x"></i>
                <i class="fa fa-circle-o-notch fa-spin fa-stack-2x"></i>
            </span>
            <br><h2>{5}</h2>
            """

    start = ""
    end = ""
    duration = ""
    if last_execution_info != "":
        start = timezone.localtime(last_execution_info['start']).strftime("%x %X")
        end = timezone.localtime(last_execution_info['end']).strftime("%x %X") if last_execution_info['end'] is not None else ""
        duration = last_execution_info['duration']
        if duration != "":
            duration = duration - timedelta(microseconds=duration.microseconds)

    last_execution_table = u"""
        <p class="text-center"> Última ejecución</p>
        <table class="table table-striped table-bordered">
          <tbody>
            <tr><td>Inicio</td><td class="startDate">{0}</td></tr>
            <tr><td>Fin</td><td class="endDate">{1}</td></tr>
            <tr><td>Duración</td><td class="duration">{2}</td></tr>
          </tbody>
        </table>
        """.format(start, end, duration)

    field= u"""
        <div id="model-{6}" class="col-md-{0} col-sm-{0} col-xs-12">
            <h1 class="text-center">{1}</h1>
            <button class="btn {4} btn-lg btn-block" {3}>
                """ + button_icon + """
            </button>
            <button onclick="window.location='{7}'" class="btn btn-success btn-block" {3}>
                <h2><i class="fa fa-eye fa-lg"></i> {2}</h2>
            </button>
            """ + last_execution_table + """
        </div>"""

    return format_html(field, column, model_label, vis_label, disabled, button_class, button_label, id, vis_url)