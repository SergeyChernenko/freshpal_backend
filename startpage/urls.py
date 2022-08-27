from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views import UserViewSet, VerificationViewSet, RestorePasswordViewSet, RegistrationViewSet

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('verification', VerificationViewSet)
router.register('restore_password', RestorePasswordViewSet)
router.register('registration',RegistrationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
