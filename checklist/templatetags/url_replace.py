# For implementation help: https://stackoverflow.com/a/41653440/6543250
# For django documentation: https://docs.djangoproject.com/en/3.0/howto/custom-template-tags/

# this template is used to navigate to url when the request has a GET parameter
from django import template
from django.utils.http import urlencode

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)
