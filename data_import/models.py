from django.db import models
from django.utils import timezone


class Subreddit(models.Model):
    name = models.CharField(max_length=20, unique=True, db_index=True)
    last_updated = models.DateTimeField(null=True)
    added_on = models.DateTimeField(auto_now_add=True)
    member_count = models.PositiveIntegerField(null=True)
    priority = models.PositiveIntegerField(default=1)

    def mark_updated(self):
        self.last_updated = timezone.now()
        self.save()


class User(models.Model):
    username = models.CharField(max_length=20, unique=True, db_index=True)
    last_updated = models.DateTimeField(null=True)
    added_on = models.DateTimeField(auto_now_add=True)
    is_bot = models.BooleanField(default=False)
    is_private = models.NullBooleanField(null=True)

    def mark_updated(self):
        self.last_updated = timezone.now()
        self.save()


class Moderator(models.Model):
    user = models.ForeignKey('User')
    subreddit = models.ForeignKey('Subreddit')
    is_deleted = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    added_on = models.DateTimeField(auto_now_add=True)
    deleted_on = models.DateTimeField(null=True)

    def mark_deleted(self):
        self.is_deleted = True
        self.deleted_on = timezone.now()
        self.save()

    def undelete(self):
        self.is_deleted = False
        self.deleted_on = None
        self.save()
