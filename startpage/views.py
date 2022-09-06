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
import smtplib, ssl
import jwt
import os
from PIL import Image

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (AllowAny,)

  @action(methods=['POST'], detail=False)
  def count(self, request):
    res = User.objects.filter().count()
    return Response(res, status=status.HTTP_200_OK)


def send_code_email(email, code):
  sender = 'verification@freshpal.me'
  receiver = email

  message = MIMEMultipart("alternative")
  message["Subject"] = "Верификация нового пользователя"
  message["From"] = sender
  message["To"] = receiver

  # Create the plain-text and HTML version of your message
  text = """\
  Привет друг!
  Это твой код.
  {}
  С уважением,
  CEO FreshPal
  Черненко Сергей
  Мой личный телеграм
  Телеграм канал""".format(code)
  html = """
  <html>
    <body>    
      <div style="min-height: 45vh;">
          <div style="padding: 20px 0px 0px 10px;"><span style="#0c0c0c; font-size: 14pt; font-family: 'Open Sans', sans-serif;">Привет друг!</span></div>
          <div style="margin: 10px 0px 0px 10px;"><span style="#0c0c0c; font-size: 14pt; font-family: 'Open Sans', sans-serif;">Это твой код.</span></div>
          <div style="margin: 20px 0px 0px 10px;"><span style="color: #2dba2d; font-size: 14pt; font-family: 'Open Sans', sans-serif;">{}</span></div>
          <div style="margin: 30px 0px 0px 10px;"><span style="#0c0c0c; font-size: 12pt; font-family: 'Open Sans', sans-serif;">С уважением,</span></div>
          <div style="margin: 5px 0px 0px 10px;"><span style="#0c0c0c; font-size: 12pt; font-family: 'Open Sans', sans-serif;">CEO FreshPal</span></div>
          <div style="margin: 5px 0px 0px 10px;"><span style="#0c0c0c; font-size: 12pt; font-family: 'Open Sans', sans-serif;">Черненко Сергей</span></div>
          <div style="margin: 5px 0px 0px 10px;"><span style="font-size: 12pt; font-family: 'Open Sans', sans-serif;"><a style="color: #36d436;" href="https://t.me/nexusst">Мой личный телеграм</a></span></div>
          <div style="margin: 5px 0px 0px 10px;"><span style="font-size: 12pt; font-family: 'Open Sans', sans-serif;"><a style="color: #36d436;" href="https://t.me/freshpal">Телеграм канал</a></span></div>
      </div>
    </body>
  </html>
  """.format(code)

  # Turn these into plain/html MIMEText objects
  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")

  # Add HTML/plain-text parts to MIMEMultipart message
  # The email client will try to render the last part first
  message.attach(part1)
  message.attach(part2)

  context = ssl._create_unverified_context()
  with smtplib.SMTP_SSL("185.143.45.72", 465, context=context) as server:
    server.login(sender, 'VerificationFreshpal1298')
    server.sendmail(sender, receiver, message.as_string())

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
      send_code_email(email,code)
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
    media_path = os.getcwd() + '/media/'
    if request.data['sex'] == 'male':
      avatar = Image.open(media_path+"man.png")
    if request.data['sex'] == 'female':
      avatar = Image.open(media_path+"woman.png")
    os.mkdir(os.getcwd() + '/media/profile/' + username_id)
    avatar_path = os.getcwd() + '/media/profile/' + username_id + '/'
    name = '{}.png'.format(username_id)
    avatar.save(fp=avatar_path+name)
    return Response(200, status=status.HTTP_200_OK)


def send_link_reset_pas(email, token):
  sender = 'verification@freshpal.me'
  receiver = email

  message = MIMEMultipart("alternative")
  message["Subject"] = "Восстановление пароля"
  message["From"] = sender
  message["To"] = receiver

  # Create the plain-text and HTML version of your message
  text = """\
  Привет друг!
  Для восстановление пароля, перейди по этой ссылке.

  С уважением,
  CEO FreshPal
  Вам сюда!
  Черненко Сергей
  Мой личный телеграм
  Телеграм канал"""
  html = """
  <html>
    <body>    
      <div style="min-height: 45vh;">
          <div style="padding: 20px 0px 0px 10px;"><span style="#0c0c0c; font-size: 14pt; font-family: 'Open Sans', sans-serif;">Привет друг!</span></div>
          <div style="margin: 10px 0px 0px 10px;"><span style="#0c0c0c; font-size: 14pt; font-family: 'Open Sans', sans-serif;">Для восстановление пароля, перейди по этой ссылке.</span></div>
          <div style="margin: 5px 0px 0px 10px;"><span style="font-size: 14pt; font-family: 'Open Sans', sans-serif;"><a style="color: #36d436;" href="https://freshpal.me/restore_password/{}">Вам сюда!</a></span></div>
          <div style="margin: 30px 0px 0px 10px;"><span style="#0c0c0c; font-size: 12pt; font-family: 'Open Sans', sans-serif;">С уважением,</span></div>
          <div style="margin: 5px 0px 0px 10px;"><span style="#0c0c0c; font-size: 12pt; font-family: 'Open Sans', sans-serif;">CEO FreshPal</span></div>
          <div style="margin: 5px 0px 0px 10px;"><span style="#0c0c0c; font-size: 12pt; font-family: 'Open Sans', sans-serif;">Черненко Сергей</span></div>
          <div style="margin: 5px 0px 0px 10px;"><span style="font-size: 12pt; font-family: 'Open Sans', sans-serif;"><a style="color: #36d436;" href="https://t.me/nexusst">Мой личный телеграм</a></span></div>
          <div style="margin: 5px 0px 0px 10px;"><span style="font-size: 12pt; font-family: 'Open Sans', sans-serif;"><a style="color: #36d436;" href="https://t.me/freshpal">Телеграм канал</a></span></div>
      </div>
    </body>
  </html>
  """.format(token)

  # Turn these into plain/html MIMEText objects
  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")

  # Add HTML/plain-text parts to MIMEMultipart message
  # The email client will try to render the last part first
  message.attach(part1)
  message.attach(part2)

  context = ssl._create_unverified_context()
  with smtplib.SMTP_SSL("185.143.45.72", 465, context=context) as server:
    server.login(sender, 'VerificationFreshpal1298')
    server.sendmail(sender, receiver, message.as_string())

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
      send_link_reset_pas(request.data['email'], rand_token)
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








