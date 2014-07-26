from django.db import models
from datetime import datetime

class Subreddit(models.Model):
    name = models.CharField(max_length=20, unique=True, db_index=True)
    last_updated = models.DateTimeField(null=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def mark_updated(self):
        self.last_updated = datetime.now()

class User(models.Model):
    username = models.CharField(max_length=20, unique=True, db_index=True)
    last_updated = models.DateTimeField(null=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def mark_updated(self):
        self.last_updated = datetime.now()

class Moderator(models.Model):
    user = models.ForeignKey('User')
    subreddit = models.ForeignKey('Subreddit')
    is_deleted = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    added_on = models.DateTimeField(auto_now_add=True)
    deleted_on = models.DateTimeField(null=True)

    def mark_deleted(self):
        self.is_deleted = True
        self.deleted_on = datetime.now()
        self.save()

    def undelete(self):
        self.is_deleted = False
        self.deleted_on = None
        self.save()