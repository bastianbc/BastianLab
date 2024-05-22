from urllib.parse import urlencode
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """ This function is used in pagination to prevent using context or query data when 
    switching pages """
    query = context['request'].GET.copy()
    if query.get('page'): query.pop('page') 
    query.update(kwargs)
    return query.urlencode()