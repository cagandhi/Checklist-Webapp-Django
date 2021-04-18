from django.test import TestCase
from django.urls import resolve, reverse

from checklist.views import (
    CommentDeleteView,
    CommentUpdateView,
    ItemCreateView,
    ItemDetailView,
    ItemUpdateView,
)

from .helper_methods import (
    create_category_if_not_exists,
    create_checklist,
    create_comment,
    create_item,
    create_user_if_not_exists,
)


# test item CRUD views
class TestItemCreateView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.category = create_category_if_not_exists("test_category")
        self.list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
        )

    def test_view_url(self):
        url = resolve("/checklist/1/item/new/")
        self.assertEqual(url.func.__name__, ItemCreateView.__name__)

    def test_view_template_guest(self):
        response = self.client.get(reverse("item-create", kwargs={"checklist_id": 1}))
        self.assertEqual(response.status_code, 302)

    def test_view_template_login(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("item-create", kwargs={"checklist_id": 1}))
        self.assertTemplateUsed(response, "checklist/item_form.html")

    def test_create_item_guest(self):
        item_data = {"title": "item 1", "checklist": self.list1}

        response = self.client.post("/checklist/1/item/new/", data=item_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/checklist/1/")

    def test_create_item_login(self):
        self.client.login(username="testuser", password="12345")
        item_data = {"title": "item 1", "checklist": self.list1}

        response = self.client.post("/checklist/1/item/new/", data=item_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/checklist/item/1/view/")


class TestItemDetailView(TestCase):
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

        self.item1 = create_item(title="item 1", checklist=self.list1)

    def test_view_url(self):
        url = resolve("/checklist/item/1/view/")
        self.assertEqual(url.func.__name__, ItemDetailView.__name__)

    def test_view_template(self):
        response = self.client.get(reverse("item-detail", kwargs={"pk": 1}))
        self.assertTemplateUsed(response, "checklist/item_detail.html")

    def test_title(self):
        response = self.client.get(reverse("item-detail", kwargs={"pk": 1}))
        self.assertEqual(response.context["item"].title, "item 1")


class TestItemUpdateView(TestCase):
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

        self.item1 = create_item(title="item 1", checklist=self.list1)

    def test_view_url(self):
        url = resolve("/checklist/item/1/update/")
        self.assertEqual(url.func.__name__, ItemUpdateView.__name__)

    def test_view_template_guest(self):
        response = self.client.get(reverse("item-update", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 302)

    def test_view_template_login(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("item-update", kwargs={"pk": 1}))
        self.assertTemplateUsed(response, "checklist/item_form.html")

    def test_update_item_guest(self):
        item_data = {"title": "item 1", "checklist": self.list1}

        response = self.client.post(
            reverse("item-update", kwargs={"pk": 1}), data=item_data
        )
        self.assertEqual(response.status_code, 302)

    def test_update_checklist_login(self):
        self.client.login(username="testuser", password="12345")
        item_data = {"title": "item 1", "checklist": self.list1}

        response = self.client.post(
            reverse("checklist-update", kwargs={"pk": 1}), data=item_data
        )
        self.assertEqual(response.status_code, 200)


# test comment CRUD views
class TestCommentUpdateView(TestCase):
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

        self.comment_parent = create_comment(
            checklist=self.list1, user=self.user, body="Test comment 1", parent=None
        )

    def test_view_url(self):
        url = resolve("/comment/1/update/")
        self.assertEqual(url.func.__name__, CommentUpdateView.__name__)

    def test_view_template_guest(self):
        response = self.client.get(reverse("comment-update", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 302)

    def test_view_template_login(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("comment-update", kwargs={"pk": 1}))
        self.assertTemplateUsed(response, "checklist/comment_form.html")

    def test_update_comment_guest(self):
        comment_data = {
            "checklist": self.list1,
            "user": self.user,
            "body": "Update to comment 1",
        }

        response = self.client.post(
            reverse("comment-update", kwargs={"pk": 1}), data=comment_data
        )
        self.assertEqual(response.status_code, 302)

    def test_update_checklist_login(self):
        self.client.login(username="testuser", password="12345")
        comment_data = {
            "checklist": self.list1,
            "user": self.user,
            "body": "Update to comment 1",
        }

        response = self.client.post(
            reverse("comment-update", kwargs={"pk": 1}), data=comment_data
        )
        # because it redirects me to the edit form page
        self.assertEqual(response.status_code, 302)


class TestCommentDeleteView(TestCase):
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

        self.comment_parent = create_comment(
            checklist=self.list1, user=self.user, body="Test comment 1", parent=None
        )

    def test_view_url(self):
        url = resolve("/comment/1/delete/")
        self.assertEqual(url.func.__name__, CommentDeleteView.__name__)

    def test_view_template_guest(self):
        response = self.client.get(reverse("comment-delete", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 302)

    def test_view_template_login(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("comment-delete", kwargs={"pk": 1}))
        self.assertTemplateUsed(response, "checklist/comment_confirm_delete.html")

    def test_delete_comment_guest(self):
        response = self.client.post(reverse("comment-delete", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 302)

    def test_delete_checklist_login(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(reverse("comment-update", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)
