# Generated by Django 3.1.1 on 2021-04-04 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0002_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sub',
            name='subscriber',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='sub',
            name='username',
            field=models.CharField(max_length=100, null=True),
        ),
    ]