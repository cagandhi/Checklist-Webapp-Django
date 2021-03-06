from django.contrib.auth.models import User
from django.test import TestCase

from checklist.models import Bookmark, Category, Checklist, Item, Upvote


class ChecklistModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="12345")
        cls.user.save()

        cls.category = Category.objects.create(name="Category_test")
        cls.checklist = Checklist.objects.create(
            title="New Checklist 1",
            content="Test content",
            author=cls.user,
            category=cls.category,
        )

    def test_str_method(self):
        self.assertEqual(ChecklistModelTest.checklist.__str__(), "New Checklist 1")

    def test_get_absolute_url(self):
        self.assertEqual(
            ChecklistModelTest.checklist.get_absolute_url(),
            "/checklist/" + str(ChecklistModelTest.user.id) + "/",
        )

    def tearDown(self):
        User.objects.filter(id=ChecklistModelTest.user.id).delete()


class ItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="12345")
        cls.user.save()

        cls.category = Category.objects.create(name="Category_test")
        cls.checklist = Checklist.objects.create(
            title="New Checklist 1",
            content="Test content",
            author=cls.user,
            category=cls.category,
        )

        cls.item = Item.objects.create(title="New Item 1", checklist=cls.checklist)

    def test_get_absolute_url(self):
        self.assertEqual(
            ItemModelTest.item.get_absolute_url(),
            "/checklist/item/" + str(ItemModelTest.item.id) + "/view/",
        )

    def tearDown(self):
        User.objects.filter(id=ChecklistModelTest.user.id).delete()


class UpvoteModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="12345")
        cls.user.save()

        cls.category = Category.objects.create(name="Category_test")
        cls.checklist = Checklist.objects.create(
            title="New Checklist 1",
            content="Test content",
            author=cls.user,
            category=cls.category,
        )

        cls.upvote = Upvote.objects.create(user=cls.user, checklist=cls.checklist)

    def test_str_method(self):
        self.assertEqual(
            UpvoteModelTest.upvote.__str__(),
            UpvoteModelTest.user.username + " - " + UpvoteModelTest.checklist.title,
        )

    def tearDown(self):
        User.objects.filter(id=BookmarkModelTest.user.id).delete()


class BookmarkModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="12345")
        cls.user.save()

        cls.category = Category.objects.create(name="Category_test")
        cls.checklist = Checklist.objects.create(
            title="New Checklist 1",
            content="Test content",
            author=cls.user,
            category=cls.category,
        )

        cls.bookmark = Bookmark.objects.create(user=cls.user, checklist=cls.checklist)

    def test_str_method(self):
        self.assertEqual(
            BookmarkModelTest.bookmark.__str__(),
            BookmarkModelTest.user.username + " - " + BookmarkModelTest.checklist.title,
        )

    def tearDown(self):
        User.objects.filter(id=BookmarkModelTest.user.id).delete()


class CategoryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Category_test")

    def test_str_method(self):
        self.assertEqual(
            CategoryModelTest.category.__str__(),
            CategoryModelTest.category.name,
        )
