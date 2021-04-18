from django.test import TestCase
from django.urls import resolve, reverse

from checklist.views import (
    BookmarkChecklistListView,
    CategoryChecklistListView,
    SearchChecklistListView,
    UpvoteChecklistListView,
)

from checklist.tests.helper_methods import (
    create_bookmark_upvote,
    create_category_if_not_exists,
    create_checklist,
    create_user_if_not_exists,
)


class TestBookmarkChecklistListView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.category = create_category_if_not_exists("test_category")
        self.list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
            is_draft=False,
        )
        self.client.login(username="testuser", password="12345")

    def test_view_url(self):
        url = resolve("/bookmarks/")
        self.assertEqual(url.func.__name__, BookmarkChecklistListView.__name__)

    def test_view_template(self):
        response = self.client.get(reverse("bookmarks"))
        self.assertTemplateUsed(response, "checklist/bookmark_checklists.html")

    def test_no_bookmarks(self):
        response = self.client.get(reverse("bookmarks"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["checklist_upvotes"], [])

    def test_one_bookmark(self):
        book1 = create_bookmark_upvote(
            user=self.user, checklist=self.list1, if_bookmark=True
        )

        response = self.client.get(reverse("bookmarks"))
        self.assertEqual(response.context["checklist_upvotes"].number, 1)
        self.assertEqual(response.context["checklist_upvotes"][0][0], book1)


class TestUpvoteChecklistListView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.category = create_category_if_not_exists("test_category")
        self.list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
            is_draft=False,
        )
        self.client.login(username="testuser", password="12345")

    def test_view_url(self):
        url = resolve("/upvotes/")
        self.assertEqual(url.func.__name__, UpvoteChecklistListView.__name__)

    def test_view_template(self):
        response = self.client.get(reverse("upvotes"))
        self.assertTemplateUsed(response, "checklist/upvote_checklists.html")

    def test_no_upvotes(self):
        response = self.client.get(reverse("upvotes"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["checklist_upvotes"], [])

    def test_one_upvote(self):
        upvote1 = create_bookmark_upvote(
            user=self.user, checklist=self.list1, if_bookmark=False
        )

        response = self.client.get(reverse("upvotes"))
        self.assertEqual(response.context["checklist_upvotes"].number, 1)
        self.assertEqual(response.context["checklist_upvotes"][0][0], upvote1)


class TestSearchChecklistListView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.category = create_category_if_not_exists("test_category")
        self.list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
            is_draft=False,
        )
        self.client.login(username="testuser", password="12345")

    def test_view_url(self):
        url = resolve("/search/")
        self.assertEqual(url.func.__name__, SearchChecklistListView.__name__)

    def test_view_template_error(self):
        # lambda expression required because without lambda, client.get() will be executed which will result in error even before we check assertRaises()
        # https://stackoverflow.com/a/44269882/6543250
        self.assertRaises(UnboundLocalError, lambda: self.client.get(reverse("search")))

    def test_view_template_noerror(self):
        # https://docs.djangoproject.com/en/3.1/topics/testing/tools/#django.test.Client.get
        response = self.client.get(reverse("search"), {"q": "list"})
        self.assertTemplateUsed(response, "checklist/search_checklists.html")

    def test_search(self):
        response = self.client.get(reverse("search"), {"q": "list"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["checklist_upvotes"].number, 1)
        self.assertEqual(response.context["checklist_upvotes"][0][0], self.list1)


class TestCategoryChecklistListView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.category = create_category_if_not_exists("test_category")
        self.url = reverse("category", kwargs={"category": "test_category"})

    def test_view_url(self):
        url = resolve("/checklist/test_category/")
        self.assertEqual(url.func.__name__, CategoryChecklistListView.__name__)

    def test_view_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "checklist/category_checklists.html")

    def test_no_checklists(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["checklist_upvotes"], [])

    def test_one_checklist(self):
        list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
        )
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["checklist_upvotes"].number, 1)
        self.assertEqual(response.context["checklist_upvotes"][0][0], list1)
