# Generated by Django 3.1.1 on 2022-07-20 22:19

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainpage', '0025_auto_20220721_0117'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PublRatingUsers',
            new_name='PublRatingUser',
        ),
    ]
