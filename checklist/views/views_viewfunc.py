import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required

# mixins for checking if user is logged in and the checklist author is the same as logged in user
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone

from checklist.forms import CommentForm
from checklist.models import (
    Bookmark,
    Checklist,
    Comment,
    Follow,
    FollowChecklist,
    Item,
    Notification,
    Upvote,
)

logger = logging.getLogger(__name__)


# ABOUT PAGE
def about(request):
    logger.error("Test!!")

    return render(request, "checklist/about.html", {"title_new": "about"})


# UPVOTE CHECKLIST FUNCTIONALITY
@login_required
def upvote_checklist(request, checklist_id):
    # for "messages", refer https://stackoverflow.com/a/61603003/6543250

    """if user cannot retract upvote, then this code be uncommented
    if Upvote.objects.filter(user=User.objects.filter(username=username).first(), checklist=Checklist.objects.get(id=checklist_id)):
            msg = 'You have already upvoted the checklist once!'
            messages.info(request, msg)
    """

    """
    Note: notifications recorded only when a user upvotes the checklist not downvote in order to promote healthy behaviour and not let the author inundate with downvote notifs in case some user decides to harass the author.
    """

    if Checklist.objects.get(id=checklist_id).author == request.user:
        msg = "Action Denied! You cannot upvote your own checklist!"
        messages.error(request, msg)
    else:
        # remove user's upvote if he has already upvoted
        obj = Upvote.objects.filter(
            user=request.user, checklist=Checklist.objects.get(id=checklist_id)
        )
        msg = ""
        if obj:
            obj.delete()
            msg = "Upvote retracted!"
        else:
            upvote_obj = Upvote(
                user=request.user,
                checklist=Checklist.objects.get(id=checklist_id),
            )
            upvote_obj.save()

            msg = "Checklist upvoted!"

            # also update notifications table so relevant notif can be shown to author
            fromUser = request.user
            toUser = Checklist.objects.get(id=checklist_id).author
            Notification(
                fromUser=fromUser,
                toUser=toUser,
                notif_type=1,
                checklist=Checklist.objects.get(id=checklist_id),
            ).save()

        messages.success(request, msg)

    if request.META.get("HTTP_REFERER"):
        if "login" in request.META.get("HTTP_REFERER") and "next" in request.META.get(
            "HTTP_REFERER"
        ):
            return redirect("checklist-home")

    # redirect to home url; simply reload the page
    # return redirect('checklist-home')
    return redirect(request.META.get("HTTP_REFERER", "checklist-home"))


# BOOKMARK FUNCTIONALITY
@login_required
def bookmark_checklist(request, checklist_id):
    # remove user's bookmark if he has already bookmarked
    if Checklist.objects.get(id=checklist_id).author == request.user:
        msg = "Action Denied! You cannot bookmark your own checklist!"
        messages.error(request, msg)
    else:

        obj = Bookmark.objects.filter(
            user=request.user, checklist=Checklist.objects.get(id=checklist_id)
        )
        msg = ""
        if obj:
            obj.delete()
            msg = "Bookmark removed!"
        else:
            bookmark_obj = Bookmark(
                user=request.user,
                checklist=Checklist.objects.get(id=checklist_id),
            )
            bookmark_obj.save()

            msg = "Checklist bookmarked!"

        messages.success(request, msg)

    if request.META.get("HTTP_REFERER"):
        if "login" in request.META.get("HTTP_REFERER") and "next" in request.META.get(
            "HTTP_REFERER"
        ):
            return redirect("checklist-home")

    return redirect(request.META.get("HTTP_REFERER", "checklist-home"))


# COMPLETE/DELETE ITEM
@login_required
def item_action(request, item_id, action_type):

    if Item.objects.get(id=item_id).checklist.author != request.user:
        msg = "Action Denied! You can only make changes to your own checklist!"
        messages.error(request, msg)
        return redirect(request.META.get("HTTP_REFERER", "checklist-home"))
    else:
        obj = Item.objects.get(id=item_id)

        if action_type == "complete":
            obj.completed = not obj.completed
            obj.save()

            msg = "Item Ticked/Un-ticked!"
        elif action_type == "delete":
            obj.delete()
            msg = "Item deleted!"

        messages.success(request, msg)
        return redirect("checklist-detail", pk=obj.checklist.id)


# PUBLISH DRAFT CHECKLISTS
@login_required
def publish_checklist(request, checklist_id):
    # for "messages", refer https://stackoverflow.com/a/61603003/6543250

    """if user cannot retract upvote, then this code be uncommented
    if Upvote.objects.filter(user=User.objects.filter(username=username).first(), checklist=Checklist.objects.get(id=checklist_id)):
            msg = 'You have already upvoted the checklist once!'
            messages.info(request, msg)
    """
    if Checklist.objects.get(id=checklist_id).author != request.user:
        msg = "Action Denied! You can only publish your own checklist!"
        messages.error(request, msg)
    else:
        obj = Checklist.objects.get(id=checklist_id)
        obj.is_draft = False
        obj.save()

        msg = "Checklist published and removed from drafts!"
        messages.success(request, msg)

    if request.META.get("HTTP_REFERER"):
        if "login" in request.META.get("HTTP_REFERER") and "next" in request.META.get(
            "HTTP_REFERER"
        ):
            return redirect("checklist-home")

    # redirect to home url; simply reload the page
    # return redirect('checklist-home')
    return redirect(request.META.get("HTTP_REFERER", "checklist-home"))


# FOLLOW USER
@login_required
def follow_user(request, username):
    if request.user.username == username:
        msg = "Action Denied! You can only follow other users!"
        messages.error(request, msg)
    else:
        toUser = User.objects.filter(username=username).first()
        obj = Follow.objects.filter(fromUser=request.user, toUser=toUser)

        msg = ""
        if obj:
            obj.delete()
            msg = "User unfollowed!"
        else:
            Follow(fromUser=request.user, toUser=toUser).save()
            msg = "User followed!"

            fromUser = request.user
            Notification(fromUser=fromUser, toUser=toUser, notif_type=2).save()

        messages.success(request, msg)

    if request.META.get("HTTP_REFERER"):
        if "login" in request.META.get("HTTP_REFERER") and "next" in request.META.get(
            "HTTP_REFERER"
        ):
            return redirect("checklist-home")

    return redirect(request.META.get("HTTP_REFERER", "checklist-home"))


# SAVE AND EDIT
@login_required
def save_and_edit(request, checklist_id):
    old_obj = Checklist.objects.get(id=checklist_id)

    if request.user != old_obj.author:
        new_title = old_obj.title + " by " + request.user.username

        if not Checklist.objects.filter(
            title=new_title,
            content=old_obj.content,
            author=request.user,
            category=old_obj.category,
        ):

            new_obj = Checklist(
                title=new_title,
                content=old_obj.content,
                author=request.user,
                date_posted=timezone.now(),
                category=old_obj.category,
            )
            new_obj.save()

            for item in old_obj.item_set.all():
                item.pk = None
                item.checklist = new_obj
                item.save()

            msg = "Checklist saved. You can now modify it as your own!"
            messages.success(request, msg)

            return redirect("checklist-detail", new_obj.id)

        else:
            msg = "You have already saved this checklist once!"
            messages.error(request, msg)
    else:
        msg = "You can only save and edit others' checklists!"
        messages.error(request, msg)

        return redirect("checklist-detail", old_obj.id)

    if request.META.get("HTTP_REFERER"):
        if "login" in request.META.get("HTTP_REFERER") and "next" in request.META.get(
            "HTTP_REFERER"
        ):
            return redirect("checklist-home")

    return redirect(request.META.get("HTTP_REFERER", "checklist-home"))


# DISMISS NOTIF
@login_required
def dismiss_notif(request, id):
    Notification.objects.filter(id=id).delete()

    if request.META.get("HTTP_REFERER"):
        if "login" in request.META.get("HTTP_REFERER") and "next" in request.META.get(
            "HTTP_REFERER"
        ):
            return redirect("checklist-home")

    return redirect(request.META.get("HTTP_REFERER", "checklist-home"))


# FOLLOW CHECKLIST
@login_required
def follow_checklist(request, checklist_id):
    checklist = Checklist.objects.get(id=checklist_id)

    if request.user == checklist.author:
        msg = "Action Denied! You can not follow your own checklists!"
        messages.error(request, msg)
    else:
        obj = FollowChecklist.objects.filter(
            fromUser=request.user, toChecklist=checklist
        )

        if obj:
            obj.delete()
            msg = "Checklist unfollowed!"
        else:
            FollowChecklist(fromUser=request.user, toChecklist=checklist).save()
            msg = "Checklist followed!"

            fromUser = request.user
            Notification(
                fromUser=fromUser,
                toUser=checklist.author,
                notif_type=3,
                checklist=checklist,
            ).save()

        messages.success(request, msg)

    if request.META.get("HTTP_REFERER"):
        if "login" in request.META.get("HTTP_REFERER") and "next" in request.META.get(
            "HTTP_REFERER"
        ):
            return redirect("checklist-home")

    return redirect(request.META.get("HTTP_REFERER", "checklist-home"))


# SUBMIT COMMENT
@login_required
def submit_comment(request, checklist_id):

    checklist = get_object_or_404(Checklist, id=checklist_id)

    comments = checklist.comments.all().filter(parent=None)

    new_comment = None
    comment_form = None
    # Comment posted
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():

            parent_obj = None
            try:
                parent_id = int(request.POST.get("parent_id"))
            except TypeError:
                parent_id = None

            if parent_id:
                parent_obj = Comment.objects.get(id=parent_id)

            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current checklist and user to the comment
            new_comment.checklist = checklist
            new_comment.user = request.user
            new_comment.parent = parent_obj

            # don't allow the checklist author to post a parent comment (the first comment from which the thread starts)
            if parent_obj is None and request.user == checklist.author:
                msg = "Author can only to reply to others' comments!"
                messages.error(request, msg)
            else:
                # Save the comment to the database
                new_comment.save()
                msg = "Your comment has been saved!"
                messages.success(request, msg)

    # get request so return a new blank form
    else:
        comment_form = CommentForm()

    # try:
    #     messages.info(request, msg)
    # except:  # noqa: E722
    #     pass

    return_path = ""
    kwargs_dict = {}

    if not request.META.get("HTTP_REFERER"):
        return_path = reverse("checklist-detail", kwargs={"pk": checklist_id})
        kwargs_dict = {
            "comments": comments,
            "comment_form": comment_form,
        }
    else:
        return_path = request.META.get("HTTP_REFERER")
        kwargs_dict = {
            "pk": checklist_id,
            "comments": comments,
            "comment_form": comment_form,
        }

    return redirect(
        return_path,
        kwargs=kwargs_dict,
    )
