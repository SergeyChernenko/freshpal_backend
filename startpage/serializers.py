from rest_framework import serializers
from .models import Verification, RestorePassword
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id','username','password','email')
    extra_kwargs = {'password':{'write_only':True,'required':True}}

  def create(self, validated_data):
    user = User.objects.create_user(**validated_data)
    return user


class VerificationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Verification
    fields = ('id', 'email','code')


class RestorePasswordSerializer(serializers.ModelSerializer):
  class Meta:
    model = RestorePassword
    fields = ('id', 'username','token')



