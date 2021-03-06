# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def panel(title_icon, title, body):
    header = """
        <div class="x_title">
            <h2><i class="fa {0}"></i> {1}</h2>
          <div class="clearfix"></div>
        </div>
        """
    content = """
        <div class="x_content">
          {2}
        </div>"""
    header = header if title != "" else ""
    panel = "<div class='x_panel'>{0}{1}</div>".format(header, content)
    return format_html(panel, title_icon, title, body)