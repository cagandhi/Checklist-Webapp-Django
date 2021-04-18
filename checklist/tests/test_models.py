from django.contrib.auth.models import User
from django.test import TestCase

from checklist.models import (
    Bookmark,
    Category,
    Checklist,
    Comment,
    Follow,
    FollowChecklist,
    Item,
    Notification,
    Upvote,
)

from .helper_methods import (
    create_bookmark_upvote,
    create_category_if_not_exists,
    create_checklist,
    create_comment,
    create_item,
    create_notif,
    create_user_if_not_exists,
)


# test classes
class TestChecklistModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user_if_not_exists(username="testuser", password="12345")

        cls.category = create_category_if_not_exists("Category_test")
        cls.checklist = create_checklist(
            title="New Checklist 1",
            content="Test content",
            user=cls.user,
            category=cls.category,
        )

    def test_object_creation(self):
        self.assertTrue(isinstance(TestChecklistModel.checklist, Checklist))

    def test_str_method(self):
        self.assertEqual(TestChecklistModel.checklist.__str__(), "New Checklist 1")

    def test_get_absolute_url(self):
        self.assertEqual(
            TestChecklistModel.checklist.get_absolute_url(),
            "/checklist/" + str(TestChecklistModel.user.id) + "/",
        )


class TestItemModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user_if_not_exists(username="testuser", password="12345")
        cls.category = create_category_if_not_exists("Category_test")
        cls.checklist = create_checklist(
            title="New Checklist 1",
            content="Test content",
            user=cls.user,
            category=cls.category,
        )
        cls.item = create_item(title="New Item 1", checklist=cls.checklist)

    def test_object_creation(self):
        self.assertTrue(isinstance(TestItemModel.item, Item))

    def test_get_absolute_url(self):
        self.assertEqual(
            TestItemModel.item.get_absolute_url(),
            "/checklist/item/" + str(TestItemModel.item.id) + "/view/",
        )


class TestUpvoteModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user_if_not_exists(username="testuser", password="12345")
        cls.category = create_category_if_not_exists("Category_test")
        cls.checklist = create_checklist(
            title="New Checklist 1",
            content="Test content",
            user=cls.user,
            category=cls.category,
        )

        cls.upvote = create_bookmark_upvote(
            user=cls.user, checklist=cls.checklist, if_bookmark=False
        )

    def test_object_creation(self):
        self.assertTrue(isinstance(TestUpvoteModel.upvote, Upvote))

    def test_str_method(self):
        self.assertEqual(
            TestUpvoteModel.upvote.__str__(),
            TestUpvoteModel.user.username + " - " + TestUpvoteModel.checklist.title,
        )


class TestBookmarkModel(TestCase):
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

        cls.bookmark = create_bookmark_upvote(
            user=cls.user, checklist=cls.checklist, if_bookmark=True
        )

    def test_object_creation(self):
        self.assertTrue(isinstance(TestBookmarkModel.bookmark, Bookmark))

    def test_str_method(self):
        self.assertEqual(
            TestBookmarkModel.bookmark.__str__(),
            TestBookmarkModel.user.username + " - " + TestBookmarkModel.checklist.title,
        )


class TestCategoryModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Category_test")

    def test_object_creation(self):
        self.assertTrue(isinstance(TestCategoryModel.category, Category))

    def test_str_method(self):
        self.assertEqual(
            TestCategoryModel.category.__str__(),
            TestCategoryModel.category.name,
        )


class TestFollowModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = create_user_if_not_exists(username="testuser", password="12345")
        cls.user2 = create_user_if_not_exists(username="testuser2", password="12345")

    def test_object_creation(self):
        follow_obj = Follow.objects.create(
            fromUser=TestFollowModel.user1, toUser=TestFollowModel.user2
        )
        self.assertTrue(isinstance(follow_obj, Follow))


class TestFollowChecklistModel(TestCase):
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
            fromUser=TestFollowChecklistModel.user,
            toChecklist=TestFollowChecklistModel.checklist,
        )
        self.assertTrue(isinstance(follow_obj, FollowChecklist))


class TestNotificationModel(TestCase):
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
        notif_obj = create_notif(
            fromUser=TestNotificationModel.user1,
            toUser=TestNotificationModel.user2,
            notif_type=2,
        )
        self.assertTrue(isinstance(notif_obj, Notification))


class TestCommentModel(TestCase):
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
        comment_obj = create_comment(
            checklist=TestCommentModel.checklist,
            user=TestCommentModel.user2,
            body="Test comment",
        )

        self.assertTrue(isinstance(comment_obj, Comment))
