# Generated by Django 3.1.1 on 2021-03-25 22:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('startpage', '0005_auto_20210326_0141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restorepassword',
            name='username',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]