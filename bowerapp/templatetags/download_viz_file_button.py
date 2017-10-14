# -*- coding: utf-8 -*-
from django import template
from django.utils.html import format_html
from django.utils import timezone

register = template.Library()


@register.simple_tag
def download_viz_file_button(execution_obj, disabled = ""):

    timeStamp = execution_obj.timestampFile

    if timeStamp is None:
        timeStamp = ""
        disabled = "disabled"
    else:
        timeStamp = timezone.localtime(timeStamp).strftime("%Y-%m-%d %H:%M:%S")

    # removed time: (<span id="timestamp1">{3}</span>)
    field = u"""
     <a href="{0}" class="btn btn-success btn-lg btn-block {1}">
       <i class="fa fa-file-excel-o"></i> {2}
     </a>
    """
    buttonMessage = u"Descargar datos"
    path = ""
    if execution_obj.downloadFile:
        path = execution_obj.downloadFile.url

    return format_html(field, path, disabled, buttonMessage, timeStamp)