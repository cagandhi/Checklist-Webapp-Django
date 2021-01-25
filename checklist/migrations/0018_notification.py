# Generated by Django 3.0.4 on 2021-01-25 00:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('checklist', '0017_remove_item_priority'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_notified', models.DateTimeField(default=django.utils.timezone.now)),
                ('msg', models.CharField(max_length=500)),
                ('fromUser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fromUserNotif', to=settings.AUTH_USER_MODEL)),
                ('toUser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='toUserNotif', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
