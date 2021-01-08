from django.test import TestCase, Client
from checklist.views import ChecklistListView
from django.urls import reverse, resolve

from checklist.models import (
    Checklist,
    Category,
    Item,
    Upvote,
    Bookmark,
    Follow,
)
from django.contrib.auth.models import User


def create_user_if_not_exists(username, password):
    if not User.objects.filter(username=username):
        user = User.objects.create_user(username=username, password=password)
        user.save()

    return User.objects.filter(username=username).first()


def create_category_if_not_exists(name):
    if not Category.objects.filter(name=name):
        Category.objects.create(name=name)

    return Category.objects.filter(name=name).first()


def create_checklist(title, content, user, category):
    return Checklist.objects.create(
        title=title,
        content=content,
        author=user,
        category=category,
    )


class TestChecklistListView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.category = create_category_if_not_exists("test_category")

    def test_checklist_list_view_url(self):
        url = resolve("/")
        self.assertEqual(url.func.__name__, ChecklistListView.__name__)

    def test_checklist_list_view_template(self):
        response = self.client.get(reverse("checklist-home"))
        self.assertTemplateUsed(response, "checklist/home.html")

    def test_no_questions(self):
        response = self.client.get(reverse("checklist-home"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["checklist_upvotes"], [])

    def test_one_question(self):
        list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
        )

        response = self.client.get(reverse("checklist-home"))
        self.assertEqual(response.context["checklist_upvotes"].number, 1)
        self.assertEqual(response.context["checklist_upvotes"][0][0], list1)

    def test_two_questions(self):
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
