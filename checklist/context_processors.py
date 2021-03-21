# https://stackoverflow.com/a/34903331/6543250 - to pass data to "base.html"

from checklist.models import Category, Notification


def add_variable_to_context(request):
    context = {}
    context["category_list"] = Category.objects.all()

    # if user logged in
    if request.user.is_authenticated:
        # descending order in notifs whose receiving user is the currently logged in user
        context["notif_list"] = Notification.objects.filter(
            toUser=request.user
        ).order_by("-date_notified")
    else:
        context["notif_list"] = []

    return context
