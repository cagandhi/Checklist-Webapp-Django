# Generated by Django 3.0.4 on 2020-05-12 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklist', '0002_auto_20200313_0230'),
    ]

    operations = [
        migrations.AddField(
            model_name='checklist',
            name='upvotes',
            field=models.IntegerField(default=0),
        ),
    ]