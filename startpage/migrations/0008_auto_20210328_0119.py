# Generated by Django 3.1.1 on 2021-03-27 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('startpage', '0007_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='birthday',
            field=models.DateField(blank=True, null=True),
        ),
    ]
