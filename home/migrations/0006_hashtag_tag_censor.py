# Generated by Django 3.1.1 on 2022-08-01 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_auto_20220729_0052'),
    ]

    operations = [
        migrations.AddField(
            model_name='hashtag',
            name='tag_censor',
            field=models.BooleanField(default=False),
        ),
    ]
