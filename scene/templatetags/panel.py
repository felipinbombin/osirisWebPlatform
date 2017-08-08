# -*- coding: utf-8 -*-
from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def panel(title_icon, title, body):
    header = """
        <div class="x_title">
            <h2><i class="fa {}"></i> {}</h2>
          <div class="clearfix"></div>
        </div>
        """
    content = """
        <div class="x_content">
          {}
        </div>"""
    header = header if title != "" else ""
    panel = "<div class='x_panel'>" + header + content + "</div>"
    return format_html(panel, title_icon, title, body)