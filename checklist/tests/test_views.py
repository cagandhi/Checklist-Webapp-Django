from checklist.models import Bookmark, Category, Checklist
from checklist.views import (BookmarkChecklistListView, ChecklistCreateView,
                             ChecklistDeleteView, ChecklistDetailView,
                             ChecklistListView, ChecklistUpdateView,
                             UpvoteChecklistListView, UserChecklistListView,
                             UserDraftChecklistListView,)
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse


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


def create_bookmark_upvote(user, checklist):
    return Bookmark.objects.create(user=user, checklist=checklist)


# wrap unit tests for a class
class TestChecklistListView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.category = create_category_if_not_exists("test_category")

    def test_view_url(self):
        url = resolve("/")
        self.assertEqual(url.func.__name__, ChecklistListView.__name__)

    def test_view_template(self):
        response = self.client.get(reverse("checklist-home"))
        self.assertTemplateUsed(response, "checklist/home.html")

    def test_no_lists(self):
        response = self.client.get(reverse("checklist-home"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["checklist_upvotes"], [])

    def test_one_list(self):
        list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
        )

        response = self.client.get(reverse("checklist-home"))
        self.assertEqual(response.context["checklist_upvotes"].number, 1)
        self.assertEqual(response.context["checklist_upvotes"][0][0], list1)

    def test_two_lists(self):
        list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
        )
        list2 = create_checklist(
            title="list 2",
            content="content 2",
            user=self.user,
            category=self.category,
        )

        response = self.client.get(reverse("checklist-home"))
        self.assertEqual(response.context["checklist_upvotes"].number, 1)
        self.assertEqual(response.context["checklist_upvotes"][0][0], list2)
        self.assertEqual(response.context["checklist_upvotes"][1][0], list1)

    # https://stackoverflow.com/a/9493533/6543250 - teardown not extremely useful for database flushing since that is handled by django.test.TestCase
    def tearDown(self):
        self.user.delete()


class TestUserChecklistListView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.category = create_category_if_not_exists("test_category")

    def test_view_url(self):
        url = resolve("/user/testuser/")
        self.assertEqual(url.func.__name__, UserChecklistListView.__name__)

    def test_view_template(self):
        response = self.client.get(
            reverse("user-checklists", kwargs={"username": "testuser"})
        )
        self.assertTemplateUsed(response, "checklist/user_checklists.html")

    def test_no_lists(self):
        response = self.client.get(
            reverse("user-checklists", kwargs={"username": "testuser"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["checklist_upvotes"], [])

    def test_one_list(self):
        list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
        )

        response = self.client.get(
            reverse("user-checklists", kwargs={"username": "testuser"})
        )
        self.assertEqual(response.context["checklist_upvotes"].number, 1)
        self.assertEqual(response.context["checklist_upvotes"][0][0], list1)

    def test_two_lists(self):
        list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
        )
        list2 = create_checklist(
            title="list 2",
            content="content 2",
            user=self.user,
            category=self.category,
        )

        response = self.client.get(
            reverse("user-checklists", kwargs={"username": "testuser"})
        )
        self.assertEqual(response.context["checklist_upvotes"].number, 1)
        self.assertEqual(response.context["checklist_upvotes"][0][0], list2)
        self.assertEqual(response.context["checklist_upvotes"][1][0], list1)

    def tearDown(self):
        self.user.delete()


class TestUserDraftChecklistListView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.category = create_category_if_not_exists("test_category")

    def test_view_url(self):
        url = resolve("/checklist/drafts/")
        self.assertEqual(url.func.__name__, UserDraftChecklistListView.__name__)

    def test_view_template(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("user-drafts"))
        self.assertTemplateUsed(response, "checklist/user_checklists.html")

    def test_no_lists_login(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("user-drafts"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["checklist_upvotes"], [])

    def test_no_lists_nologin(self):
        response = self.client.get(reverse("user-drafts"))

        self.assertEqual(response.status_code, 302)
        self.assertRaises(TypeError, lambda: response.context["checklist_upvotes"])

    def test_one_list(self):
        self.client.login(username="testuser", password="12345")
        list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
            is_draft=True,
        )

        response = self.client.get(reverse("user-drafts"))
        self.assertEqual(response.context["checklist_upvotes"].number, 1)
        self.assertEqual(response.context["checklist_upvotes"][0][0], list1)

    def test_one_list_nologin(self):
        list1 = create_checklist(  # noqa: F841
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
            is_draft=True,
        )

        response = self.client.get(reverse("user-drafts"))
        self.assertEqual(response.status_code, 302)
        self.assertRaises(TypeError, lambda: response.context["checklist_upvotes"])

    def test_two_lists(self):
        self.client.login(username="testuser", password="12345")
        list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
            is_draft=True,
        )
        list2 = create_checklist(
            title="list 2",
            content="content 2",
            user=self.user,
            category=self.category,
            is_draft=True,
        )

        response = self.client.get(reverse("user-drafts"))
        self.assertEqual(response.context["checklist_upvotes"].number, 1)
        self.assertEqual(response.context["checklist_upvotes"][0][0], list2)
        self.assertEqual(response.context["checklist_upvotes"][1][0], list1)

    def tearDown(self):
        self.user.delete()


class TestChecklistDetailView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.category = create_category_if_not_exists("test_category")

        self.client.login(username="testuser", password="12345")
        self.list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
            is_draft=True,
        )

    def test_view_url(self):
        url = resolve("/checklist/1/")
        self.assertEqual(url.func.__name__, ChecklistDetailView.__name__)

    def test_view_template(self):
        response = self.client.get(reverse("checklist-detail", kwargs={"pk": 1}))
        self.assertTemplateUsed(response, "checklist/checklist_detail.html")

    def test_title(self):
        response = self.client.get(reverse("checklist-detail", kwargs={"pk": 1}))
        self.assertEqual(response.context["checklist"].title, "list 1")

    def tearDown(self):
        self.user.delete()


class TestChecklistCreateView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.category = create_category_if_not_exists("test_category")
        self.client.login(username="testuser", password="12345")

    def test_view_url(self):
        url = resolve("/checklist/new/")
        self.assertEqual(url.func.__name__, ChecklistCreateView.__name__)

    def test_view_template(self):
        response = self.client.get(reverse("checklist-create"))
        self.assertTemplateUsed(response, "checklist/checklist_form.html")

    def test_create_checklist(self):
        # rf = RequestFactory()
        list_data = {
            "title": "list 1",
            "content": "content 1",
            "category": self.category,
            "is_draft": False,
        }
        response = self.client.post("/checklist/new/", data=list_data)
        self.assertEqual(response.status_code, 200)


class TestChecklistUpdateView(TestCase):
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
        url = resolve("/checklist/1/update/")
        self.assertEqual(url.func.__name__, ChecklistUpdateView.__name__)

    def test_view_template(self):
        response = self.client.get(reverse("checklist-update", kwargs={"pk": 1}))
        self.assertTemplateUsed(response, "checklist/checklist_form.html")

    def test_update_checklist(self):
        list_data = {
            "title": "list 1 updated",
            "content": "content 1",
            "category": self.category,
        }

        response = self.client.post(
            reverse("checklist-update", kwargs={"pk": 1}), data=list_data
        )
        self.assertEqual(response.status_code, 200)


class TestChecklistDeleteView(TestCase):
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
        url = resolve("/checklist/1/delete/")
        self.assertEqual(url.func.__name__, ChecklistDeleteView.__name__)

    def test_view_template(self):
        response = self.client.get(reverse("checklist-delete", kwargs={"pk": 1}))
        self.assertTemplateUsed(response, "checklist/checklist_confirm_delete.html")

    # refer https://stackoverflow.com/a/16010105/6543250 for the following methods
    def test_delete_checklist_get_request(self):
        response = self.client.get(
            reverse("checklist-delete", kwargs={"pk": 1}), follow=True
        )
        self.assertContains(response, "Are you sure you want to delete the checklist?")

    def test_delete_checklist_post_request(self):
        post_response = self.client.post(
            reverse("checklist-delete", kwargs={"pk": 1}), follow=True
        )
        self.assertRedirects(post_response, reverse("checklist-home"), status_code=302)


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
        book1 = create_bookmark_upvote(user=self.user, checklist=self.list1)

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
        upvote1 = create_bookmark_upvote(user=self.user, checklist=self.list1)

        response = self.client.get(reverse("bookmarks"))
        self.assertEqual(response.context["checklist_upvotes"].number, 1)
        self.assertEqual(response.context["checklist_upvotes"][0][0], upvote1)
