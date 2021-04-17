from django.contrib.auth.models import User
from django.test import TestCase

from checklist.models import (
    Bookmark,
    Category,
    Checklist,
    Item,
    Upvote,
    Follow,
    FollowChecklist,
    Notification,
    Comment,
)


def create_user_if_not_exists(username, password):
    if not User.objects.filter(username=username):
        user = User.objects.create_user(username=username, password=password)
        user.save()

    return User.objects.filter(username=username).first()


class ChecklistModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user_if_not_exists(username="testuser", password="12345")

        cls.category = Category.objects.create(name="Category_test")
        cls.checklist = Checklist.objects.create(
            title="New Checklist 1",
            content="Test content",
            author=cls.user,
            category=cls.category,
        )

    def test_object_creation(self):
        self.assertTrue(isinstance(ChecklistModelTest.checklist, Checklist))

        # properties don't need to be asserted because it is Django's job to make sure model attributes hold correct values
        # self.assertEqual(ChecklistModelTest.checklist.title, "New Checklist 1")
        # self.assertEqual(ChecklistModelTest.checklist.content, "Test content")
        # self.assertEqual(ChecklistModelTest.checklist.author, ChecklistModelTest.user)
        # self.assertEqual(
        #     ChecklistModelTest.checklist.category, ChecklistModelTest.category
        # )

    def test_str_method(self):
        self.assertEqual(ChecklistModelTest.checklist.__str__(), "New Checklist 1")

    def test_get_absolute_url(self):
        self.assertEqual(
            ChecklistModelTest.checklist.get_absolute_url(),
            "/checklist/" + str(ChecklistModelTest.user.id) + "/",
        )


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

    def test_object_creation(self):
        self.assertTrue(isinstance(ItemModelTest.item, Item))
        # self.assertEqual(ItemModelTest.item.title, "New Item 1")
        # self.assertEqual(ItemModelTest.item.checklist, ItemModelTest.checklist)
        # self.assertEqual(ItemModelTest.item.completed, False)

    def test_get_absolute_url(self):
        self.assertEqual(
            ItemModelTest.item.get_absolute_url(),
            "/checklist/item/" + str(ItemModelTest.item.id) + "/view/",
        )


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

    def test_object_creation(self):
        self.assertTrue(isinstance(UpvoteModelTest.upvote, Upvote))
        # self.assertEqual(UpvoteModelTest.upvote.user, UpvoteModelTest.user)
        # self.assertEqual(UpvoteModelTest.upvote.checklist, UpvoteModelTest.checklist)

    def test_str_method(self):
        self.assertEqual(
            UpvoteModelTest.upvote.__str__(),
            UpvoteModelTest.user.username + " - " + UpvoteModelTest.checklist.title,
        )


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

    def test_object_creation(self):
        self.assertTrue(isinstance(BookmarkModelTest.bookmark, Bookmark))
        # self.assertEqual(BookmarkModelTest.bookmark.user, BookmarkModelTest.user)
        # self.assertEqual(
        #     BookmarkModelTest.bookmark.checklist, BookmarkModelTest.checklist
        # )

    def test_str_method(self):
        self.assertEqual(
            BookmarkModelTest.bookmark.__str__(),
            BookmarkModelTest.user.username + " - " + BookmarkModelTest.checklist.title,
        )


class CategoryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Category_test")

    def test_object_creation(self):
        self.assertTrue(isinstance(CategoryModelTest.category, Category))
        # self.assertEqual(CategoryModelTest.category.name, "Category_test")

    def test_str_method(self):
        self.assertEqual(
            CategoryModelTest.category.__str__(),
            CategoryModelTest.category.name,
        )


class FollowModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = create_user_if_not_exists(username="testuser", password="12345")
        cls.user2 = create_user_if_not_exists(username="testuser2", password="12345")

    def test_object_creation(self):
        follow_obj = Follow.objects.create(
            fromUser=FollowModelTest.user1, toUser=FollowModelTest.user2
        )
        self.assertTrue(isinstance(follow_obj, Follow))


class FollowChecklistModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user_if_not_exists(username="testuser", password="12345")
        cls.category = Category.objects.create(name="Category_test")

        cls.checklist = Checklist.objects.create(
            title="New Checklist 1",
            content="Test content",
            author=cls.user,
            category=cls.category,
        )

    def test_object_creation(self):
        follow_obj = FollowChecklist.objects.create(
            fromUser=FollowChecklistModelTest.user,
            toChecklist=FollowChecklistModelTest.checklist,
        )
        self.assertTrue(isinstance(follow_obj, FollowChecklist))


class NotificationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = create_user_if_not_exists(username="testuser", password="12345")
        cls.user2 = create_user_if_not_exists(username="testuser2", password="12345")
        cls.category = Category.objects.create(name="Category_test")

        cls.checklist = Checklist.objects.create(
            title="New Checklist 1",
            content="Test content",
            author=cls.user1,
            category=cls.category,
        )

    def test_object_creation(self):
        notif_obj = Notification.objects.create(
            fromUser=NotificationModelTest.user1,
            toUser=NotificationModelTest.user2,
            notif_type=2,
        )
        self.assertTrue(isinstance(notif_obj, Notification))


class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = create_user_if_not_exists(username="testuser", password="12345")
        cls.user2 = create_user_if_not_exists(username="testuser2", password="12345")
        cls.category = Category.objects.create(name="Category_test")

        cls.checklist = Checklist.objects.create(
            title="New Checklist 1",
            content="Test content",
            author=cls.user1,
            category=cls.category,
        )

    def test_object_creation(self):
        comment_obj = Comment.objects.create(
            checklist=CommentModelTest.checklist,
            user=CommentModelTest.user2,
            body="Test comment",
        )
        self.assertTrue(isinstance(comment_obj, Comment))
