# Generated by Django 3.1.1 on 2021-03-25 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('startpage', '0003_auto_20210326_0124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restorepassword',
            name='token',
            field=models.CharField(max_length=200),
        ),
    ]
