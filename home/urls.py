from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views import HomeViewSet, HashtagViewSet, ActivityViewSet, DonatViewSet

router = routers.DefaultRouter()
router.register('home', HomeViewSet)
router.register('hashtag', HashtagViewSet)
router.register('activity', ActivityViewSet)
router.register('donat', DonatViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
