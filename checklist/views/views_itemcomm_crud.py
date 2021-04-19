from django.contrib import messages

# mixins for checking if user is logged in and the checklist author is the same as logged in user
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, reverse
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from checklist.models import Checklist, Comment, Item


# CREATE ITEM
class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    fields = ["title"]

    checklist_id = 0

    # refer https://stackoverflow.com/a/5926527/6543250
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
            messages.error(self.request, msg)
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
class CommentDeleteView(
    SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView
):
    model = Comment
    # success_url = "/"

    # checks if currently logged in user is the checklist author
    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.user

    # is accessed instead of success url attribute, refer https://stackoverflow.com/a/59475442/6543250
    def get_success_url(self):
        return reverse(
            "checklist-detail", kwargs={"pk": self.get_object().checklist.id}
        )

    def delete(self, request, *args, **kwargs):
        comment = self.get_object()
        # can_delete = (
        #     comment.parent is None
        #     and Comment.objects.filter(parent=comment).count() == 0
        # ) or (comment.parent is not None)

        cannot_delete = (
            comment.parent is None
            and Comment.objects.filter(parent=comment).count() != 0
        )
        if cannot_delete:
            messages.error(
                self.request,
                "You cannot delete your comment as there are replies to your comment now!",
            )
            return redirect("checklist-detail", comment.checklist.id)
            # return reverse("checklist-detail", kwargs={"pk": comment.checklist.id})
        else:
            messages.success(
                self.request, "Your comment has been successfully deleted!"
            )
            return super(CommentDeleteView, self).delete(request, *args, **kwargs)
