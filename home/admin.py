from django.contrib import admin
from .models import Hashtag, Donat, Mention

class HashtagAdmin(admin.ModelAdmin):
    list_display = ('publication', 'hashtag', 'datetime', 'comment','censor')

class DonatAdmin(admin.ModelAdmin):
    list_display = ('username', 'sum', 'datetime')

class MentionAdmin(admin.ModelAdmin):
    list_display = ('username', 'publication', 'comment', 'datetime')

admin.site.register(Hashtag, HashtagAdmin)
admin.site.register(Donat, DonatAdmin)
admin.site.register(Mention, MentionAdmin)