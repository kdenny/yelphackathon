from django.db import models
from django.contrib.auth.models import User
from djgeojson.fields import PointField, LineStringField
import datetime

from djgeojson.serializers import Serializer as GeoJSONSerializer


class RestaurantPoint(models.Model):
    geom = PointField()
    name = models.TextField(max_length=200)
    rating = models.FloatField(max_length=5)
    isclosed = models.BooleanField(default=False)
    address = models.TextField(max_length=200)

    @property
    def popupContent(self):
        return '{0}<br>{1}'.format(
          self.name,
          self.rating)

class IntermediatePoint(models.Model):
    geom = PointField()

class RouteLine(models.Model):
    geom = LineStringField()


# Create your models here.
class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username

class Profile(models.Model):
    user = models.ForeignKey(User)
    oauth_token = models.CharField(max_length=200)
    oauth_secret = models.CharField(max_length=200)
    name = models.TextField(max_length=200)
    age = models.IntegerField()
    address = models.TextField(max_length=200, default="250 K Street NE Washington, DC")
    logindate = models.DateTimeField(default=datetime.datetime.now, blank=True)

    def __unicode__(self):
        return unicode(self.user)


class InstagramProfile(models.Model):
    user = models.ForeignKey(User)
    instagram_user = models.CharField(max_length=200)
    access_token = models.CharField(max_length=200)

    def __unicode__(self):
        return unicode(self.user)

class TwitterProfile(models.Model):
    user = models.ForeignKey(User)
    twitter_user = models.CharField(max_length=200)
    oauth_token = models.CharField(max_length=200)
    oauth_token_secret = models.CharField(max_length=200)

    def __unicode__(self):
        return unicode(self.user)

class LinkedinProfile(models.Model):
    user = models.ForeignKey(User)
    linkedin_user = models.CharField(max_length=200)
    access_token = models.CharField(max_length=200)

    def __unicode__(self):
        return unicode(self.user)

class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)

    class Meta:
        ordering = ('created',)

class FacebookProfile(models.Model):
    user = models.ForeignKey(User)
    fb_user_id = models.CharField(max_length=100)
    time_created = models.DateTimeField(auto_now_add=True)
    profile_url = models.CharField(max_length=50)
    access_token = models.CharField(max_length=100)

class GoogleProfile(models.Model):
    user = models.ForeignKey(User)
    google_user_id = models.CharField(max_length=100)
    time_created = models.DateTimeField(auto_now_add=True)
    access_token = models.CharField(max_length=100)
    profile_url = models.CharField(max_length=100)



