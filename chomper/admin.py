from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from chomper.models import UserProfile, Profile, InstagramProfile, TwitterProfile, LinkedinProfile, IntermediatePoint, RouteLine, RestaurantPoint

# Register your models here.
class TwitterProfileAdmin(admin.ModelAdmin):
	list_display = ('user','twitter_user')

admin.site.register(UserProfile)
admin.site.register(Profile)
admin.site.register(TwitterProfile, TwitterProfileAdmin)
admin.site.register(LinkedinProfile)



admin.site.register(IntermediatePoint,LeafletGeoAdmin)

admin.site.register(RouteLine,LeafletGeoAdmin)

admin.site.register(RestaurantPoint,LeafletGeoAdmin)
