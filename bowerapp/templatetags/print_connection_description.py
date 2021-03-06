from __future__ import unicode_literals

from django import template

register = template.Library()


@register.filter
def print_connection_description(the_list, separator=' <i class="fa fa-arrows-h fa-lg" aria-hidden="true"></i> '):
    return separator.join(str(i['station']['lineName'] + '-' + i['station']['name']) for i in the_list)