import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
# mixins for checking if user is logged in and the checklist author is the same as logged in user
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView,)

from .forms import CommentForm
from .models import (Bookmark, Category, Checklist, Comment, Follow, FollowChecklist,
                     Item, Notification, Upvote,)

logger = logging.getLogger(__name__)


def paginate_content(checklist_upvotes, page, paginate_by=5):
    # add paginator object
    paginator = Paginator(list(checklist_upvotes), paginate_by)

    try:
        page_checklist_upvotes = paginator.page(page)
    except PageNotAnInteger:
        page_checklist_upvotes = paginator.page(1)
    except EmptyPage:
        page_checklist_upvotes = paginator.page(paginator.num_pages)

    return page_checklist_upvotes


def get_upvote_bookmark_list(checklists_var, is_anonymous, user):
    upvotes_cnt_list = []
    upvoted_bool_list = []
    bookmarked_bool_list = []

    for checklist in checklists_var:
        # for each checklist, fetch the count of upvotes
        # upvote_set - set of all upvotes who have foreign key checklist as the current checklist
        upvotes_cnt_list.append(checklist.upvote_set.count())

        # if user is not anonymous
        if not is_anonymous:

            # if any of the upvote objects have this checklist as foreign key and the user for that object is the current logged in user, then append True to the list
            if checklist.upvote_set.filter(user=user):
                upvoted_bool_list.append(True)
            else:
                upvoted_bool_list.append(False)

            if checklist.bookmark_set.filter(user=user):
                bookmarked_bool_list.append(True)
            else:
                bookmarked_bool_list.append(False)
        # need this else clause so that empty lists for upvoted and bookmarked are not passed in checklist_upvotes while zipping
        else:
            upvoted_bool_list.append(True)
            bookmarked_bool_list.append(True)

    return upvotes_cnt_list, upvoted_bool_list, bookmarked_bool_list


# CHECKLIST HOME - display all checklists order by most recent - this class is used when user navigates to "localhost:8000/"
class ChecklistListView(ListView):
    model = Checklist  # what model to query in order to create the list
    template_name = "checklist/home.html"  # <app_name>/<model>_<viewtype>.html
    paginate_by = 5
    # context_object_name = 'checklists'

    def get_context_data(self, **kwargs):
        context = super(ChecklistListView, self).get_context_data(**kwargs)

        # fetch checklists which are published and not in draft, use class method get_published_lists()
        checklists_var = Checklist.get_checklists(is_draft=False)
        # .exclude(author=self.request.user) - if user's own checklists not to be displayed on home page

        is_anonymous = self.request.user.is_anonymous
        user = self.request.user
        (
            upvotes_cnt_list,
            upvoted_bool_list,
            bookmarked_bool_list,
        ) = get_upvote_bookmark_list(checklists_var, is_anonymous, user)

        checklist_upvotes = zip(
            checklists_var,
            upvotes_cnt_list,
            upvoted_bool_list,
            bookmarked_bool_list,
        )  # ,followed_or_not_list)

        # add paginator object
        # paginator = Paginator(list(checklist_upvotes), self.paginate_by)
        page = self.request.GET.get("page")
        page_checklist_upvotes = paginate_content(
            checklist_upvotes, page, self.paginate_by
        )

        context["checklist_upvotes"] = page_checklist_upvotes
        context["title"] = "home"
        context["is_paginated"] = page_checklist_upvotes.has_other_pages

        return context

        """
        ---------- X ----------
        # This code snippet is for displaying followed users posts on top

        followed_checklists=Checklist.objects.none()

        for userFollowed in self.request.user.fromUser.all():
            followed_checklists = followed_checklists.union(userFollowed.toUser.checklist_set.filter(is_draft=False))

        # all checklists
        checklists_all = Checklist.objects.filter(is_draft=False)

        # those checklists which are written by authors not followed by the logged in user
        checklists_var = checklists_all.difference(followed_checklists).order_by('-date_posted')

        followed_or_not_list = ['Followed']*followed_checklists.count()
        followed_or_not_list.extend(['']*checklists_var.count())

        # arrange checklists by followed authors and then by non-followed authors
        checklists_var = list(chain(followed_checklists, checklists_var))

        ---------- X ----------
        """


# DISPLAY CHECKLISTS BY LOGGED IN USER
class UserChecklistListView(ListView):
    model = Checklist
    template_name = (
        "checklist/user_checklists.html"  # <app_name>/<model>_<viewtype>.html
    )
    paginate_by = 5

    # https://stackoverflow.com/a/36950584/6543250 - when to use get_queryset() vs get_context_data()

    # how to paginate when get_context_data() implemented
    # 1. https://stackoverflow.com/a/33485595/6543250
    # 2. https://docs.djangoproject.com/en/1.8/topics/pagination/#using-paginator-in-a-view
    def get_context_data(self, **kwargs):
        context = super(UserChecklistListView, self).get_context_data(**kwargs)

        user = get_object_or_404(User, username=self.kwargs.get("username"))

        if not self.request.user.is_anonymous:
            if self.request.user.fromUser.filter(toUser=user):
                if_followed = True
            else:
                if_followed = False
        else:
            if_followed = True

        # to protect draft checklists from being seen
        checklists_var = Checklist.get_checklists(is_draft=False, author=user)

        is_anonymous = self.request.user.is_anonymous
        user = self.request.user
        (
            upvotes_cnt_list,
            upvoted_bool_list,
            bookmarked_bool_list,
        ) = get_upvote_bookmark_list(checklists_var, is_anonymous, user)

        checklist_upvotes = zip(
            checklists_var,
            upvotes_cnt_list,
            upvoted_bool_list,
            bookmarked_bool_list,
        )

        # add paginator object
        page = self.request.GET.get("page")

        page_checklist_upvotes = paginate_content(
            checklist_upvotes, page, self.paginate_by
        )

        context["if_followed"] = if_followed
        context["checklist_upvotes"] = page_checklist_upvotes
        context["title"] = "user"
        context["is_paginated"] = page_checklist_upvotes.has_other_pages

        return context


# DRAFT CHECKLISTS BY USER
class UserDraftChecklistListView(LoginRequiredMixin, ListView):
    model = Checklist
    template_name = "checklist/user_checklists.html"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(UserDraftChecklistListView, self).get_context_data(**kwargs)

        upvotes_cnt_list = []
        upvoted_bool_list = []
        bookmarked_bool_list = []

        # to display only draft checklists
        checklists_var = Checklist.get_checklists(
            is_draft=True, author=self.request.user
        )

        for checklist in checklists_var:
            upvotes_cnt_list.append(checklist.upvote_set.count())

            upvoted_bool_list.append(False)
            bookmarked_bool_list.append(False)

        checklist_upvotes = zip(
            checklists_var,
            upvotes_cnt_list,
            upvoted_bool_list,
            bookmarked_bool_list,
        )

        page = self.request.GET.get("page")

        page_checklist_upvotes = paginate_content(
            checklist_upvotes, page, self.paginate_by
        )

        context["checklist_upvotes"] = page_checklist_upvotes
        context["draft"] = "draft"
        context["username"] = self.request.user.username
        context["is_paginated"] = page_checklist_upvotes.has_other_pages

        return context


# DISPLAY A SINGLE CHECKLIST
class ChecklistDetailView(DetailView):
    model = Checklist

    def get_context_data(self, **kwargs):
        context = super(ChecklistDetailView, self).get_context_data(**kwargs)

        chk = get_object_or_404(Checklist, id=self.kwargs.get("pk"))

        # if user is not anonymous, meaning user is logged in
        if not self.request.user.is_anonymous:
            if chk.upvote_set.filter(user=self.request.user):
                if_upvoted = True
            else:
                if_upvoted = False

            if chk.bookmark_set.filter(user=self.request.user):
                if_bookmarked = True
            else:
                if_bookmarked = False

            if FollowChecklist.objects.filter(toChecklist=chk).filter(
                fromUser=self.request.user
            ):
                if_followed = True
            else:
                if_followed = False
        else:
            if_upvoted = True
            if_bookmarked = True
            if_followed = True

        # if_upvoted and if_bookmarked are flags I use to toggle type of button shown on frontend but this is relevant only when user is logged in. If not logged in, this is not relevant.

        uvote = (
            chk.upvote_set.count()
        )  # Upvote.objects.filter(checklist_id=self.kwargs.get("pk")).count()
        itemset = chk.item_set.order_by("title")  # ,'completed')

        # for comments stuff:
        # 1. https://www.youtube.com/watch?v=KrGQ2Nrz4Dc
        # 2. https://djangocentral.com/creating-comments-system-with-django/

        comments = chk.comments.all().filter(parent=None)
        comment_form = CommentForm()

        context["if_upvoted"] = if_upvoted
        context["if_bookmarked"] = if_bookmarked
        context["if_followed"] = if_followed
        context["uvote"] = uvote
        context["itemset"] = itemset

        context["comments"] = comments
        context["comment_form"] = comment_form

        return context


# mixins need to be declared before the base class based views such as CreateView, DeleteView


# CREATE CHECKLIST
# LoginRequiredMixin - required so that the CBV can only be accessed when the user is logged in
class ChecklistCreateView(LoginRequiredMixin, CreateView):
    model = Checklist  # even though model is specified in ChecklistCreateForm, we need to specify the model again here
    fields = ["title", "content", "category", "is_draft"]
    # form_class = ChecklistCreateForm # to define custom form

    # to link logged in user as author to the checklist being created
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


# UPDATE CHECKLIST
# UserPassesTestMixin - required so that an author can only edit a checklist authored by them
class ChecklistUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Checklist
    fields = ["title", "content", "category", "is_draft"]

    # to link logged in user as author to the checklist being updated
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    # test_func is function invoked by the UserPassesTestMixin to see if our user passes a certain test condition
    def test_func(self):
        # method of the UpdateView which gives us the current object(model - Checklist in our case)
        checklist = self.get_object()
        # checks if currently logged in user is the checklist author
        return self.request.user == checklist.author


# DELETE CHECKLIST
# mixins required for delete view are the same as that of update
class ChecklistDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Checklist
    # url to redirect to when the deletion is a success
    success_url = "/"

    # checks if currently logged in user is the checklist author
    def test_func(self):
        checklist = self.get_object()
        return self.request.user == checklist.author


# VIEW BOOKMARKS PAGE
class BookmarkChecklistListView(LoginRequiredMixin, ListView):
    model = Bookmark
    template_name = "checklist/bookmark_checklists.html"
    paginate_by = 5

    # def get_queryset(self):
    #   return Bookmark.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(BookmarkChecklistListView, self).get_context_data(**kwargs)

        upvotes_cnt_list = []
        upvoted_bool_list = []

        bookmarks_var = Bookmark.objects.filter(user=self.request.user)

        for bookmark in bookmarks_var:
            upvotes_cnt_list.append(
                Upvote.objects.filter(checklist=bookmark.checklist).count()
            )

            if not self.request.user.is_anonymous:
                if bookmark.checklist.upvote_set.filter(user=self.request.user):
                    upvoted_bool_list.append(True)
                else:
                    upvoted_bool_list.append(False)

        checklist_upvotes = zip(bookmarks_var, upvotes_cnt_list, upvoted_bool_list)

        page = self.request.GET.get("page")

        page_checklist_upvotes = paginate_content(
            checklist_upvotes, page, self.paginate_by
        )

        context["checklist_upvotes"] = page_checklist_upvotes
        context["title"] = "bookmarks"
        context["is_paginated"] = page_checklist_upvotes.has_other_pages

        return context


# VIEW UPVOTE PAGE
class UpvoteChecklistListView(LoginRequiredMixin, ListView):
    model = Upvote
    template_name = "checklist/upvote_checklists.html"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(UpvoteChecklistListView, self).get_context_data(**kwargs)

        upvotes_cnt_list = []
        upvotes_var = Upvote.objects.filter(user=self.request.user)

        for upvote in upvotes_var:
            upvotes_cnt_list.append(
                Upvote.objects.filter(checklist=upvote.checklist).count()
            )

        checklist_upvotes = zip(upvotes_var, upvotes_cnt_list)

        page = self.request.GET.get("page")

        page_checklist_upvotes = paginate_content(
            checklist_upvotes, page, self.paginate_by
        )

        context["checklist_upvotes"] = page_checklist_upvotes
        context["title"] = "bookmarks"
        context["is_paginated"] = page_checklist_upvotes.has_other_pages

        return context


# SEARCH RESULTS PAGE
class SearchChecklistListView(ListView):
    model = Checklist
    template_name = "checklist/search_checklists.html"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(SearchChecklistListView, self).get_context_data(**kwargs)

        query = ""
        if self.request.GET:
            checklists_var = None
            # if a query string is present in URL
            if ("q" in self.request.GET) and self.request.GET["q"].strip():
                query = self.request.GET["q"]
                checklists_var = Checklist.objects.filter(
                    (Q(title__icontains=query) | Q(content__icontains=query))
                    & Q(is_draft=False)
                )

        is_anonymous = self.request.user.is_anonymous
        user = self.request.user
        (
            upvotes_cnt_list,
            upvoted_bool_list,
            bookmarked_bool_list,
        ) = get_upvote_bookmark_list(checklists_var, is_anonymous, user)

        checklist_upvotes = zip(
            checklists_var,
            upvotes_cnt_list,
            upvoted_bool_list,
            bookmarked_bool_list,
        )

        page = self.request.GET.get("page")

        page_checklist_upvotes = paginate_content(
            checklist_upvotes, page, self.paginate_by
        )

        context["checklist_upvotes"] = page_checklist_upvotes
        context["title"] = "search"
        context["is_paginated"] = page_checklist_upvotes.has_other_pages
        context["query_string"] = query

        return context


# DISPLAY CHECKLISTS FOR A CATEGORY PAGE
class CategoryChecklistListView(ListView):
    model = Checklist
    template_name = (
        "checklist/category_checklists.html"  # <app_name>/<model>_<viewtype>.html
    )
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(CategoryChecklistListView, self).get_context_data(**kwargs)

        category = get_object_or_404(Category, name=self.kwargs.get("category"))

        # category_id = Category.objects.filter(name=self.kwargs.get('category')).first().id
        checklists_var = Checklist.objects.filter(
            category_id=category.id, is_draft=False
        ).order_by("-date_posted")

        is_anonymous = self.request.user.is_anonymous
        user = self.request.user
        (
            upvotes_cnt_list,
            upvoted_bool_list,
            bookmarked_bool_list,
        ) = get_upvote_bookmark_list(checklists_var, is_anonymous, user)

        checklist_upvotes = zip(
            checklists_var,
            upvotes_cnt_list,
            upvoted_bool_list,
            bookmarked_bool_list,
        )

        page = self.request.GET.get("page")

        page_checklist_upvotes = paginate_content(
            checklist_upvotes, page, self.paginate_by
        )

        context["checklist_upvotes"] = page_checklist_upvotes
        context["title"] = "user"
        context["is_paginated"] = page_checklist_upvotes.has_other_pages

        return context


# CREATE ITEM
class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    fields = ["title"]

    checklist_id = 0

    # 1st method executed
    def dispatch(self, *args, **kwargs):
        self.checklist_id = self.kwargs.get("checklist_id")
        if Checklist.objects.get(id=self.checklist_id).author != self.request.user:

            # clear all messages
            system_messages = messages.get_messages(self.request)
            for message in system_messages:
                # This iteration is necessary
                pass
            system_messages.used = True

            msg = "Action Denied! You can only add items to your own checklist!"
            messages.info(self.request, msg)
            return redirect("checklist-detail", pk=self.checklist_id)
        else:
            return super().dispatch(*args, **kwargs)

    # 2nd method executed
    def form_valid(self, form):
        form.instance.checklist = Checklist.objects.get(id=self.checklist_id)
        return super().form_valid(form)


# DISPLAY A SINGLE ITEM
class ItemDetailView(DetailView):
    model = Item


# UPDATE ITEM
class ItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Item
    fields = ["title"]

    # # to link logged in user as author to the checklist being updated
    # def form_valid(self, form):
    #   form.instance.author = self.request.user
    #   return super().form_valid(form)

    # checks if currently logged in user is the checklist author
    def test_func(self):
        item = self.get_object()
        return self.request.user == item.checklist.author


# UPDATE COMMENT
class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    fields = ["body"]

    # to link logged in user as author to the checklist being updated
    def form_valid(self, form):
        return super().form_valid(form)

    # checks if currently logged in user is the checklist author
    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.user


# DELETE COMMENT
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    success_url = "/"

    # checks if currently logged in user is the checklist author
    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.user


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
        messages.info(request, msg)
    else:
        # remove user's upvote if he has already upvoted
        obj = Upvote.objects.filter(
            user=request.user, checklist=Checklist.objects.get(id=checklist_id)
        )
        if obj:
            obj.delete()
            msg = "Upvote retracted!"
            messages.info(request, msg)
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

            messages.info(request, msg)

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
        messages.info(request, msg)
    else:

        obj = Bookmark.objects.filter(
            user=request.user, checklist=Checklist.objects.get(id=checklist_id)
        )
        if obj:
            obj.delete()
            msg = "Bookmark removed!"
            messages.info(request, msg)
        else:
            bookmark_obj = Bookmark(
                user=request.user,
                checklist=Checklist.objects.get(id=checklist_id),
            )
            bookmark_obj.save()

            msg = "Checklist bookmarked!"
            messages.info(request, msg)

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
        messages.info(request, msg)
        return redirect(request.META.get("HTTP_REFERER", "checklist-home"))
    else:
        obj = Item.objects.get(id=item_id)

        if action_type == "complete":
            obj.completed = not obj.completed
            obj.save()

            msg = "Item Ticked/Un-ticked!"
        elif action_type == "delete":
            obj.delete()
            msg = "Item deleted"

        messages.info(request, msg)
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
        messages.info(request, msg)
    else:
        obj = Checklist.objects.get(id=checklist_id)
        obj.is_draft = False
        obj.save()

        msg = "Checklist published and removed from drafts"
        messages.info(request, msg)

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
        messages.info(request, msg)
    else:
        toUser = User.objects.filter(username=username).first()
        obj = Follow.objects.filter(fromUser=request.user, toUser=toUser)

        if obj:
            obj.delete()
            msg = "User unfollowed!"
        else:
            Follow(fromUser=request.user, toUser=toUser).save()
            msg = "User followed!"

            fromUser = request.user
            Notification(fromUser=fromUser, toUser=toUser, notif_type=2).save()

        messages.info(request, msg)

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
            messages.info(request, msg)

            return redirect("checklist-detail", new_obj.id)

        else:
            msg = "You have already saved this checklist once!"
            messages.info(request, msg)
    else:
        msg = "You can only save and edit others' checklists"
        messages.info(request, msg)

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
    # pass

    checklist = Checklist.objects.get(id=checklist_id)

    if request.user == checklist.author:
        msg = "Action Denied! You can not follow your own checklists!"
        messages.info(request, msg)
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

        messages.info(request, msg)

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
        if request.user == checklist.author:
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
                # Save the comment to the database
                new_comment.save()
    else:
        comment_form = CommentForm()

    return redirect(
        request.META.get("HTTP_REFERER", "checklist-home"),
        kwargs={
            "comments": comments,
            "new_comment": new_comment,
            "comment_form": comment_form,
        },
    )
