# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import ugettext as _

register = template.Library()


@register.simple_tag
def download_scene_file_button(step_id, scene, disabled=""):
    url = reverse("scene:downloadStepFile", kwargs={"step_id": step_id, "scene_id": scene.id})

    if step_id == 1:
        time_stamp = scene.timeStampStep1File
    elif step_id == 3:
        time_stamp = scene.timeStampStep3File
    elif step_id == 5:
        time_stamp = scene.timeStampStep5File
    elif step_id == 6:
        time_stamp = scene.timeStampStep6File
    else:
        time_stamp = None

    if time_stamp is None:
        time_stamp = ""
        disabled = "disabled"
    else:
        time_stamp = timezone.localtime(time_stamp).strftime("%Y-%m-%d %H:%M:%S")

    field = """
     <a href="{}" class="btn btn-success btn-lg btn-block {}">
       <i class="fa fa-file-excel-o"></i> {}
       (<span id="timestamp1">{}</span>)
     </a>
    """
    button_message = _("Descargar ultimo archivo subido")
    return format_html(field, url, disabled, button_message, time_stamp)
