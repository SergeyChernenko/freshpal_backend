# Generated by Django 3.1.1 on 2022-07-28 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hashtag',
            name='hashtag',
            field=models.TextField(max_length=100, null=True),
        ),
    ]
