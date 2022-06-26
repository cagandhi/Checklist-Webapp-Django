# mixins for checking if user is logged in and the checklist author is the same as logged in user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from checklist.models import Bookmark, Category, Checklist, Upvote

from .helper_methods import get_data_and_context, paginate_content


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

        context = get_data_and_context(
            context, self.request, self.paginate_by, checklists_var
        )
        context["title"] = "search"
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

        context = get_data_and_context(
            context, self.request, self.paginate_by, checklists_var
        )
        context["title"] = "user"

        return context
