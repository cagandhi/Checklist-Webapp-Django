from django import template
from checklist.models import Notification

register = template.Library()

@register.simple_tag(takes_context=True)
def no_notif(context):
    request = context["request"]
    print("---------------- X ----------------")
    print(request.user)
    print("---------------- X ----------------")

    return Notification.objects.filter(toUser=request.user).order_by(
        "-date_notified"
    )
