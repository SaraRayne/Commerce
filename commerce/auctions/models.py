from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=25, default=None)

    def __str__(self):
        return f"{self.category}"

class Listing(models.Model):
    title = models.CharField(max_length=64, default=None)
    description = models.TextField(default=None)
    starting_bid = models.DecimalField(max_digits=7, decimal_places=2)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    date = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, related_name="categories", blank=True)
    photo = models.URLField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listings")
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    amount = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f"{self.listing}"

class Watchlist(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watch_listings")

    def __str__(self):
        return f"{self.owner} is watching {self.listing}"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comment")
    commenter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    comment = models.TextField(default=None)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter}"
