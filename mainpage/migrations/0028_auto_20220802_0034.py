# Generated by Django 3.1.1 on 2022-08-01 21:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainpage', '0027_publ_remote'),
    ]

    operations = [
        migrations.AddField(
            model_name='sub',
            name='datetime',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='sub',
            name='subscriber',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subscriber', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='sub',
            name='username',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
