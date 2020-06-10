from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from djrichtextfield.models import RichTextField


class Checklist(models.Model):
	title = models.CharField(max_length=100)
	# https://pypi.org/project/django-richtextfield/ - to store rich text in database [ GitHub: https://github.com/jaap3/django-richtextfield ]
	content = RichTextField()
	date_posted = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(User, on_delete = models.CASCADE)
	visibility = models.PositiveIntegerField(default=0)
	category = models.ForeignKey('Category', null=True, on_delete = models.SET_NULL)
	is_draft = models.BooleanField(default=False)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('checklist-detail', kwargs={'pk': self.id})


class Item(models.Model):
	# LOW_PRIORITY = 1
	# MEDIUM_PRIORITY = 2
	# HIGH_PRIORITY = 3
	# PRIORITY_CHOICES = (
	# 	(LOW_PRIORITY, 'Low'),
	# 	(MEDIUM_PRIORITY, 'Medium'),
	# 	(HIGH_PRIORITY, 'High'),
	# )

	title = models.CharField(max_length=100)
	# priority = models.PositiveIntegerField(choices=PRIORITY_CHOICES, default=MEDIUM_PRIORITY)
	completed = models.BooleanField(default=False)
	checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE)

	def get_absolute_url(self):
		return reverse('checklist-detail', kwargs={'pk': self.checklist.id})


class Upvote(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE)

	def __str__(self):
		return self.user.username + " - " + self.checklist.title


class Bookmark(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE)

	def __str__(self):
		return self.user.username + " - " + self.checklist.title


class Category(models.Model):
	name = models.CharField(max_length=30)

	def __str__(self):
		return self.name


class Follow(models.Model):
	# why use related_name property - refer https://stackoverflow.com/a/2642645/6543250
	fromUser = models.ForeignKey(User, on_delete = models.CASCADE, related_name='fromUser')
	toUser = models.ForeignKey(User, on_delete = models.CASCADE, related_name='toUser')
