from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from chomper.models import UserProfile, Profile, IntermediatePoint, RouteLine, RestaurantPoint

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Profile)



admin.site.register(IntermediatePoint,LeafletGeoAdmin)

admin.site.register(RouteLine,LeafletGeoAdmin)

admin.site.register(RestaurantPoint,LeafletGeoAdmin)
