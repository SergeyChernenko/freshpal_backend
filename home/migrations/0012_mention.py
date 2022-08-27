# Generated by Django 3.1.1 on 2022-08-17 20:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0043_auto_20220817_2021'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0011_auto_20220812_0106'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mention',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.BooleanField(default=False)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('publication', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mainpage.publ')),
                ('username', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]