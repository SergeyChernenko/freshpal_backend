# Generated by Django 3.1.1 on 2022-08-05 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0034_auto_20220804_0412'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='censor',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='nude',
            field=models.BooleanField(default=True),
        ),
    ]
