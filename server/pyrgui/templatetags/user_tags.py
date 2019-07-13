from django import template

register = template.Library()


@register.filter
def pretty_args(value):
    pretty_value = value[1:-1].replace(',', '<br>')
    return pretty_value


@register.filter
def cut_result(value):
    return value[0:value.find(')')+1]

