# Primary link: Refer https://stackoverflow.com/a/22735278/6543250 for next navigation markers in template tags

# Refer this link: https://www.caktusgroup.com/blog/2018/10/18/filtering-and-pagination-django/ for more explanation and (better generalization ?)

# Additional links: For implementation help: https://stackoverflow.com/a/41653440/6543250
# For django documentation: https://docs.djangoproject.com/en/3.0/howto/custom-template-tags/

# This template is used to navigate to url when the request has a GET parameter
from django import template

register = template.Library()


@register.simple_tag
def url_replace_mod(request, field, value):
    # print('inside template tag url replace mode')
    d = request.GET.copy()
    d[field] = value
    # print(d)
    # print('?'+d.urlencode())
    return "?" + d.urlencode()


@register.simple_tag
def url_delete(request, field):
    d = request.GET.copy()
    del d[field]
    return d.urlencode()
