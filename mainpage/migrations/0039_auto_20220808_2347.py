# Generated by Django 3.1.1 on 2022-08-08 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0038_userprofile_now_visit'),
    ]

    operations = [
        migrations.AddField(
            model_name='publ',
            name='publ_user',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='publratinguser',
            name='publ_user',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
