# Generated by Django 3.1.1 on 2022-07-20 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0020_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='level',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='positive',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='sum',
            field=models.PositiveBigIntegerField(null=True),
        ),
    ]
