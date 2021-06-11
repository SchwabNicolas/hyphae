from django import template

register = template.Library()


@register.filter
def citation(value, style):
    return value.get_citation(style=style)
