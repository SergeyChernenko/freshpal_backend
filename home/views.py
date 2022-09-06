from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

from django.contrib.auth.models import User
from startpage.serializers import UserSerializer
from startpage.models import ServerInfo
from mainpage.models import UserProfile, Sub, Publ, PublRating, PublRatingUser, UserProfileStar
from home.models import Hashtag, Donat, Mention
from django.db.models import Q, Count, Sum, F


import os
from datetime import datetime, timedelta
from django.utils import timezone
import pytz

def filter_recommended(datetime_request,username,subs,censor,nude):
  if censor == True and nude == True:
    if not datetime_request:
      datetime_start = Publ.objects.values_list('datetime', flat=True).filter(~Q(username=username), parent_id=0, remote=False).order_by('-datetime')[0]
      data = list(Publ.objects.values('id', 'username', 'username__username', 'message', 'datetime', 'edit')
                  .filter(~Q(username=username), ~Q(username__in=subs), datetime__lte=datetime_start, parent_id=0,
                          remote=False).order_by('-datetime')[:10])
    if datetime_request:
      datetime_start = datetime_request
      data = list(Publ.objects.values('id', 'username', 'username__username', 'message', 'datetime', 'edit')
                  .filter(~Q(username=username), ~Q(username__in=subs), datetime__lt=datetime_start, parent_id=0,
                          remote=False).order_by('-datetime')[:10])

  if censor == True and nude == False:
    if not datetime_request:
      datetime_start = Publ.objects.values_list('datetime', flat=True).filter(~Q(username=username), parent_id=0, remote=False, nude=False).order_by('-datetime')[0]
      data = list(Publ.objects.values('id', 'username', 'username__username', 'message', 'datetime', 'edit')
                  .filter(~Q(username=username), ~Q(username__in=subs), datetime__lte=datetime_start, parent_id=0,
                          remote=False, nude=False).order_by('-datetime')[:10])
    if datetime_request:
      datetime_start = datetime_request
      data = list(Publ.objects.values('id', 'username', 'username__username', 'message', 'datetime', 'edit')
                  .filter(~Q(username=username), ~Q(username__in=subs), datetime__lt=datetime_start, parent_id=0,
                          remote=False, nude=False).order_by('-datetime')[:10])

  if censor == False and nude == True:
    if not datetime_request:
      datetime_start = Publ.objects.values_list('datetime', flat=True).filter(~Q(username=username), parent_id=0, remote=False, censor=False).order_by('-datetime')[0]
      data = list(Publ.objects.values('id', 'username', 'username__username', 'message', 'datetime', 'edit')
                  .filter(~Q(username=username), ~Q(username__in=subs), datetime__lte=datetime_start, parent_id=0,
                          remote=False, censor=False).order_by('-datetime')[:10])
    if datetime_request:
      datetime_start = datetime_request
      data = list(Publ.objects.values('id', 'username', 'username__username', 'message', 'datetime', 'edit')
                  .filter(~Q(username=username), ~Q(username__in=subs), datetime__lt=datetime_start, parent_id=0,
                          remote=False, censor=False).order_by('-datetime')[:10])

  if censor == False and nude == False:
    if not datetime_request:
      datetime_start = Publ.objects.values_list('datetime', flat=True).filter(~Q(username=username), parent_id=0, remote=False, censor=False, nude=False).order_by('-datetime')[0]
      data = list(Publ.objects.values('id', 'username', 'username__username', 'message', 'datetime', 'edit')
                  .filter(~Q(username=username), ~Q(username__in=subs), datetime__lte=datetime_start, parent_id=0,
                          remote=False, censor=False, nude=False).order_by('-datetime')[:10])
    if datetime_request:
      datetime_start = datetime_request
      data = list(Publ.objects.values('id', 'username', 'username__username', 'message', 'datetime', 'edit')
                  .filter(~Q(username=username), ~Q(username__in=subs), datetime__lt=datetime_start, parent_id=0,
                          remote=False, censor=False, nude=False).order_by('-datetime')[:10])

  return data

class HomeViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (IsAuthenticated,)

  @action(methods=['POST'], detail=False)
  def get_subs(self, request, *args, **kwargs):
    username = User.objects.get(username=request.user.username)
    subs = Sub.objects.values_list('username', flat=True).filter(subscriber=username)
    datetime_request = request.data['datetime_request']
    server_url = ServerInfo.objects.get(id=1).url
    if Publ.objects.filter(username__in=subs,parent_id=0,remote=False).exists():
      if not datetime_request:
        datetime_start = Publ.objects.values_list('datetime', flat=True).filter(username__in=subs,parent_id=0,remote=False).order_by('-datetime')[0]
        data = list(Publ.objects.values('id', 'username', 'username__username', 'message', 'datetime', 'edit')
                      .filter(username__in=subs,datetime__lte=datetime_start,parent_id=0,remote=False).order_by('-datetime')[:10])


      if datetime_request:
        datetime_start = datetime_request
        data = list(Publ.objects.values('id', 'username', 'username__username', 'message', 'datetime', 'edit')
                    .filter(username__in=subs,datetime__lt=datetime_start,parent_id=0,remote=False).order_by('-datetime')[:10])

      publ_list = [publ['id'] for publ in data]
      user_list = [publ['username'] for publ in data]
      comment_count = Publ.objects.values("parent_id").annotate(count=Count('parent_id')).filter(parent_id__in=publ_list, remote=False).order_by("-count")
      publ_rating = PublRating.objects.values('level', 'positive', 'sum_like', 'sum_dislike').filter(publication__in=publ_list).order_by('-publication')
      check_like = PublRatingUser.objects.values('publication', 'positive').filter(username=username,publication__in=publ_list)
      r_user = UserProfile.objects.values('username', 'level', 'positive').filter(username__in=user_list)
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
        content = os.listdir(os.getcwd() + '/media/profile/' + str(data[i]['username']))
        content = [img.split('_') for img in content if 'jpeg' in img or 'gif' in img]
        for j in range(len(content)):
          if data[i]['id'] == int(content[j][0]):
            full_image = '{}/media/profile/{}/{}'.format(server_url,str(data[i]['username']),(content[j][0] + '_' + content[j][1]))
            data[i]['images'].append(full_image)
      return Response(data, status=status.HTTP_200_OK)
    else:
      return Response(False, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def get_recommended(self, request, *args, **kwargs):
    username = User.objects.get(username=request.user.username)
    subs = Sub.objects.values_list('username', flat=True).filter(subscriber=username)
    datetime_request = request.data['datetime_request']
    filter = UserProfile.objects.values('censor','nude').filter(username__username=request.user.username)[0]
    server_url = ServerInfo.objects.get(id=1).url
    if Publ.objects.filter(parent_id=0,remote=False).exists():
      data = filter_recommended(datetime_request,username,subs,filter['censor'],filter['nude'])
      publ_list = [publ['id'] for publ in data]
      user_list = [publ['username'] for publ in data]
      comment_count = Publ.objects.values("parent_id").annotate(count=Count('parent_id')).filter(parent_id__in=publ_list, remote=False).order_by("-count")
      publ_rating = PublRating.objects.values('level', 'positive', 'sum_like', 'sum_dislike').filter(publication__in=publ_list).order_by('-publication')
      check_like = PublRatingUser.objects.values('publication', 'positive').filter(username=username,publication__in=publ_list)
      r_user = UserProfile.objects.values('username', 'level', 'positive').filter(username__in=user_list)
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
        content = os.listdir(os.getcwd() + '/media/profile/' + str(data[i]['username']))
        content = [img.split('_') for img in content if 'jpeg' in img or 'gif' in img]
        for j in range(len(content)):
          if data[i]['id'] == int(content[j][0]):
            full_image = '{}/media/profile/{}/{}'.format(server_url,str(data[i]['username']),(content[j][0] + '_' + content[j][1]))
            data[i]['images'].append(full_image)
      return Response(data, status=status.HTTP_200_OK)
    else:
      return Response(False, status=status.HTTP_200_OK)



class HashtagViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (IsAuthenticated,)

  @action(methods=['POST'], detail=False)
  def get_hashtag_right(self, request, *args, **kwargs):
    now_time = timezone.now()
    one_month_ago = now_time - timedelta(days=30)
    censor = UserProfile.objects.values_list('censor', flat=True).filter(username__username=request.user.username)[0]
    if censor == True:
      hashtag_count = Hashtag.objects.values("hashtag").annotate(count=Count('hashtag')).filter(datetime__lte=now_time,
                                                                                                datetime__gte=one_month_ago,
                                                                                                comment=False).order_by("-count")[:10]
    if censor == False:
      hashtag_count = Hashtag.objects.values("hashtag").annotate(count=Count('hashtag')).filter(datetime__lte=now_time,
                                                                                                datetime__gte=one_month_ago,
                                                                                                censor=False,
                                                                                                comment=False).order_by( "-count")[:10]
    return Response(hashtag_count, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def get_hashtag_all(self, request, *args, **kwargs):
    now_time = timezone.now()
    one_month_ago = now_time - timedelta(days=30)
    censor = UserProfile.objects.values_list('censor', flat=True).filter(username__username=request.user.username)[0]
    if Hashtag.objects.all().exists():
      if censor == True:
        hashtag = Hashtag.objects.values('hashtag').annotate(count=Count('hashtag')).filter(comment=False,
                                                                                            datetime__lte=now_time,
                                                                                            datetime__gte=one_month_ago).order_by( "-count")[:50]
      if censor == False:
        hashtag = Hashtag.objects.values('hashtag').annotate(count=Count('hashtag')).filter(comment=False,
                                                                                            datetime__lte=now_time,
                                                                                            datetime__gte=one_month_ago,
                                                                                            censor=False).order_by("-count")[:100]
      return Response(hashtag, status=status.HTTP_200_OK)
    else:
      return Response(False, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def get_data_from_tag(self, request, *args, **kwargs):
    hashtag = request.data['hashtag']
    datetime_request = request.data['datetime_request']
    username = User.objects.get(username=request.user.username)
    server_url = ServerInfo.objects.get(id=1).url
    if not datetime_request:
      publ = set(
        Hashtag.objects.values_list('publication', flat=True).filter(hashtag=hashtag).order_by('-datetime')[:10])
      datetime_start = Publ.objects.values_list('datetime', flat=True).filter(id__in=publ).order_by('-datetime')[0]
      data = list(Publ.objects.values('id', 'username', 'username__username', 'message', 'datetime', 'edit').filter(id__in=publ).order_by('-datetime'))
    if datetime_request:
      datetime_start = datetime_request
      publ = set(Hashtag.objects.values_list('publication', flat=True).filter(hashtag=hashtag,
                                                                              datetime__lt=datetime_start).order_by('-datetime')[:10])
      data = list(Publ.objects.values('id', 'username', 'username__username', 'message', 'datetime', 'edit').filter(id__in=publ).order_by('-datetime'))
    publ_list = [publ['id'] for publ in data]
    user_list = [publ['username'] for publ in data]
    comment_count = Publ.objects.values("parent_id").annotate(count=Count('parent_id')).filter(parent_id__in=publ_list,remote=False).order_by("-count")
    publ_rating = PublRating.objects.values('level', 'positive', 'sum_like', 'sum_dislike').filter(publication__in=publ_list).order_by('-publication')
    check_like = PublRatingUser.objects.values('publication', 'positive').filter(username=username).filter(publication__in=publ_list)
    r_user = UserProfile.objects.values('username', 'level', 'positive').filter(username__in=user_list)
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
      content = os.listdir(os.getcwd() + '/media/profile/' + str(data[i]['username']))
      content = [img.split('_') for img in content if 'jpeg' in img or 'gif' in img]
      for j in range(len(content)):
        if data[i]['id'] == int(content[j][0]):
          full_image = '{}/media/profile/{}/{}'.format(server_url,str(data[i]['username']),(content[j][0] + '_' + content[j][1]))
          data[i]['images'].append(full_image)
    return Response(data, status=status.HTTP_200_OK)

class ActivityViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (IsAuthenticated,)

  @action(methods=['POST'], detail=False)
  def get_activity(self, request, *args, **kwargs):
    visit = UserProfile.objects.values_list('last_visit', flat=True).filter(username__username=request.user.username)[0]
    count_like = 0
    count_sub = 0
    count_men = 0
    if visit != None:
      if PublRatingUser.objects.filter(publ_user=request.user.id,datetime__lte=timezone.now(), datetime__gte=visit).exists():
        count_like += PublRatingUser.objects.filter(publ_user=request.user.id,datetime__lte=timezone.now(), datetime__gte=visit).count()
      if Sub.objects.filter(username=request.user.id,datetime__lte=timezone.now(), datetime__gte=visit).exists():
        count_sub += Sub.objects.filter(username=request.user.id,datetime__lte=timezone.now(), datetime__gte=visit).count()
      if Mention.objects.filter(username_id=request.user.id,datetime__lte=timezone.now(), datetime__gte=visit).exists():
        count_men += Mention.objects.filter(username_id=request.user.id,datetime__lte=timezone.now(), datetime__gte=visit).count()
      return Response({'count_like':count_like, 'count_sub':count_sub, 'count_men':count_men}, status=status.HTTP_200_OK)
    if visit == None:
      data = UserProfile.objects.get(username_id=request.user.id)
      data.now_visit = timezone.now()
      data.last_visit = timezone.now()
      data.save()
      return Response(status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def get_like(self, request, *args, **kwargs):
    likes_datetime = request.data['likes_datetime']
    if PublRatingUser.objects.filter(publ_user=request.user.id).exists():
      if not likes_datetime:
        datetime_start = PublRatingUser.objects.values_list('datetime', flat=True).filter(publ_user=request.user.id, positive=True).order_by('-datetime')[0]
        data = list(PublRatingUser.objects.values('publication', 'username', 'username__username', 'datetime')
                    .filter(datetime__lte=datetime_start, publ_user=request.user.id, positive=True).order_by('-datetime')[:15])
      if likes_datetime:
        datetime_start = likes_datetime
        data = list(PublRatingUser.objects.values('publication', 'username', 'username__username', 'datetime')
                    .filter(datetime__lt=datetime_start, publ_user=request.user.id, positive=True).order_by('-datetime')[:15])
      list_user = set([data[i]['username'] for i in range(len(data))])
      r_user = UserProfile.objects.values('username', 'level', 'positive').filter(username__in=list_user)
      for i in range(len(data)):
        for j in range(len(r_user)):
          if data[i]['username'] == r_user[j]['username']:
             data[i]['level'] = r_user[j]['level']
             data[i]['positive'] = r_user[j]['positive']
      return Response(data, status=status.HTTP_200_OK)
    else:
      return Response(False, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def get_sub(self, request, *args, **kwargs):
    likes_datetime = request.data['sub_datetime']
    if Sub.objects.filter(username__id=request.user.id).exists():
      if not likes_datetime:
        datetime_start = Sub.objects.values_list('datetime', flat=True).filter(username__id=request.user.id).order_by('-datetime')[0]
        data = list(Sub.objects.values('subscriber__id', 'subscriber__username', 'datetime')
                    .filter(username__id=request.user.id, datetime__lte=datetime_start).order_by('-datetime')[:15])

      if likes_datetime:
        datetime_start = likes_datetime
        data = list(Sub.objects.values('subscriber__id', 'subscriber__username', 'datetime')
                    .filter(username__id=request.user.id, datetime__lt=datetime_start).order_by('-datetime')[:15])
      list_user = set([data[i]['subscriber__id'] for i in range(len(data))])
      r_user = UserProfile.objects.values('username', 'level', 'positive').filter(username__in=list_user)
      for i in range(len(data)):
        for j in range(len(r_user)):
          if data[i]['subscriber__id'] == r_user[j]['username']:
             data[i]['level'] = r_user[j]['level']
             data[i]['positive'] = r_user[j]['positive']
      return Response(data, status=status.HTTP_200_OK)
    else:
      return Response(False, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def get_mention(self, request, *args, **kwargs):
    men_datetime = request.data['men_datetime']
    comment = request.data['comment']
    server_url = ServerInfo.objects.get(id=1).url
    if comment == False:
      if Mention.objects.filter(username__id=request.user.id, publication__parent_id=0).exists():
        if not men_datetime:
          datetime_start = Mention.objects.values_list('datetime', flat=True).filter(username__id=request.user.id, publication__parent_id=0).order_by('-datetime')[0]
          data = list(Mention.objects.annotate(publ_id=F('publication__id'), publ_user_id=F('publication__username__id'), publ_username=F('publication__username__username'),
                                               level_user=F('publication__username__userprofile__level'), positive_user=F('publication__username__userprofile__positive'),
                                               message=F('publication__message'),publ_datetime=F('publication__datetime'),edit=F('publication__edit'), parent_id=F('publication__parent_id'),
                                               positive=F('publication__publrating__positive'), level=F('publication__publrating__level'),
                                               sum_like=F('publication__publrating__sum_like'),sum_dislike=F('publication__publrating__sum_dislike'))
                                              .values('publ_id','publ_user_id', 'publ_username', 'level_user', 'positive_user', 'message','publ_datetime', 'edit', 'parent_id', 'level','positive', 'sum_like', 'sum_dislike','datetime')
                                            .filter(username__id=request.user.id, datetime__lte=datetime_start, parent_id=0).order_by('-datetime')[:10])
        if men_datetime:
          datetime_start = men_datetime
          data = list(Mention.objects.annotate(publ_id=F('publication__id'), publ_user_id=F('publication__username__id'), publ_username=F('publication__username__username'),
                                               level_user=F('publication__username__userprofile__level'), positive_user=F('publication__username__userprofile__positive'),
                                               message=F('publication__message'),publ_datetime=F('publication__datetime'),edit=F('publication__edit'), parent_id=F('publication__parent_id'),
                                               positive=F('publication__publrating__positive'), level=F('publication__publrating__level'),
                                               sum_like=F('publication__publrating__sum_like'),sum_dislike=F('publication__publrating__sum_dislike'))
                                              .values('publ_id','publ_user_id', 'publ_username', 'level_user', 'positive_user', 'message','publ_datetime', 'edit', 'parent_id', 'level','positive', 'sum_like', 'sum_dislike','datetime')
                                              .filter(username__id=request.user.id, datetime__lt=datetime_start, parent_id=0).order_by('-datetime')[:10])
        publ_list = [publ['publ_id'] for publ in data]
        comment_count = Publ.objects.values("parent_id").annotate(count=Count('parent_id')).filter(parent_id__in=publ_list, remote=False).order_by("-count")
        check_like = PublRatingUser.objects.values('publication', 'positive').filter(username__id=request.user.id,publication__in=publ_list)
        for i in range(len(data)):
          for j in range(len(check_like)):
            if check_like[j]['publication'] == data[i]['publ_id']:
              if check_like[j]['positive'] == True:
                data[i]['check_like'] = True
              if check_like[j]['positive'] == False:
                data[i]['check_dislike'] = True
          for j in range(len(comment_count)):
            if comment_count[j]['parent_id'] == data[i]['publ_id']:
              data[i]['comments'] = comment_count[j]['count']
          data[i]['images'] = []
          content = os.listdir(os.getcwd() + '/media/profile/' + str(data[i]['publ_user_id']))
          content = [img.split('_') for img in content if 'jpeg' in img or 'gif' in img]
          for j in range(len(content)):
            if data[i]['publ_id'] == int(content[j][0]):
              full_image = '{}/media/profile/{}/{}'.format(server_url,str(data[i]['publ_user_id']),(content[j][0] + '_' + content[j][1]))
              data[i]['images'].append(full_image)

        return Response(data, status=status.HTTP_200_OK)
      else:
        return Response(False, status=status.HTTP_200_OK)
    if comment == True:
      if Mention.objects.filter(~Q(publication__parent_id=0),username__id=request.user.id).exists():
        if not men_datetime:
          datetime_start = Mention.objects.values_list('datetime', flat=True).filter(~Q(publication__parent_id=0), username__id=request.user.id).order_by('-datetime')[0]
          data = list(Mention.objects.annotate(publ_id=F('publication__id'), publ_user_id=F('publication__username__id'),
                                     publ_username=F('publication__username__username'),
                                     level_user=F('publication__username__userprofile__level'),
                                     positive_user=F('publication__username__userprofile__positive'),
                                     message=F('publication__message'), publ_datetime=F('publication__datetime'),
                                     edit=F('publication__edit'), parent_id=F('publication__parent_id'),
                                     positive=F('publication__publrating__positive'),
                                     level=F('publication__publrating__level'),
                                     sum_like=F('publication__publrating__sum_like'),
                                     sum_dislike=F('publication__publrating__sum_dislike'))
            .values('publ_id', 'publ_user_id', 'publ_username', 'level_user', 'positive_user', 'message',
                    'publ_datetime', 'edit', 'parent_id', 'level', 'positive', 'sum_like', 'sum_dislike','datetime')
            .filter(~Q(parent_id=0), username__id=request.user.id, datetime__lte=datetime_start).order_by('-datetime')[:10])
        if men_datetime:
          datetime_start = men_datetime
          data = list(Mention.objects.annotate(publ_id=F('publication__id'), publ_user_id=F('publication__username__id'),
                                     publ_username=F('publication__username__username'),
                                     level_user=F('publication__username__userprofile__level'),
                                     positive_user=F('publication__username__userprofile__positive'),
                                     message=F('publication__message'), publ_datetime=F('publication__datetime'),
                                     edit=F('publication__edit'), parent_id=F('publication__parent_id'),
                                     positive=F('publication__publrating__positive'),
                                     level=F('publication__publrating__level'),
                                     sum_like=F('publication__publrating__sum_like'),
                                     sum_dislike=F('publication__publrating__sum_dislike'))
            .values('publ_id', 'publ_user_id', 'publ_username', 'level_user', 'positive_user', 'message',
                    'publ_datetime', 'edit', 'parent_id', 'level', 'positive', 'sum_like', 'sum_dislike','datetime')
            .filter(~Q(parent_id=0), username__id=request.user.id, datetime__lt=datetime_start).order_by('-datetime')[:10])
        publ_list = [publ['publ_id'] for publ in data]
        comment_count = Publ.objects.values("parent_id").annotate(count=Count('parent_id')).filter(parent_id__in=publ_list, remote=False).order_by("-count")
        check_like = PublRatingUser.objects.values('publication', 'positive').filter(username__id=request.user.id,publication__in=publ_list)
        for i in range(len(data)):
          for j in range(len(check_like)):
            if check_like[j]['publication'] == data[i]['publ_id']:
              if check_like[j]['positive'] == True:
                data[i]['check_like'] = True
              if check_like[j]['positive'] == False:
                data[i]['check_dislike'] = True
          for j in range(len(comment_count)):
            if comment_count[j]['parent_id'] == data[i]['publ_id']:
              data[i]['comments'] = comment_count[j]['count']
          data[i]['images'] = []
          content = os.listdir(os.getcwd() + '/media/profile/' + str(data[i]['publ_user_id']))
          content = [img.split('_') for img in content if 'jpeg' in img or 'gif' in img]
          for j in range(len(content)):
            if data[i]['publ_id'] == int(content[j][0]):
              full_image = '{}/media/profile/{}/{}'.format(server_url,str(data[i]['publ_user_id']),(content[j][0] + '_' + content[j][1]))
              data[i]['images'].append(full_image)

        return Response(data, status=status.HTTP_200_OK)
      else:
        return Response(False, status=status.HTTP_200_OK)


class DonatViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = (IsAuthenticated,)

  @action(methods=['POST'], detail=False)
  def get_donat_top(self, request, *args, **kwargs):
      data = Donat.objects.values('username_id','username__username').order_by('username').annotate(sum=Sum('sum')).order_by('-sum')[:5]
      for i in range(len(data)):
        if UserProfileStar.objects.filter(username_id=data[i]['username_id'], star=i+1).exists() == False:
          set_star(data[i]['username__username'], i+1)
      return Response(data, status=status.HTTP_200_OK)

  @action(methods=['POST'], detail=False)
  def get_donat_all(self, request, *args, **kwargs):
    data = Donat.objects.values('username_id','username__username').order_by('username').annotate(sum=Sum('sum')).order_by('-sum')
    return Response(data, status=status.HTTP_200_OK)

def set_star(username, stars):
  if UserProfileStar.objects.filter(~Q(username__username=username), star=stars).exists():
    UserProfileStar.objects.filter(~Q(username__username=username), star=stars).delete()
  username = User.objects.get(username=username)
  star = UserProfileStar.objects.create()
  star.username = username
  star.star = stars
  star.save()