# Generated by Django 3.1.1 on 2021-04-13 20:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainpage', '0006_auto_20210413_2255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sub',
            name='subscriber',
            field=models.CharField(max_length=100, null=True, verbose_name='Subscriber'),
        ),
        migrations.AlterField(
            model_name='sub',
            name='username',
            field=models.CharField(max_length=100, null=True, verbose_name='Username'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.SmallIntegerField(null=True, verbose_name='Avatar'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='birthday',
            field=models.DateField(blank=True, null=True, verbose_name='Birthday'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='username',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Username'),
        ),
    ]