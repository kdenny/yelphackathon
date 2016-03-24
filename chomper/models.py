from django.db import models
from django.contrib.auth.models import User
from djgeojson.fields import PointField, LineStringField
import datetime

from djgeojson.serializers import Serializer as GeoJSONSerializer


class RestaurantPoint(models.Model):
    geom = PointField()
    name = models.TextField(max_length=200)
    rid = models.CharField(max_length=10)
    rating = models.FloatField(max_length=5)
    origdist = models.CharField(max_length=10)
    origdirlink = models.TextField(max_length=200)
    destdist = models.CharField(max_length=10)
    extradist = models.CharField(max_length=10)
    link = models.TextField(max_length=200)
    Color = models.TextField(max_length=200)
    CentColor = models.TextField(max_length=200)
    isclosed = models.BooleanField(default=False)
    address = models.TextField(max_length=200)

    @property
    def popupContent(self):
        return '<b>{0} </b><a id="yelp" class="fancybox fancybox.iframe" target="_blank" href={5}>(link)</a><br>Rating: {1}<br>Origin Time: {2} min <a href={6}>(Get Directions)</a><br>Destination Time: {3} min <br>Out of the Way Time: {4} min'.format(
          self.name,
          self.rating,
          self.origdist,
          self.destdist,
          self.extradist,
          self.link,
          self.origdirlink)

class IntermediatePoint(models.Model):
    geom = PointField()

class UserPoint(models.Model):
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

class UserLocation(models.Model):
    user = models.ForeignKey(User)
    address = models.TextField(max_length=200, default="250 K Street NE")
    latlng = models.OneToOneField(UserPoint)

    def __unicode__(self):
        return unicode(self.address)

class Profile(models.Model):
    user = models.ForeignKey(User)
    oauth_token = models.CharField(max_length=200)
    oauth_secret = models.CharField(max_length=200)
    name = models.TextField(max_length=200)
    age = models.IntegerField()
    location = models.ManyToManyField(UserLocation)
    logindate = models.DateTimeField(default=datetime.datetime.now, blank=True)

    def __unicode__(self):
        return unicode(self.user)


class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)

    class Meta:
        ordering = ('created',)



