from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import resolve, reverse

from .helper_methods import (
    create_category_if_not_exists,
    create_checklist,
    create_item,
    create_notif,
    create_user_if_not_exists,
)


# test view functions
class TestAboutView(TestCase):
    def test_view_url(self):
        url = resolve("/about/")
        self.assertEqual(url.func.__name__, "about")

    def test_view_template(self):
        response = self.client.get(reverse("checklist-about"))
        self.assertTemplateUsed(response, "checklist/about.html")


class TestUpvoteChecklistView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.user2 = create_user_if_not_exists("testuser2", "12345")

        self.category = create_category_if_not_exists("test_category")
        self.list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
            is_draft=False,
        )

    def test_view_url(self):
        url = resolve("/checklist/1/upvote/")
        self.assertEqual(url.func.__name__, "upvote_checklist")

    def test_upvote_guest(self):
        response = self.client.get(
            reverse("checklist-upvote", kwargs={"checklist_id": 1})
        )
        self.assertEqual(response.status_code, 302)

    def test_upvote_login_author(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(
            reverse("checklist-upvote", kwargs={"checklist_id": 1})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Action Denied! You cannot upvote your own checklist!"
        )
        self.assertRedirects(response, "/", status_code=302)

    def test_upvote_login_other(self):
        self.client.login(username="testuser2", password="12345")
        response = self.client.get(
            reverse("checklist-upvote", kwargs={"checklist_id": 1})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Checklist upvoted!")
        self.assertRedirects(response, "/", status_code=302)

    def test_remove_upvote_other(self):
        self.client.login(username="testuser2", password="12345")
        response = self.client.get(
            reverse("checklist-upvote", kwargs={"checklist_id": 1})
        )

        response = self.client.get(
            reverse("checklist-upvote", kwargs={"checklist_id": 1})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), "Checklist upvoted!")
        self.assertEqual(str(messages[1]), "Upvote retracted!")
        self.assertRedirects(response, "/", status_code=302)


class TestBookmarkChecklistView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.user2 = create_user_if_not_exists("testuser2", "12345")

        self.category = create_category_if_not_exists("test_category")
        self.list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
            is_draft=False,
        )

    def test_view_url(self):
        url = resolve("/checklist/1/bookmark/")
        self.assertEqual(url.func.__name__, "bookmark_checklist")

    def test_bookmark_guest(self):
        response = self.client.get(
            reverse("checklist-bookmark", kwargs={"checklist_id": 1})
        )
        self.assertEqual(response.status_code, 302)

    def test_bookmark_login_author(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(
            reverse("checklist-bookmark", kwargs={"checklist_id": 1})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Action Denied! You cannot bookmark your own checklist!"
        )
        self.assertRedirects(response, "/", status_code=302)

    def test_bookmark_login_other(self):
        self.client.login(username="testuser2", password="12345")
        response = self.client.get(
            reverse("checklist-bookmark", kwargs={"checklist_id": 1})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Checklist bookmarked!")
        self.assertRedirects(response, "/", status_code=302)

    def test_remove_bookmark_other(self):
        self.client.login(username="testuser2", password="12345")
        response = self.client.get(
            reverse("checklist-bookmark", kwargs={"checklist_id": 1})
        )

        response = self.client.get(
            reverse("checklist-bookmark", kwargs={"checklist_id": 1})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), "Checklist bookmarked!")
        self.assertEqual(str(messages[1]), "Bookmark removed!")
        self.assertRedirects(response, "/", status_code=302)


class TestItemActionView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.user2 = create_user_if_not_exists("testuser2", "12345")

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
        url = resolve("/checklist/item/1/complete/")
        self.assertEqual(url.func.__name__, "item_action")

    def test_complete_guest(self):
        response = self.client.get(
            reverse("item-action", kwargs={"item_id": 1, "action_type": "complete"})
        )
        self.assertEqual(response.status_code, 302)

    def test_complete_author(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(
            reverse("item-action", kwargs={"item_id": 1, "action_type": "complete"})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Item Ticked/Un-ticked!")
        self.assertRedirects(response, "/checklist/1/", status_code=302)

    def test_complete_other(self):
        self.client.login(username="testuser2", password="12345")
        response = self.client.get(
            reverse("item-action", kwargs={"item_id": 1, "action_type": "complete"})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Action Denied! You can only make changes to your own checklist!",
        )
        self.assertRedirects(response, "/", status_code=302)

    def test_delete_guest(self):
        response = self.client.get(
            reverse("item-action", kwargs={"item_id": 1, "action_type": "delete"})
        )
        self.assertEqual(response.status_code, 302)

    def test_delete_author(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(
            reverse("item-action", kwargs={"item_id": 1, "action_type": "delete"})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Item deleted!")
        self.assertRedirects(response, "/checklist/1/", status_code=302)

    def test_delete_other(self):
        self.client.login(username="testuser2", password="12345")
        response = self.client.get(
            reverse("item-action", kwargs={"item_id": 1, "action_type": "delete"})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Action Denied! You can only make changes to your own checklist!",
        )
        self.assertRedirects(response, "/", status_code=302)


class TestPublishChecklistView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.user2 = create_user_if_not_exists("testuser2", "12345")

        self.category = create_category_if_not_exists("test_category")
        self.list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
            is_draft=True,
        )

    def test_view_url(self):
        url = resolve("/checklist/1/publish/")
        self.assertEqual(url.func.__name__, "publish_checklist")

    def test_view_template_guest(self):
        response = self.client.get(
            reverse("checklist-publish", kwargs={"checklist_id": 1})
        )
        self.assertEqual(response.status_code, 302)

    def test_view_template_login(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(
            reverse("checklist-publish", kwargs={"checklist_id": 1})
        )
        self.assertEqual(response.status_code, 302)

    def test_publish_guest(self):
        response = self.client.get(
            reverse("checklist-publish", kwargs={"checklist_id": 1})
        )
        self.assertEqual(response.status_code, 302)

    def test_publish_login_author(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(
            reverse("checklist-publish", kwargs={"checklist_id": 1})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Checklist published and removed from drafts!"
        )
        self.assertRedirects(response, "/", status_code=302)

    def test_publish_login_other(self):
        self.client.login(username="testuser2", password="12345")
        response = self.client.get(
            reverse("checklist-publish", kwargs={"checklist_id": 1})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Action Denied! You can only publish your own checklist!"
        )
        self.assertRedirects(response, "/", status_code=302)


class TestFollowUserView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.user2 = create_user_if_not_exists("testuser2", "12345")

    def test_view_url(self):
        url = resolve("/user/testuser/follow/")
        self.assertEqual(url.func.__name__, "follow_user")

    def test_follow_guest(self):
        response = self.client.get(
            reverse("user-follow", kwargs={"username": "testuser"})
        )
        self.assertEqual(response.status_code, 302)

    def test_follow_self(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(
            reverse("user-follow", kwargs={"username": "testuser"})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Action Denied! You can only follow other users!"
        )
        self.assertRedirects(response, "/", status_code=302)

    def test_follow_other(self):
        self.client.login(username="testuser2", password="12345")
        response = self.client.get(
            reverse("user-follow", kwargs={"username": "testuser"})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "User followed!")
        self.assertRedirects(response, "/", status_code=302)

    def test_unfollow(self):
        self.client.login(username="testuser2", password="12345")
        response = self.client.get(
            reverse("user-follow", kwargs={"username": "testuser"})
        )

        response = self.client.get(
            reverse("user-follow", kwargs={"username": "testuser"})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), "User followed!")
        self.assertEqual(str(messages[1]), "User unfollowed!")
        self.assertRedirects(response, "/", status_code=302)


class TestSaveAndEditView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.user2 = create_user_if_not_exists("testuser2", "12345")

        self.category = create_category_if_not_exists("test_category")
        self.list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
            is_draft=True,
        )

    def test_view_url(self):
        url = resolve("/checklist/1/save/")
        self.assertEqual(url.func.__name__, "save_and_edit")

    def test_view_template_guest(self):
        response = self.client.get(
            reverse("checklist-save", kwargs={"checklist_id": 1})
        )
        self.assertEqual(response.status_code, 302)

    def test_view_template_login(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(
            reverse("checklist-save", kwargs={"checklist_id": 1})
        )
        self.assertEqual(response.status_code, 302)

    def test_save_and_edit_self(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(
            reverse("checklist-save", kwargs={"checklist_id": 1})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "You can only save and edit others' checklists!"
        )
        self.assertRedirects(response, "/checklist/1/", status_code=302)

    def test_save_and_edit_other(self):
        self.client.login(username="testuser2", password="12345")
        response = self.client.get(
            reverse("checklist-save", kwargs={"checklist_id": 1})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Checklist saved. You can now modify it as your own!"
        )
        self.assertRedirects(response, "/checklist/2/", status_code=302)

    def test_save_and_edit_again(self):
        self.client.login(username="testuser2", password="12345")
        response = self.client.get(
            reverse("checklist-save", kwargs={"checklist_id": 1})
        )

        response = self.client.get(
            reverse("checklist-save", kwargs={"checklist_id": 1})
        )
        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(
            str(messages[0]), "Checklist saved. You can now modify it as your own!"
        )
        self.assertEqual(
            str(messages[1]), "You have already saved this checklist once!"
        )
        self.assertRedirects(response, "/", status_code=302)


class TestDismissNotifView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.user2 = create_user_if_not_exists("testuser2", "12345")

        # self.category = create_category_if_not_exists("test_category")
        # self.list1 = create_checklist(
        #     title="list 1",
        #     content="content 1",
        #     user=self.user,
        #     category=self.category,
        #     is_draft=True,
        # )

        self.notif = create_notif(self.user2, self.user, 2)

    def test_view_url(self):
        url = resolve("/notif/1/dismiss/")
        self.assertEqual(url.func.__name__, "dismiss_notif")

    def test_view_template_guest(self):
        response = self.client.get(reverse("dismiss-notif", kwargs={"id": 1}))
        self.assertEqual(response.status_code, 302)

    def test_view_template_login(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("dismiss-notif", kwargs={"id": 1}))
        self.assertEqual(response.status_code, 302)

    def test_dismiss_notif_self(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("dismiss-notif", kwargs={"id": 1}))
        self.assertRedirects(response, "/", status_code=302)

    def test_dismiss_notif_other(self):
        self.client.login(username="testuser2", password="12345")
        response = self.client.get(reverse("dismiss-notif", kwargs={"id": 1}))
        self.assertRedirects(response, "/", status_code=302)


class TestFollowChecklistView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        self.user2 = create_user_if_not_exists("testuser2", "12345")

        self.category = create_category_if_not_exists("test_category")
        self.list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
            is_draft=True,
        )

    def test_view_url(self):
        url = resolve("/checklist/1/follow/")
        self.assertEqual(url.func.__name__, "follow_checklist")

    def test_view_template_guest(self):
        response = self.client.get(
            reverse("checklist-follow", kwargs={"checklist_id": 1})
        )
        self.assertEqual(response.status_code, 302)

    def test_follow_checklist_self(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(
            reverse("checklist-follow", kwargs={"checklist_id": 1})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Action Denied! You can not follow your own checklists!"
        )
        # redirected to home because self.client.get is activated upon the server start meaning from the home page and hence am redirected back to home page
        self.assertRedirects(response, "/", status_code=302)

    def test_follow_checklist_other(self):
        self.client.login(username="testuser2", password="12345")
        response = self.client.get(
            reverse("checklist-follow", kwargs={"checklist_id": 1})
        )

        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Checklist followed!")
        self.assertRedirects(response, "/", status_code=302)

    def test_unfollow_checklist_other(self):
        self.client.login(username="testuser2", password="12345")
        response = self.client.get(
            reverse("checklist-follow", kwargs={"checklist_id": 1})
        )

        response = self.client.get(
            reverse("checklist-follow", kwargs={"checklist_id": 1})
        )
        # refer https://stackoverflow.com/a/14909727/6543250
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), "Checklist followed!")
        self.assertEqual(str(messages[1]), "Checklist unfollowed!")
        self.assertRedirects(response, "/", status_code=302)


class TestSubmitCommentView(TestCase):
    def setUp(self):
        self.user = create_user_if_not_exists("testuser", "12345")
        _ = create_user_if_not_exists("testuser2", "12345")
        self.category = create_category_if_not_exists("test_category")
        self.list1 = create_checklist(
            title="list 1",
            content="content 1",
            user=self.user,
            category=self.category,
            is_draft=False,
        )

    def test_view_url(self):
        url = resolve("/checklist/1/comment/")
        self.assertEqual(url.func.__name__, "submit_comment")

    def test_view_template_guest(self):
        response = self.client.get(
            reverse("comment-submit", kwargs={"checklist_id": 1})
        )
        self.assertEqual(response.status_code, 302)

    def test_view_template_login(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(
            reverse("comment-submit", kwargs={"checklist_id": 1}),
            data={"body": "This is body of the comment"},
        )
        self.assertEqual(response.status_code, 302)

    def test_submit_comment_self(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(
            reverse("comment-submit", kwargs={"checklist_id": 1}),
            data={"body": "This is body of the comment"},
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Author can only to reply to others' comments!"
        )
        self.assertRedirects(
            response,
            reverse("checklist-detail", kwargs={"pk": 1}),
            status_code=302,
        )

    def test_submit_comment_other(self):
        self.client.login(username="testuser2", password="12345")
        response = self.client.post(
            reverse("comment-submit", kwargs={"checklist_id": 1}),
            data={"body": "This is body of the comment"},
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Your comment has been saved!")
        self.assertRedirects(
            response,
            reverse("checklist-detail", kwargs={"pk": 1}),
            status_code=302,
        )
