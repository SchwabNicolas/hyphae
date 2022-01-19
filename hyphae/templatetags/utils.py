import random
from django import template

register = template.Library()


@register.simple_tag
def random_int(a, b=None):
    if b is None:
        a, b = 0, a
    return random.randint(a, b)


@register.filter(name='prefix')
def prefix(value, prefix=''):
    if value != '':
        return f'{prefix}{value}'
    return ''


@register.filter(name='suffix')
def suffix(value, suffix=''):
    if value != '':
        return f'{value}{suffix}'
    return ''


@register.tag(name="ifauth")
def if_auth(parser, token):
    nodelist = parser.parse(('endifauth',))
    parser.delete_first_token()
    return IfAuthNode(nodelist)


class IfAuthNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        request = context['request']
        if request.user.is_authenticated:
            output = self.nodelist.render(context)
        else:
            output = ''
        return output
