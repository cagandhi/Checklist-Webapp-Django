from django.test import TestCase
from django.urls import resolve, reverse

from checklist.tests.helper_methods import (
    create_category_if_not_exists,
    create_checklist,
    create_user_if_not_exists,
)
from checklist.views import (
    ChecklistCreateView,
    ChecklistDeleteView,
    ChecklistDetailView,
    ChecklistListView,
    ChecklistUpdateView,
    UserChecklistListView,
    UserDraftChecklistListView,
)


# test listviews and detailviews
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

    def test_no_lists_guest(self):
        response = self.client.get(reverse("user-drafts"))

        self.assertEqual(response.status_code, 302)
        # lambda expression required because without lambda, client.get() will be executed which will result in error even before we check assertRaises()
        # https://stackoverflow.com/a/44269882/6543250
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

    def test_one_list_guest(self):
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


# test checklist CRUD views
class TestChecklistDetailView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.category = create_category_if_not_exists("test_category")

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


class TestChecklistCreateView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.category = create_category_if_not_exists("test_category")

    def test_view_url(self):
        url = resolve("/checklist/new/")
        self.assertEqual(url.func.__name__, ChecklistCreateView.__name__)

    def test_view_template_guest(self):
        response = self.client.get(reverse("checklist-create"))
        self.assertEqual(response.status_code, 302)

    def test_view_template_login(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("checklist-create"))
        self.assertTemplateUsed(response, "checklist/checklist_form.html")

    def test_create_checklist_guest(self):
        list_data = {
            "title": "list 1",
            "content": "content 1",
            "category": self.category,
            "is_draft": False,
        }
        response = self.client.post("/checklist/new/", data=list_data)
        self.assertEqual(response.status_code, 302)

    def test_create_checklist_login(self):
        self.client.login(username="testuser", password="12345")
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

    def test_view_url(self):
        url = resolve("/checklist/1/update/")
        self.assertEqual(url.func.__name__, ChecklistUpdateView.__name__)

    def test_view_template_guest(self):
        response = self.client.get(reverse("checklist-update", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 302)

    def test_view_template_login(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("checklist-update", kwargs={"pk": 1}))
        self.assertTemplateUsed(response, "checklist/checklist_form.html")

    def test_update_checklist_guest(self):
        list_data = {
            "title": "list 1 updated",
            "content": "content 1",
            "category": self.category,
        }

        response = self.client.post(
            reverse("checklist-update", kwargs={"pk": 1}), data=list_data
        )
        self.assertEqual(response.status_code, 302)

    def test_update_checklist_login(self):
        self.client.login(username="testuser", password="12345")
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

        # self.client.login(username="testuser", password="12345")

    def test_view_url(self):
        url = resolve("/checklist/1/delete/")
        self.assertEqual(url.func.__name__, ChecklistDeleteView.__name__)

    def test_view_template_guest(self):
        response = self.client.get(reverse("checklist-delete", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 302)

    def test_view_template_login(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("checklist-delete", kwargs={"pk": 1}))
        self.assertTemplateUsed(response, "checklist/checklist_confirm_delete.html")

    def test_delete_checklist_get_request_guest(self):
        response = self.client.get(
            reverse("checklist-delete", kwargs={"pk": 1}), follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_checklist_post_request_guest(self):
        post_response = self.client.post(
            reverse("checklist-delete", kwargs={"pk": 1}), follow=True
        )
        self.assertRedirects(
            post_response,
            "/login/?next=" + reverse("checklist-delete", kwargs={"pk": 1}),
            status_code=302,
        )

    # refer https://stackoverflow.com/a/16010105/6543250 for the following methods
    def test_delete_checklist_get_request_login(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(
            reverse("checklist-delete", kwargs={"pk": 1}), follow=True
        )
        self.assertContains(response, "Are you sure you want to delete the checklist?")

    def test_delete_checklist_post_request_login(self):
        self.client.login(username="testuser", password="12345")
        post_response = self.client.post(
            reverse("checklist-delete", kwargs={"pk": 1}), follow=True
        )
        self.assertRedirects(post_response, reverse("checklist-home"), status_code=302)
