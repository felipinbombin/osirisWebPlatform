# -*- coding: utf-8 -*-
from django import template
from django.utils.html import format_html
from django.utils import timezone

register = template.Library()


@register.simple_tag
def download_viz_file_button(execution_obj, disabled =""):

    timeStamp = execution_obj.timestampFile

    if timeStamp is None:
        timeStamp = ""
        disabled = "disabled"
    else:
        timeStamp = timezone.localtime(timeStamp).strftime("%Y-%m-%d %H:%M:%S")

    field = u"""
     <a href="{}" class="btn btn-success btn-lg btn-block {}">
       <i class="fa fa-file-excel-o"></i> {}
       (<span id="timestamp1">{}</span>)
     </a>
    """
    buttonMessage = u"Descargar datos"
    return format_html(field, execution_obj.downloadFile.url, disabled, buttonMessage, timeStamp)