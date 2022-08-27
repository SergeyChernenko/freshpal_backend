from django.contrib import admin
from .models import Sub, UserProfile, Publ, Rating, PublRating, PublRatingUser, UserProfileStar

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'description', 'sex', 'success', 'last_visit', 'birthday', 'level', 'like', 'sum', 'positive','censor','nude')

class UserProfileStarAdmin(admin.ModelAdmin):
    list_display = ('username', 'star')

class SubAdmin(admin.ModelAdmin):
    list_display = ('username', 'subscriber','datetime')

class PublAdmin(admin.ModelAdmin):
    list_display = ('username', 'message', 'datetime', 'parent_id', 'publ_user', 'edit','remote','censor','nude')

class RatingAdmin(admin.ModelAdmin):
    list_display = ('level', 'like', 'sum')

class PublRatingAdmin(admin.ModelAdmin):
    list_display = ('publication', 'level', 'sum', 'sum_like', 'sum_dislike', 'positive')

class PublRatingUserAdmin(admin.ModelAdmin):
    list_display = ('publication', 'username', 'like', 'positive', 'publ_user', 'datetime')

admin.site.register(Sub, SubAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Publ, PublAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(PublRating, PublRatingAdmin)
admin.site.register(PublRatingUser, PublRatingUserAdmin)
admin.site.register(UserProfileStar, UserProfileStarAdmin)
