from django.contrib.auth.models import User

from checklist.models import (
    Bookmark,
    Category,
    Checklist,
    Comment,
    Item,
    Notification,
    Upvote,
)


# define helper functions
def create_user_if_not_exists(username, password):
    if not User.objects.filter(username=username):
        user = User.objects.create_user(username=username, password=password)
        user.save()

    return User.objects.filter(username=username).first()


def create_category_if_not_exists(name):
    if not Category.objects.filter(name=name):
        Category.objects.create(name=name)

    return Category.objects.filter(name=name).first()


def create_checklist(title, content, user, category, is_draft=False):
    return Checklist.objects.create(
        title=title, content=content, author=user, category=category, is_draft=is_draft
    )


def create_bookmark_upvote(user, checklist, if_bookmark):
    if if_bookmark:
        return Bookmark.objects.create(user=user, checklist=checklist)
    else:
        return Upvote.objects.create(user=user, checklist=checklist)


def create_item(title, checklist, completed=False):
    return Item.objects.create(title=title, checklist=checklist)


def create_comment(checklist, user, body, parent=None):
    return Comment.objects.create(
        checklist=checklist, user=user, body=body, parent=parent
    )


def create_notif(fromUser, toUser, notif_type, checklist=None):
    return Notification.objects.create(
        fromUser=fromUser,
        toUser=toUser,
        notif_type=notif_type,
        checklist=checklist,
    )
