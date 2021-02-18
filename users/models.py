from django.db import models
from django.contrib.auth.models import User
from PIL import Image  # noqa: F401


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpg", upload_to="profile_pics")

    def __str__(self):
        return f"{self.user.username} Profile"

    # # When you are overriding model's save method in Django, you should also pass *args and **kwargs to overridden method.
    # def save(self, *args, **kwargs):
    # 	super().save(*args, **kwargs)

    # 	img = Image.open(self.image.path)

    # 	if img.height>300 or img.width>300:
    # 		output_size = (300, 300)
    # 		img.thumbnail(output_size)
    # 		img.save(self.image.path)
