from django import template
import time
from datetime import datetime
from django.utils.dateparse import parse_datetime
import pytz

register = template.Library()


@register.filter
def timediff(value):
    date_format = "%Y-%m-%d %H:%M:%S.%f"
    var = datetime.now(tz=pytz.utc)
    #curr_time = datetime.strptime(var).strftime(date_format)
    #print(var)
    #print(value)
    delta = var - value
    return delta.seconds


@register.filter
def pretty_args(value):
    pretty_value = value[1:-1].replace(',', '<br>')
    return pretty_value


@register.filter
def cut_result(value):
    return value[0:value.find(')')+1]
