from django.test import TestCase
from checklist.models import Checklist, Category
from django.contrib.auth.models import User


# Create your tests here.
class ChecklistModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser", password="12345"
        )
        cls.user.save()

        cls.category = Category.objects.create(name="Category_test")
        cls.checklist = Checklist.objects.create(
            title="New Checklist 1",
            content="Test content",
            author=cls.user,
            category=cls.category,
        )

    def test_str_method(self):
        self.assertEqual(
            ChecklistModelTest.checklist.__str__(), "New Checklist 1"
        )

    def test_get_absolute_url(self):
        self.assertEqual(
            ChecklistModelTest.checklist.get_absolute_url(),
            "/checklist/" + str(ChecklistModelTest.user.id) + "/",
        )

    def tearDown(self):
        User.objects.filter(id=ChecklistModelTest.user.id).delete()
