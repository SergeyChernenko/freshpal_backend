from rest_framework import serializers
from .models import UserProfile, Sub, Publ

class UserProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = UserProfile
    fields = ('id', 'username','birthday','avatar')

class SubSerializer(serializers.ModelSerializer):
  class Meta:
    model = Sub
    fields = ('id', 'username','subscriber')

class PublSerializer(serializers.ModelSerializer):
  class Meta:
    model = Publ
    fields = ('id', 'username','message','datetime')
