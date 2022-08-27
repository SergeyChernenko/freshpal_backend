from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import action

from django.core import serializers
from django.contrib.auth.models import User
from startpage.models import Verification
from startpage.serializers import UserSerializer
from mainpage.models import UserProfile, Sub, Publ, PublRating, PublRatingUser, Rating, UserProfileStar
from home.models import Hashtag, Mention
from mainpage.serializers import UserProfileSerializer, SubSerializer, PublSerializer
from django.db.models import Q, Count
from django.contrib.auth.hashers import check_password


from mainpage.helpers import like_user, dislike_user, like_publ, dislike_publ, add_cost, check_text_censor, clean_text, detector_nude


import re
import cv2
from binascii import a2b_base64
import base64
import os
from PIL import Image
import json
from datetime import datetime
import numpy as np
from django.utils import timezone
import pytz


class AvatarViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (IsAuthenticated,)

  @action(methods=['POST'], detail=False)
  def set(self, request, *args, **kwargs):
    dataurl = request.data['avatar']
    username = str(request.user.id)
    imgstr = re.search(r'base64,(.*)', dataurl).group(1)
    binary_data = a2b_base64(imgstr)
    os.chdir(os.getcwd() + '\media')
    os.chdir(os.getcwd() + '\profile')
    os.chdir(username)
    path = '{}.png'.format(username)
    Out = open(path, 'wb')
    Out.write(binary_data)
    Out.close()
    image = Image.open(path)
    image = image.resize((150, 150), Image.ANTIALIAS)
    os.remove(path)
    image.save(fp=path)
    os.chdir('../../..')
    return Response(path, status=status.HTTP_200_OK)


class SubscribeViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (IsAuthenticated,)

  @action(methods=['POST'], detail=False)
  def list_followers(self, request, *args, **kwargs):  # список подписчиков
    username = User.objects.get(username=request.data['username'])
    list_id = Sub.objects.values_list('subscriber__id',flat=True).filter(username=username)
    check_sub = Sub.objects.values_list('username',flat=True).filter(username__in=list_id,subscriber=username)
    data = UserProfile.objects.values('username__id','username__username','level','positive').filter(username__id__in=list_id)
    for i in range(len(data)):
      for id in check_sub:
        if id == data[i]['username__id']:
          data[i]['sub'] = True
    return Response(data, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def list_following(self, request, *args, **kwargs):  # список подписок
    username = User.objects.get(username=request.data['username'])
    list_id = Sub.objects.values_list('username__id',flat=True).filter(subscriber=username)
    data = UserProfile.objects.values('username__id','username__username','level','positive').filter(username__id__in=list_id)
    return Response(data, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def plus(self, request, *args, **kwargs): # подписка
    sub_plus = Sub.objects.create()
    sub_plus.username = User.objects.get(username=request.data['username'])
    sub_plus.subscriber = User.objects.get(username=request.user.username)
    sub_plus.save()
    return Response(True, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def minus(self, request, *args, **kwargs): # отписка
    username = User.objects.get(username=request.data['username'])
    subscriber = User.objects.get(username=request.user.username)
    Sub.objects.filter(username=username, subscriber=subscriber).delete()
    return Response(False, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def sum(self, request, *args, **kwargs): # кол-во подписчиков и подписок у пользователя
    username = User.objects.get(username=request.data['username'])
    sum_subscribe = Sub.objects.filter(username=username).count()
    sum_subscriptions = Sub.objects.filter(subscriber=username).count()
    sum_publ = Publ.objects.filter(username=username, parent_id=0, remote=False).count()
    data={}
    data['subscribe'] = sum_subscribe
    data['subscriptions'] = sum_subscriptions
    data['publications'] = sum_publ
    return Response(data, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def check_sub(self, request, *args, **kwargs): # проверка подписки
    username = User.objects.get(username=request.data['username'])
    subscriber = User.objects.get(username=request.user.username)
    if Sub.objects.filter(username=username, subscriber=subscriber).exists():
      return Response(True, status=status.HTTP_200_OK)
    else:
      return Response(False, status=status.HTTP_200_OK)

class UserProfileViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (IsAuthenticated,)

  @action(methods=['POST'], detail=False)
  def last_visit(self, request, *args, **kwargs):
    username = request.user.username
    visit = UserProfile.objects.get(username__username=username)
    last = visit.now_visit
    visit.now_visit = timezone.now()
    visit.last_visit = last
    visit.save()
    return Response(status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def get_username(self, request, *args, **kwargs):
    data = {'username': request.user.username, 'username_id': request.user.id}
    return Response(data, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def check(self, request, *args, **kwargs):  # существует ли пользователь
    data = {}
    if User.objects.filter(username=request.data['username']).exists():
      username = User.objects.get(username=request.data['username'])
      username_token = request.user.username
      user_data = UserProfile.objects.values('level', 'positive', 'description','success').filter(username=username)[0]
      if UserProfileStar.objects.filter(username__username=request.data['username']).exists():
        star = UserProfileStar.objects.values_list('star',flat=True).filter(username__username=request.data['username'])[0]
      else:
        star = 0
      if username_token == str(username):
        access = True
      else:
        access = False
      data['check'] = True
      data['id'] = username.id
      data['access'] = access
      data['level'] = user_data['level']
      data['positive'] = user_data['positive']
      data['description'] = user_data['description']
      data['success'] = user_data['success']
      data['star'] = star
      return Response(data, status=status.HTTP_200_OK)
    else:
      data['check'] = False
      return Response(data, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def description_save(self, request, *args, **kwargs):
    description = request.data['description']
    user_data = UserProfile.objects.get(username__username=request.user.username)
    user_data.description = description.strip()
    user_data.save()
    return Response(True,status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def get_data_settings(self, request, *args, **kwargs):
    username = request.user.username
    user_data = UserProfile.objects.values('description','censor','nude').filter(username__username=username)
    return Response(user_data, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def edit_censor(self, request, *args, **kwargs):
    filter = request.data['filter']
    user_data = UserProfile.objects.get(username__username=request.user.username)
    if filter:
      if len(filter) == 1:
        if filter[0] == 'censor':
          user_data.censor = True
          user_data.nude = False
        if filter[0] == 'nude':
          user_data.nude = True
          user_data.censor = False
      if len(filter) == 2:
        for fl in filter:
          if fl == 'censor':
            user_data.censor = True
          if fl == 'nude':
            user_data.nude = True
    else:
      user_data.censor = False
      user_data.nude = False
    user_data.save()
    return Response(status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def check_pass(self, request, *args, **kwargs):
    username = User.objects.get(username=request.user.username)
    password = request.data['password']
    res = check_password(password,username.password)
    return Response(res,status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def change_pass(self, request, *args, **kwargs):
    username = User.objects.get(username=request.user.username)
    username.set_password(request.data['password'])
    username.save()
    return Response(True, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def search_username(self, request, *args, **kwargs):
    username = request.data['username']
    if username:
      result = UserProfile.objects.values('username', 'username__username','level', 'positive').filter(username__username__startswith=username)
      return Response(result, status=status.HTTP_200_OK)
    else:
      return Response(status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def search_hashtag(self, request, *args, **kwargs):
    hashtag = request.data['hashtag'][1:]
    if hashtag:
      result = Hashtag.objects.values('hashtag').annotate(count=Count('hashtag')).filter(hashtag__startswith=hashtag).order_by("-count")
      return Response(result, status=status.HTTP_200_OK)
    else:
      return Response(status=status.HTTP_200_OK)


def save_image(publ_id, images, username_id, object):
  path_start = os.getcwd()
  if len(path_start.split("\\")) > 4:
    os.chdir('../../..')
  os.chdir(os.getcwd() + '\media')
  os.chdir(os.getcwd() + '\profile')
  os.chdir(username_id)
  for i in range(len(images)):
    format = images[i][:17].split('/')[1].split(';')[0]
    if format == 'png' or format == 'jpeg':
      encoded_data = images[i].split(',')[1]
      decoded_data = base64.b64decode(encoded_data)
      np_data = np.frombuffer(decoded_data, np.uint8)
      image = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
      height = image.shape[0]
      width = image.shape[1]
      if height > 1920:
        height = int(image.shape[0] / (image.shape[0] / 1920))
        width = int(image.shape[1] / (image.shape[0] / 1920))
      if width > 1920:
        height = int(image.shape[0] // (image.shape[1] / 1920))
        width = int(image.shape[1] / (image.shape[1] / 1920))
      resized_image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
      name = '{}_{}.jpeg'.format(publ_id, i)
      cv2.imwrite(name, resized_image)
      if detector_nude(name) == True:
        object.nude = True
      else:
        object.nude = False
    if format == 'gif':
      imgstr = re.search(r'base64,(.*)', images[i]).group(1)
      binary_data = a2b_base64(imgstr)
      name = '{}_{}.gif'.format(publ_id, i)
      Out = open(name, 'wb')
      Out.write(binary_data)
      Out.close()
  os.chdir('../../..')

class PublViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (IsAuthenticated,)

  @action(methods=['POST'], detail=False)
  def save_publ(self, request, *args, **kwargs): # сохранить публикацию на стене
    username = User.objects.get(username=request.user.username)
    censor_tag = False
    censor_text = False
    mess = Publ.objects.create()
    hashtag = set([tag.strip("#").lower() for tag in request.data['message'].split() if tag.startswith("#")])
    mention = set([tag.strip("@").lower() for tag in request.data['message'].split() if tag.startswith("@")])
    ment_user = UserProfile.objects.values('username').filter(username__username__in=mention)
    if ment_user:
      for ment in ment_user:
        ment_save = Mention.objects.create()
        ment_save.username = User.objects.get(id=ment['username'])
        ment_save.publication = mess
        ment_save.save()
    if hashtag:
      for hash in hashtag:
        censor_tag = check_text_censor(hash)
        hashtag_save = Hashtag.objects.create()
        hashtag_save.publication = mess
        hashtag_save.hashtag = hash
        hashtag_save.datetime = timezone.now()
        if censor_tag == True:
          hashtag_save.censor = True
        hashtag_save.save()
    message = request.data['message'].strip()
    if message:
      message_clean = clean_text(message)
      for let in message_clean:
        censor_text = check_text_censor(let)
        if censor_text == True:
          break
    mess.username = username
    if request.data['images']:
      save_image(mess.id, request.data['images'], str(request.user.id),mess)
    mess.message = message
    mess.datetime = timezone.now()
    mess.parent_id = 0
    if censor_tag == True or censor_text == True:
      mess.censor = True
    mess.save()
    publ_rating = PublRating.objects.create()
    publ_rating.publication = mess
    publ_rating.level = 1
    publ_rating.sum = 0
    publ_rating.sum_like = 0
    publ_rating.sum_dislike = 0
    publ_rating.save()
    return Response(1, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def get_publ(self, request, *args, **kwargs):  # получить все публикации на стене
    username = User.objects.get(username=request.data['username'])
    username_token = User.objects.get(username=request.user.username)
    datetime_request = request.data['datetime_request']
    if Publ.objects.filter(username=username,parent_id=0,remote=False).exists():
      if not datetime_request:
        datetime_start = Publ.objects.values_list('datetime', flat=True).filter(username=username,parent_id=0,remote=False).order_by('-datetime')[0]
        data = list(Publ.objects.values('id', 'message', 'datetime', 'edit')
                    .filter(username=username,datetime__lte=datetime_start,parent_id=0,remote=False).order_by('-datetime')[:10])

      if datetime_request:
        datetime_start = datetime_request
        data = list(Publ.objects.values('id', 'message', 'datetime', 'edit')
                    .filter(username=username,datetime__lt=datetime_start,parent_id=0,remote=False).order_by('-datetime')[:10])
      publ_list = [publ['id'] for publ in data]
      comment_count = Publ.objects.values("parent_id").annotate(count=Count('parent_id')).filter(parent_id__in=publ_list,remote=False).order_by("-count")
      publ_rating = PublRating.objects.values('level', 'positive', 'sum_like', 'sum_dislike').filter(publication__in=publ_list).order_by('-publication')
      check_like = PublRatingUser.objects.values('publication', 'positive').filter(username=username_token).filter(publication__in=publ_list)
      for i in range(len(data)):
        data[i]['level'] = publ_rating[i]['level']
        data[i]['positive'] = publ_rating[i]['positive']
        data[i]['sum_like'] = publ_rating[i]['sum_like']
        data[i]['sum_dislike'] = publ_rating[i]['sum_dislike']
        for j in range(len(check_like)):
          if check_like[j]['publication'] == data[i]['id']:
            if check_like[j]['positive'] == True:
              data[i]['check_like'] = True
            if check_like[j]['positive'] == False:
              data[i]['check_dislike'] = True
        for j in range(len(comment_count)):
          if comment_count[j]['parent_id'] == data[i]['id']:
            data[i]['comments'] = comment_count[j]['count']
        data[i]['images'] = []
        content = os.listdir(os.getcwd() + '\\media\\profile\\' + str(username.id))
        content = [img.split('_') for img in content if 'jpeg' in img or 'gif' in img]
        for j in range(len(content)):
          if data[i]['id'] == int(content[j][0]):
            full_image = 'http://127.0.0.1:8000/media/profile/{}/{}'.format(str(username.id),
                                                                            (content[j][0] + '_' + content[j][1]))
            data[i]['images'].append(full_image)
      return Response(data, status=status.HTTP_200_OK)
    else:
      return Response(False, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def get_publ_by_id(self, request, *args, **kwargs): # получить одну публикацию по id
    id_url = request.data['id_url']
    username_token = request.user.username
    username = User.objects.get(username=username_token)
    if Publ.objects.filter(id=id_url).exists():
      data = Publ.objects.get(id=id_url)
      if username_token == str(data.username.username):
        access = True
      else:
        access = False
      publ_rating = PublRating.objects.values('level', 'positive', 'sum_like', 'sum_dislike').filter(publication=id_url)[0]
      check_like = PublRatingUser.objects.values('positive').filter(username=username).filter(publication=id_url)
      r_user = UserProfile.objects.values('level', 'positive').filter(username=data.username.id)[0]
      comment_count = Publ.objects.values("parent_id").annotate(count=Count('parent_id')).filter(parent_id=id_url, remote=False).order_by("-count")
      data_publ = {}
      data_publ['username_id'] = str(data.username.id)
      data_publ['username'] = str(data.username.username)
      data_publ['message'] = data.message
      data_publ['datetime'] = str(data.datetime)
      data_publ['edit'] = data.edit
      data_publ['remote'] = data.remote
      data_publ['parent_id'] = data.parent_id
      data_publ['access'] = access
      data_publ['level_user'] = r_user['level']
      data_publ['positive_user'] = r_user['positive']
      if comment_count:
        data_publ['comments'] = comment_count[0]['count']
      data_publ['images'] = []
      if check_like:
        if check_like[0]['positive'] == True:
          data_publ['check_like'] = True
        if check_like[0]['positive'] == False:
          data_publ['check_dislike'] = True
      data_publ['level'] = publ_rating['level']
      data_publ['positive'] = publ_rating['positive']
      data_publ['sum_like'] = publ_rating['sum_like']
      data_publ['sum_dislike'] = publ_rating['sum_dislike']
      content = os.listdir(os.getcwd() + '\\media\\profile\\' + str(data.username.id))
      content = [img.split('_') for img in content if 'jpeg' in img or 'gif' in img]
      for i in range(len(content)):
        if content[i][0] == id_url:
          full_image = 'http://127.0.0.1:8000/media/profile/{}/{}'.format(str(data.username.id),(content[i][0] + '_' + content[i][1]))
          data_publ['images'].append(full_image)
      json_dump = json.dumps(data_publ)
      json_object = json.loads(json_dump)
      return Response(json_object, status=status.HTTP_200_OK)
    else:
      return Response(False, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def save_edit_publ(self, request, *args, **kwargs): # редактировать публикацию
    id_url = request.data['id_url']
    data = Publ.objects.get(id=id_url)
    censor_tag = False
    censor_text = False
    message = request.data['message'].strip()
    if message:
      message_clean = clean_text(message)
      for let in message_clean:
        censor_text = check_text_censor(let)
        if censor_text == True:
          break
    hashtag = set([tag.strip("#").lower() for tag in message.split() if tag.startswith("#")])
    mention = set([tag.strip("@").lower() for tag in message.split() if tag.startswith("@")])
    ment_user = UserProfile.objects.values('username').filter(username__username__in=mention)
    if Mention.objects.filter(publication=data).exists():
      Mention.objects.filter(publication=data).delete()
    if ment_user:
      for ment in ment_user:
        ment_save = Mention.objects.create()
        ment_save.username = User.objects.get(id=ment['username'])
        ment_save.publication = data
        if request.data['comment']:
          ment_save.comment = True
        ment_save.save()
    if Hashtag.objects.filter(publication=data).exists():
      Hashtag.objects.filter(publication=data).delete()
    if hashtag:
      for hash in hashtag:
        censor_tag = check_text_censor(hash)
        hashtag_save = Hashtag.objects.create()
        hashtag_save.publication = data
        hashtag_save.hashtag = hash
        hashtag_save.datetime = timezone.now()
        if request.data['comment']:
          hashtag_save.comment = True
        if censor_tag == True:
          hashtag_save.censor = True
        hashtag_save.save()
    data.message = message
    data.edit = True
    if censor_tag == True or censor_text == True:
      data.censor = True
    else:
      data.censor = False
    content = os.listdir(os.getcwd() + '\\media\\profile\\' + str(request.user.id))
    images = [img for img in content if id_url in img.split('_')[0]]
    if images:
      os.chdir(os.getcwd() + '\media')
      os.chdir(os.getcwd() + '\profile')
      os.chdir(str(request.user.id))
      for img in images:
        os.remove(img)
      os.chdir('../../..')
    if request.data['images']:
      save_image(id_url, request.data['images'], str(request.user.id),data)

    data.save()
    return Response(status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def delete_mess(self, request, *args, **kwargs):  # редактировать публикацию
    publ = Publ.objects.get(id=request.data['id_url'])
    publ.message = ''
    publ.remote = True
    publ.save()
    if Hashtag.objects.filter(publication=publ).exists():
      Hashtag.objects.filter(publication=publ).delete()
    publ_rating = PublRating.objects.get(publication=request.data['id_url'])
    if publ_rating.positive == False:
      like_user(publ.username, publ_rating.sum)
    if publ_rating.positive == True:
      dislike_user(publ.username, publ_rating.sum)
    publ_rating.level = 0
    publ_rating.sum = 0
    publ_rating.sum_like = 0
    publ_rating.sum_dislike = 0
    publ_rating.positive = True
    publ_rating.save()
    if PublRatingUser.objects.filter(publication=request.data['id_url']).exists():
      PublRatingUser.objects.filter(publication=request.data['id_url']).delete()
    content = os.listdir(os.getcwd() + '\\media\\profile\\' + str(request.user.id))
    images = [img for img in content if request.data['id_url'] in img.split('_')[0]]
    if images:
      os.chdir(os.getcwd() + '\media')
      os.chdir(os.getcwd() + '\profile')
      os.chdir(str(request.user.id))
      for img in images:
        os.remove(img)
      os.chdir('../../..')
    return Response(status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def save_comment(self, request, *args, **kwargs):  # редактировать публикацию
    username = User.objects.get(username=request.user.username)
    censor_tag = False
    censor_text = False
    mess = Publ.objects.create()
    hashtag = set([tag.strip("#").lower() for tag in request.data['comment'].split() if tag.startswith("#")])
    mention = set([tag.strip("@").lower() for tag in request.data['comment'].split() if tag.startswith("@")])
    ment_user = UserProfile.objects.values('username').filter(username__username__in=mention)
    if ment_user:
      for ment in ment_user:
        ment_save = Mention.objects.create()
        ment_save.username = User.objects.get(id=ment['username'])
        ment_save.publication = mess
        ment_save.comment = True
        ment_save.save()
    if hashtag:
      for hash in hashtag:
        censor_tag = check_text_censor(hash)
        hashtag_save = Hashtag.objects.create()
        hashtag_save.publication = mess
        hashtag_save.hashtag = hash
        hashtag_save.datetime = timezone.now()
        hashtag_save.comment = True
        if censor_tag == True:
          hashtag_save.censor = True
        hashtag_save.save()
    message = request.data['comment'].strip()
    if message:
      message_clean = clean_text(message)
      for let in message_clean:
        censor_text = check_text_censor(let)
        if censor_text == True:
          break
    if request.data['images']:
      save_image(mess.id, request.data['images'], str(request.user.id),mess)
    mess.username = username
    mess.message = message
    mess.datetime = timezone.now()
    mess.parent_id = request.data['parent_id']
    mess.publ_user = int(request.data['publ_user'])
    if censor_tag == True or censor_text == True:
      mess.censor = True
    mess.save()
    publ_rating = PublRating.objects.create()
    publ_rating.publication = mess
    publ_rating.level = 1
    publ_rating.sum = 0
    publ_rating.sum_like = 0
    publ_rating.sum_dislike = 0
    publ_rating.save()
    return Response(status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def get_comment(self, request, *args, **kwargs):  # редактировать публикацию
    parent_id = request.data['parent_id']
    datetime_request = request.data['datetime_request']
    type = request.data['type']
    username_token = User.objects.get(username=request.user.username)
    if Publ.objects.filter(parent_id=parent_id,remote=False).exists():
      if type == True:
        if not datetime_request:
          datetime_start = Publ.objects.values_list('datetime', flat=True).filter(parent_id=parent_id,remote=False).order_by('datetime')[0]
          data = list(Publ.objects.values('id', 'username', 'username__username', 'message', 'datetime', 'edit')
                      .filter(parent_id=parent_id,datetime__gte=datetime_start,remote=False).order_by('datetime')[:10])

        if datetime_request:
          datetime_start = datetime_request
          data = list(Publ.objects.values('id', 'username','username__username', 'message', 'datetime', 'edit')
                      .filter(parent_id=parent_id,datetime__gt=datetime_start,remote=False).order_by('datetime')[:10])
        publ_list = [publ['id'] for publ in data]
        publ_rating = PublRating.objects.values('publication','level', 'positive', 'sum_like', 'sum_dislike').filter(publication__in=publ_list).order_by('publication')
      if type == False:
        if not datetime_request:
          datetime_start = Publ.objects.values_list('datetime', flat=True).filter(parent_id=parent_id).order_by('-datetime')[0]
          data = list(Publ.objects.values('id', 'username', 'username__username', 'message', 'datetime', 'edit')
                      .filter(parent_id=parent_id, datetime__lte=datetime_start, remote=False).order_by('-datetime')[:10])

        if datetime_request:
          datetime_start = datetime_request
          data = list(Publ.objects.values('id', 'username', 'username__username', 'message', 'datetime', 'edit')
                      .filter(parent_id=parent_id, datetime__lt=datetime_start, remote=False).order_by('-datetime')[:10])
        publ_list = [publ['id'] for publ in data]
        publ_rating = PublRating.objects.values('publication', 'level', 'positive', 'sum_like', 'sum_dislike').filter(
          publication__in=publ_list).order_by('-publication')
      user_list = [publ['username'] for publ in data]
      check_like = PublRatingUser.objects.values('publication', 'positive').filter(username=username_token).filter(publication__in=publ_list)
      r_user = UserProfile.objects.values('username', 'level', 'positive').filter(username__in=user_list)
      comment_count = Publ.objects.values("parent_id").annotate(count=Count('parent_id')).filter(parent_id__in=publ_list, remote=False).order_by("-count")
      for i in range(len(data)):
        data[i]['level'] = publ_rating[i]['level']
        data[i]['positive'] = publ_rating[i]['positive']
        data[i]['sum_like'] = publ_rating[i]['sum_like']
        data[i]['sum_dislike'] = publ_rating[i]['sum_dislike']
        for j in range(len(r_user)):
          if data[i]['username'] == r_user[j]['username']:
            data[i]['level_user'] = r_user[j]['level']
            data[i]['positive_user'] = r_user[j]['positive']
        for j in range(len(check_like)):
          if check_like[j]['publication'] == data[i]['id']:
            if check_like[j]['positive'] == True:
              data[i]['check_like'] = True
            if check_like[j]['positive'] == False:
              data[i]['check_dislike'] = True
        for j in range(len(comment_count)):
          if comment_count[j]['parent_id'] == data[i]['id']:
            data[i]['comments'] = comment_count[j]['count']
        data[i]['images'] = []
        content = os.listdir(os.getcwd() + '\\media\\profile\\' + str(data[i]['username']))
        content = [img.split('_') for img in content if 'jpeg' in img or 'gif' in img]
        for j in range(len(content)):
          if data[i]['id'] == int(content[j][0]):
            full_image = 'http://127.0.0.1:8000/media/profile/{}/{}'.format(str(data[i]['username']),
                                                                            (content[j][0] + '_' + content[j][1]))
            data[i]['images'].append(full_image)
      return Response(data, status=status.HTTP_200_OK)
    else:
      return Response(False, status=status.HTTP_200_OK)



class RatingViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (IsAuthenticated,)

  @action(methods=['POST'], detail=False)
  def like(self, request, *args, **kwargs):
    id_publ = request.data['id']
    username = User.objects.get(username=request.user.username)
    like_cost = UserProfile.objects.values_list('like', flat=True).filter(username=username)[0]
    publ = Publ.objects.get(id=id_publ)
    if PublRatingUser.objects.filter(publication=publ).filter(username=username).filter(positive=True).exists():
      like_minus = list(PublRatingUser.objects.values_list('like', flat=True).filter(publication=publ).filter(username=username).filter(positive=True))[0]
      PublRatingUser.objects.filter(publication=publ).filter(username=username).filter(positive=True).delete()
      dislike_user(publ.username, like_minus)
      dislike_publ(id_publ, like_minus)
      amount_minus = PublRating.objects.get(publication=publ)
      amount_minus.sum_like -= 1
      amount_minus.sum_dislike -= 1
      ret_cost = amount_minus.level
      positive_p = amount_minus.positive
      amount_minus.save()
      r_user = UserProfile.objects.values('username__username', 'level', 'positive').filter(username=publ.username)[0]
      d_return = {}
      d_return['like'] = False
      d_return['level_p'] = ret_cost
      d_return['positive_p'] = positive_p
      d_return['level_user'] = r_user['level']
      d_return['positive_user'] = r_user['positive']
      d_return['username'] = r_user['username__username']
      return Response(d_return, status=status.HTTP_200_OK)
    if PublRatingUser.objects.filter(publication=publ).filter(username=username).filter(positive=False).exists():
      dislike_minus = list(PublRatingUser.objects.values_list('like', flat=True).filter(publication=publ).filter(username=username).filter(positive=False))[0]
      PublRatingUser.objects.filter(publication=publ).filter(username=username).filter(positive=False).delete()
      like_user(publ.username, dislike_minus)
      like_publ(id_publ, dislike_minus)
      amount_minus = PublRating.objects.get(publication=publ)
      amount_minus.sum_like -= 1
      amount_minus.sum_dislike -= 1
      amount_minus.save()
      like_user(publ.username, like_cost)
      like_publ(id_publ, like_cost)
      add_cost(id_publ, publ.username, username, like_cost, True)
      amount_minus = PublRating.objects.get(publication=publ)
      ret_cost = amount_minus.level
      positive_p = amount_minus.positive
      r_user = UserProfile.objects.values('username__username', 'level', 'positive').filter(username=publ.username)[0]
      d_return = {}
      d_return['like'] = True
      d_return['dislike'] = False
      d_return['level_p'] = ret_cost
      d_return['positive_p'] = positive_p
      d_return['level_user'] = r_user['level']
      d_return['positive_user'] = r_user['positive']
      d_return['username'] = r_user['username__username']
      return Response(d_return, status=status.HTTP_200_OK)
    else:
      like_user(publ.username, like_cost)
      like_publ(id_publ, like_cost)
      add_cost(id_publ, publ.username, username, like_cost, True)
      amount_minus = PublRating.objects.get(publication=publ)
      ret_cost = amount_minus.level
      positive_p = amount_minus.positive
      r_user = UserProfile.objects.values('username__username', 'level', 'positive').filter(username=publ.username)[0]
      d_return = {}
      d_return['like'] = True
      d_return['level_p'] = ret_cost
      d_return['positive_p'] = positive_p
      d_return['level_user'] = r_user['level']
      d_return['positive_user'] = r_user['positive']
      d_return['username'] = r_user['username__username']
      return Response(d_return, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def dislike(self, request, *args, **kwargs):
    id_publ = request.data['id']
    username = User.objects.get(username=request.user.username)
    like_cost = UserProfile.objects.values_list('like', flat=True).filter(username=username)[0]
    publ = Publ.objects.get(id=id_publ)
    if PublRatingUser.objects.filter(publication=publ).filter(username=username).filter(positive=False).exists():
      dislike_minus = list(PublRatingUser.objects.values_list('like', flat=True).filter(publication=publ).filter(username=username).filter(positive=False))[0]
      PublRatingUser.objects.filter(publication=publ).filter(username=username).filter(positive=False).delete()
      like_user(publ.username, dislike_minus)
      like_publ(id_publ, dislike_minus)
      amount_minus = PublRating.objects.get(publication=publ)
      amount_minus.sum_like -= 1
      amount_minus.sum_dislike -= 1
      ret_cost = amount_minus.level
      positive_p = amount_minus.positive
      amount_minus.save()
      r_user = UserProfile.objects.values('username__username', 'level', 'positive').filter(username=publ.username)[0]
      d_return = {}
      d_return['dislike'] = False
      d_return['level_p'] = ret_cost
      d_return['positive_p'] = positive_p
      d_return['level_user'] = r_user['level']
      d_return['positive_user'] = r_user['positive']
      d_return['username'] = r_user['username__username']
      return Response(d_return, status=status.HTTP_200_OK)
    if PublRatingUser.objects.filter(publication=publ).filter(username=username).filter(positive=True).exists():
      like_minus = list(PublRatingUser.objects.values_list('like', flat=True).filter(publication=publ).filter(username=username).filter(positive=True))[0]
      PublRatingUser.objects.filter(publication=publ).filter(username=username).filter(positive=True).delete()
      dislike_user(publ.username, like_minus)
      dislike_publ(id_publ, like_minus)
      amount_minus = PublRating.objects.get(publication=publ)
      amount_minus.sum_like -= 1
      amount_minus.sum_dislike -= 1
      amount_minus.save()
      dislike_user(publ.username, like_cost)
      dislike_publ(id_publ, like_cost)
      add_cost(id_publ, publ.username, username, like_cost, False)
      amount_minus = PublRating.objects.get(publication=publ)
      ret_cost = amount_minus.level
      positive_p = amount_minus.positive
      r_user = UserProfile.objects.values('username__username', 'level', 'positive').filter(username=publ.username)[0]
      d_return = {}
      d_return['dislike'] = True
      d_return['like'] = False
      d_return['level_p'] = ret_cost
      d_return['positive_p'] = positive_p
      d_return['level_user'] = r_user['level']
      d_return['positive_user'] = r_user['positive']
      d_return['username'] = r_user['username__username']
      return Response(d_return, status=status.HTTP_200_OK)
    else:
      dislike_user(publ.username, like_cost)
      dislike_publ(id_publ, like_cost)
      add_cost(id_publ, publ.username, username, like_cost, False)
      amount_minus = PublRating.objects.get(publication=publ)
      ret_cost = amount_minus.level
      positive_p = amount_minus.positive
      r_user = UserProfile.objects.values('username__username', 'level', 'positive').filter(username=publ.username)[0]
      d_return = {}
      d_return['dislike'] = True
      d_return['level_p'] = ret_cost
      d_return['positive_p'] = positive_p
      d_return['level_user'] = r_user['level']
      d_return['positive_user'] = r_user['positive']
      d_return['username'] = r_user['username__username']
    return Response(d_return, status=status.HTTP_200_OK)