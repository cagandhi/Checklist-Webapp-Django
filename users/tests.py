import os
from io import BytesIO

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import resolve, reverse


class TestProfileModel(TestCase):
    def test_str_method(self):
        username = "testuser"
        if not User.objects.filter(username=username):
            user = User.objects.create_user(username=username, password="12345")
            user.save()

        user = User.objects.filter(username=username).first()
        self.assertEqual(user.profile.__str__(), username + " Profile")


class TestRegisterView(TestCase):
    def test_view_url(self):
        url = resolve("/register/")
        self.assertEqual(url.func.__name__, "register")

    def test_view_template(self):
        response = self.client.get(reverse("register"))
        self.assertTemplateUsed(response, "users/register.html")

    def get_user_data():
        return {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password1": "My12345password",
            "password2": "My12345password",
        }

    def test_register_success(self):
        # password is more complicated because without that, form_valid() was not getting evaluated to True, refer https://stackoverflow.com/q/57337720/6543250
        user_data = self.get_user_data()
        response = self.client.post("/register/", data=user_data)
        self.assertRedirects(response, reverse("login"), status_code=302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Your account with username testuser has been created successfully! You can now log in!",
        )
        self.assertEqual(User.objects.count(), 1)

    def test_register_failure(self):
        user_data = self.get_user_data()
        response = self.client.post("/register/", data=user_data)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)


class TestProfileView(TestCase):
    def setUp(self):
        username = "testuser"
        self.user = User.objects.create_user(username=username, password="12345")
        self.user.save()

    def test_view_url(self):
        url = resolve("/profile/")
        self.assertEqual(url.func.__name__, "profile")

    def test_view_template(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)

    def get_user_data():
        return {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password1": "My12345password",
            "password2": "My12345password",
        }

    def test_profile_update_success(self):
        self.client.login(username="testuser", password="12345")

        user_data = self.get_user_data()
        response = self.client.post("/register/", data=user_data)

        user_data = {
            "username": "testuser123",
            "email": "testuser@gmail.com",
        }
        response = self.client.post("/profile/", data=user_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.first().username, "testuser123")

    def test_profile_update_failure(self):
        self.client.login(username="testuser", password="12345")

        user_data = self.get_user_data()
        _ = self.client.post("/register/", data=user_data)

        user_data = {
            "username": "testuser123",
            "email": "testuser@gmail.",
        }
        _ = self.client.post("/profile/", data=user_data)
        self.assertEqual(User.objects.first().username, "testuser")

    def test_image_update_success(self):
        self.client.login(username="testuser", password="12345")

        parent_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        img_path = os.path.join(parent_path, "media", "profile_pics", "android.JPG")
        img = BytesIO(img_path.encode("utf-8"))
        img.name = "android.JPG"

        user_data = {"name": "android.JPG", "image": img}
        response = self.client.post("/profile/", data=user_data)
        self.assertEqual(response.status_code, 200)
