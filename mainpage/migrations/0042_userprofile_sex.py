# Generated by Django 3.1.1 on 2022-08-17 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0041_userprofile_star'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='sex',
            field=models.TextField(max_length=6, null=True),
        ),
    ]