from django.db import models
from django.contrib.auth.models import User

class Verification(models.Model):
    email = models.CharField(max_length=100, verbose_name="Email")
    code = models.CharField(max_length=100, verbose_name="Code")

class RestorePassword(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name="Username")
    token = models.CharField(max_length=100, verbose_name="Token")

User._meta.get_field('email').blank = False




