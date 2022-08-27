from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.authentication import get_authorization_header

from freshpal import settings
from .models import Verification, RestorePassword
from .serializers import UserSerializer, VerificationSerializer, RestorePasswordSerializer
from mainpage.models import UserProfile
from mainpage.serializers import UserProfileSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.utils import timezone

from uuid import uuid4
import numpy as np
import smtplib
import jwt
import os
from PIL import Image

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (AllowAny,)

  @action(methods=['POST'], detail=False)
  def count(self, request):
    res = User.objects.filter().count()
    return Response(res, status=status.HTTP_200_OK)


def send_code_email(email, code):
  addr_from = "freshpalcode@gmail.com"
  addr_to = email
  password = "freshpal2021"

  msg = MIMEMultipart()
  msg['From'] = addr_from
  msg['To'] = addr_to
  msg['Subject'] = 'Код верификации'

  body = '''Для подтверждения личности просим ввести данный код в поле проверки. 
  Код подтверждения  - {}'''.format(code)
  msg.attach(MIMEText(body, 'plain'))

  server = smtplib.SMTP('smtp.gmail.com', 587)
  server.set_debuglevel(True)
  server.starttls()
  server.login(addr_from, password)
  server.send_message(msg)
  server.quit()

class VerificationViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (AllowAny,)

  @action(methods=['POST'], detail=False)
  def check_data(self, request):
    result = []
    exception = ['new','rec','activity','hashtag','settings','support','donat']
    if User.objects.filter(username=request.data['username']).exists():
      result.append(False)
    else:
      if str(request.data['username']) in exception:
        result.append(False)
      else:
        result.append(True)
    if User.objects.filter(email=request.data['email']).exists():
      result.append(False)
    else:
      result.append(True)
    return Response(result, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def send_code(self, request):
    try:
      if Verification.objects.filter(email=request.data['email']).exists():
        Verification.objects.filter(email=request.data['email']).delete()
      verif = Verification.objects.create()
      email = request.data['email']
      verif.email = email
      code = np.random.randint(100000, 999999)
      verif.code = code
      # send_code_email(email,code)
      verif.save()
      return Response(True, status=status.HTTP_200_OK)
    except:
      return Response(False, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def check_code(self, request):
    try:
      verif = Verification.objects.get(email=request.data['email'])
      code = request.data['code']
      Verification.objects.filter(email=request.data['email']).delete()
      if verif.code == code:
        return Response(200, status=status.HTTP_200_OK)
      else:
        return Response(404, status=status.HTTP_200_OK)
    except:
      return Response(502, status=status.HTTP_200_OK)

class RegistrationViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (AllowAny,)

  @action(methods=['POST'], detail=False)
  def get_username_id(self, request):
    username = User.objects.get(username=request.data['username'])
    return Response(username.id, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def data_save(self, request):
    username = User.objects.get(username=request.data['username'])
    data = UserProfile.objects.create()
    data.username = username
    data.birthday = request.data['birthday']
    data.sex = request.data['sex']
    data.level = 1
    data.like = 1
    data.sum = 0
    data.save()

    username_id = str(username.id)
    os.chdir(os.getcwd() + '\media')
    if request.data['sex'] == 'male':
      avatar = Image.open(r"man.png")
    if request.data['sex'] == 'female':
      avatar = Image.open(r"woman.png")
    os.chdir('profile')
    os.mkdir(username_id)
    os.chdir(username_id)
    name = '{}.png'.format(username_id)
    avatar.save(fp=name)
    os.chdir('../../..')
    return Response(200, status=status.HTTP_200_OK)


def send_link_reset_pas(email, token):
  addr_from = "freshpalcode@gmail.com"
  addr_to = email
  password = "freshpal2021"

  msg = MIMEMultipart()
  msg['From'] = addr_from
  msg['To'] = addr_to
  msg['Subject'] = 'Восстановление пароля'
  url = 'http://localhost:8080/#/restore_password/{}'.format(token)
  body = '''Для восстановления пароля перейдите по этой ссылке {}'''.format(url)
  msg.attach(MIMEText(body, 'plain'))

  server = smtplib.SMTP('smtp.gmail.com', 587)
  server.set_debuglevel(True)
  server.starttls()
  server.login(addr_from, password)
  server.send_message(msg)
  server.quit()

class RestorePasswordViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (AllowAny,)

  @action(methods=['POST'], detail=False)
  def get_link(self, request):
    if User.objects.filter(email=request.data['email']).exists():
      user = User.objects.get(email=request.data['email'])
      rand_token = uuid4()
      rand_token = str(rand_token)
      if RestorePassword.objects.filter(username=user).exists():
        RestorePassword.objects.filter(username=user).delete()
      reset_pas = RestorePassword.objects.create()
      reset_pas.username = user
      reset_pas.token = rand_token
      reset_pas.save()
      #send_link_reset_pas(request.data['email'], rand_token)
      return Response(status=status.HTTP_200_OK)
    else:
      return Response(status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def check_access(self, request):
    if(RestorePassword.objects.filter(token=request.data['token']).exists()):
      return Response(True, status=status.HTTP_200_OK)
    else:
      return Response(False, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def restore_pas(self, request):
    if (RestorePassword.objects.filter(token=request.data['token']).exists()):
      username = RestorePassword.objects.get(token=request.data['token'])
      user = User.objects.get(username=username.username)
      user.set_password(request.data['password'])
      user.save()
      RestorePassword.objects.filter(username=user).delete()
    return Response(request.data, status=status.HTTP_200_OK)








