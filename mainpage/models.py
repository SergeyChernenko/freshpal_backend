from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    birthday = models.DateField(blank=True, null=True)
    success = models.BooleanField(default=False)
    level = models.FloatField(null=True)
    like = models.PositiveIntegerField(null=True)
    sum = models.PositiveBigIntegerField(null=True)
    positive = models.BooleanField(default=True)
    description = models.TextField(max_length=400, null=True)
    now_visit = models.DateTimeField(null=True)
    last_visit = models.DateTimeField(null=True)
    censor = models.BooleanField(default=False)
    nude = models.BooleanField(default=False)
    sex = models.CharField(max_length=6, null=True)

class UserProfileStar(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    star = models.PositiveIntegerField(null=True)

class Sub(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='subscriber')
    datetime = models.DateTimeField(auto_now_add=True, blank=True)

class Publ(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    message = models.TextField(max_length=400, null=True)
    datetime = models.DateTimeField(null=True)
    edit = models.BooleanField(default=False)
    parent_id = models.IntegerField(null=True)
    publ_user = models.PositiveIntegerField(null=True)
    remote = models.BooleanField(default=False)
    censor = models.BooleanField(default=False)
    nude = models.BooleanField(default=False)


class PublRating(models.Model):
    publication = models.ForeignKey(Publ, on_delete=models.CASCADE, null=True)
    level = models.FloatField(null=True)
    sum = models.PositiveBigIntegerField(null=True)
    sum_like = models.PositiveIntegerField(null=True)
    sum_dislike = models.PositiveIntegerField(null=True)
    positive = models.BooleanField(default=True)

class PublRatingUser(models.Model):
    publication = models.ForeignKey(Publ, on_delete=models.CASCADE, null=True)
    publ_user = models.PositiveIntegerField(null=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    like = models.PositiveIntegerField(null=True)
    positive = models.BooleanField(default=True)
    datetime = models.DateTimeField(auto_now_add=True, blank=True)

class Rating(models.Model):
    level = models.PositiveIntegerField(null=True)
    like = models.PositiveIntegerField(null=True)
    sum = models.PositiveBigIntegerField(null=True)

