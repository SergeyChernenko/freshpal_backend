# Generated by Django 3.1.1 on 2022-06-25 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0014_auto_20220625_2317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publ',
            name='datetime',
            field=models.DateTimeField(null=True),
        ),
    ]