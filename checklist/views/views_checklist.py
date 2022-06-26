import logging

# mixins for checking if user is logged in and the checklist author is the same as logged in user
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from checklist.forms import CommentForm
from checklist.models import Checklist, FollowChecklist

from .helper_methods import get_data_and_context

logger = logging.getLogger(__name__)


# CHECKLIST HOME - display all checklists order by most recent - this class is used when user navigates to "localhost:8000/"
class ChecklistListView(ListView):
    model = Checklist  # what model to query in order to create the list
    template_name = "checklist/home.html"  # <app_name>/<model>_<viewtype>.html
    paginate_by = 5
    # context_object_name = 'checklists'

    def get_context_data(self, **kwargs):
        context = super(ChecklistListView, self).get_context_data(**kwargs)

        # fetch checklists which are published and not in draft, use class method get_checklists()
        checklists_var = Checklist.get_checklists(is_draft=False)
        # .exclude(author=self.request.user) - if user's own checklists not to be displayed on home page

        context = get_data_and_context(
            context, self.request, self.paginate_by, checklists_var
        )

        context["title"] = "home"
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

        context = get_data_and_context(
            context, self.request, self.paginate_by, checklists_var
        )

        context["if_followed"] = if_followed
        context["title"] = "user"
        return context


# DRAFT CHECKLISTS BY USER
class UserDraftChecklistListView(LoginRequiredMixin, ListView):
    model = Checklist
    template_name = "checklist/user_checklists.html"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(UserDraftChecklistListView, self).get_context_data(**kwargs)

        # to display only draft checklists
        checklists_var = Checklist.get_checklists(
            is_draft=True, author=self.request.user
        )

        context = get_data_and_context(
            context, self.request, self.paginate_by, checklists_var
        )

        # upvotes_cnt_list = []
        # upvoted_bool_list = []
        # bookmarked_bool_list = []

        # for checklist in checklists_var:
        #     upvotes_cnt_list.append(checklist.upvote_set.count())
        #     upvoted_bool_list.append(False)
        #     bookmarked_bool_list.append(False)

        context["draft"] = "draft"
        context["username"] = self.request.user.username
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
