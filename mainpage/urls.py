from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views import UserProfileViewSet, SubscribeViewSet, AvatarViewSet, PublViewSet, RatingViewSet

router = routers.DefaultRouter()
router.register('user_profile', UserProfileViewSet)
router.register('subscribe', SubscribeViewSet)
router.register('avatar', AvatarViewSet)
router.register('publ', PublViewSet)
router.register('rating', RatingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
