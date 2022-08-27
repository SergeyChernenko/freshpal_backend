from django.db import models
from django.contrib.auth.models import User
from mainpage.models import Publ

class Hashtag(models.Model):
    publication = models.ForeignKey(Publ, on_delete=models.CASCADE, null=True)
    hashtag = models.TextField(max_length=400, null=True)
    datetime = models.DateTimeField(null=True)
    comment = models.BooleanField(default=False)
    censor = models.BooleanField(default=False)

class CurseWords(models.Model):
    word = models.TextField(max_length=400, null=True)

class Donat(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    sum = models.PositiveIntegerField(null=True)
    datetime = models.DateTimeField(auto_now_add=True, blank=True)

class Mention(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    publication = models.ForeignKey(Publ, on_delete=models.CASCADE, null=True)
    comment = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, blank=True)




