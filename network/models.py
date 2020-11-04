from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Count


class User(AbstractUser):
    follow_users = models.ManyToManyField("network.User", related_name="followers", blank=True)

    def following_count(self):
        # if self.follow_users is None:
        #     return 0
        return self.follow_users.aggregate(Count('pk'))['pk__count']

    def followers_count(self):
        # if self.followers is None:
        #     return 0
        return self.followers.aggregate(Count('pk'))['pk__count']


class Post(models.Model):
    creator = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=10000)
    timestamp = models.DateTimeField(auto_now_add=True)

    def num_likes(self):
        return self.likes.aggregate(Count('pk'))['pk__count']

    def is_liking(self, user):
        for like in self.likes.all():
            if like.creator == user:
                return True
        return False


class Like(models.Model):
    creator = models.ForeignKey("User", on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
