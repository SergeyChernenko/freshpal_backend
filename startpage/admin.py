from django.contrib import admin
from .models import Verification, RestorePassword, ServerInfo

class VerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'code')

class RestorePasswordAdmin(admin.ModelAdmin):
    list_display = ('username', 'token')

class ServerInfoAdmin(admin.ModelAdmin):
    list_display = ('id','url')

admin.site.register(Verification, VerificationAdmin)
admin.site.register(RestorePassword, RestorePasswordAdmin)
admin.site.register(ServerInfo, ServerInfoAdmin)
