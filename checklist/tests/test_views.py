from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from checklist.models import Category, Checklist
from checklist.views import (ChecklistDetailView, ChecklistListView,
                             UserChecklistListView, UserDraftChecklistListView,)


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
