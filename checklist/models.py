from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from djrichtextfield.models import RichTextField


class Checklist(models.Model):
    title = models.CharField(max_length=100)
    # https://pypi.org/project/django-richtextfield/ - to store rich text in database [ GitHub: https://github.com/jaap3/django-richtextfield ]
    content = RichTextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    visibility = models.PositiveIntegerField(default=0)
    category = models.ForeignKey("Category", null=True, on_delete=models.SET_NULL)
    is_draft = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("checklist-detail", kwargs={"pk": self.id})


class Item(models.Model):
    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse("item-detail", kwargs={"pk": self.checklist.id})


class Upvote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + " - " + self.checklist.title


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + " - " + self.checklist.title


class Category(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Follow(models.Model):
    # why use related_name property - refer https://stackoverflow.com/a/2642645/6543250
    fromUser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="fromUser"
    )
    toUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="toUser")


class FollowChecklist(models.Model):
    # why use related_name property - refer https://stackoverflow.com/a/2642645/6543250
    fromUser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="fromUserFC"
    )
    toChecklist = models.ForeignKey(
        Checklist, on_delete=models.CASCADE, related_name="toChecklist"
    )


class Notification(models.Model):

    UPVOTE = 1
    USER_FOLLOW = 2
    CHECKLIST_FOLLOW = 3

    NOTIF_CHOICES = (
        (UPVOTE, "upvote"),
        (USER_FOLLOW, "user_follow"),
        (CHECKLIST_FOLLOW, "checklist_follow"),
    )

    fromUser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="fromUserNotif"
    )
    toUser = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="toUserNotif"
    )
    date_notified = models.DateTimeField(default=timezone.now)
    notif_type = models.PositiveIntegerField(choices=NOTIF_CHOICES, default=UPVOTE)
    checklist = models.ForeignKey(
        Checklist, on_delete=models.CASCADE, null=True, blank=True
    )


class Comment(models.Model):
    checklist = models.ForeignKey(
        Checklist, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users")
    body = RichTextField()
    created_on = models.DateTimeField(default=timezone.now)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return "Comment {} by {}".format(self.body, self.user.username)

    def children(self):
        return Comment.objects.filter(parent=self)
