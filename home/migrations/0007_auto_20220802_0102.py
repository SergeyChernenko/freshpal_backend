# Generated by Django 3.1.1 on 2022-08-01 22:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_hashtag_tag_censor'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hashtag',
            old_name='tag_censor',
            new_name='censor',
        ),
    ]
