# -*- coding: utf-8 -*-
from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def table(id, columns, titles, withChecker=False):
    ths = u""
    for index in range(columns):
        header = u""
        if len(titles) > index:
            header = titles[index]
        ths += u"<th>{}</th>".format(header)

    checker = u""
    if withChecker:
        checker = u"<th style='padding-right:5px;'><input type='checkbox' id='checkbox-select-all' class='flat' checked></th>"

    table = u"""
        <table id="{}" class="table table-striped table-bordered dt-responsive table-condensed nowrap" width="100%">
            <thead>
              <tr>""" + checker + ths + u"""</tr>
            </thead>
            <tbody>
            </tbody>
        </table>
        """

    return format_html(table, id)