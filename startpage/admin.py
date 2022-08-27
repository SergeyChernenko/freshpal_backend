from django.contrib import admin
from .models import Verification, RestorePassword

class VerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'code')

class RestorePasswordAdmin(admin.ModelAdmin):
    list_display = ('username', 'token')

admin.site.register(Verification, VerificationAdmin)
admin.site.register(RestorePassword, RestorePasswordAdmin)
