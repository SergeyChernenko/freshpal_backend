from mainpage.models import UserProfile, Sub, Publ, PublRating, PublRatingUser, Rating
from home.models import CurseWords, Hashtag
from django.contrib.auth.models import User

from nudenet import NudeClassifierLite

import re,string

def more_zero_user(new_sum, new_rating):
  start_sum = list(Rating.objects.values('level', 'like', 'sum').filter(sum__lte=new_sum).order_by("-level"))[0]
  finish_sum = list(Rating.objects.values('level', 'like', 'sum').filter(sum__gt=new_sum).order_by("level"))[0]
  balance = round((finish_sum['sum'] - new_sum) / (finish_sum['sum'] - start_sum['sum']), 2)
  new_level = start_sum['level'] + (1 - balance)
  new_rating.level = new_level
  new_rating.like = start_sum['like']
  new_rating.sum = new_sum
  new_rating.positive = True
  new_rating.save()

def less_zero_user(new_sum, new_rating):
  new_sum = abs(new_sum)
  start_sum = list(Rating.objects.values('level', 'like', 'sum').filter(sum__lte=new_sum).order_by("-level"))[0]
  finish_sum = list(Rating.objects.values('level', 'like', 'sum').filter(sum__gt=new_sum).order_by("level"))[0]
  balance = round((finish_sum['sum'] - new_sum) / (finish_sum['sum'] - start_sum['sum']), 2)
  new_level = start_sum['level'] + (1 - balance)
  new_rating.level = new_level
  new_rating.like = 0
  new_rating.sum = new_sum
  new_rating.positive = False
  new_rating.save()

def standart_user(new_rating):
  new_rating.level = 1
  new_rating.like = 1
  new_rating.sum = 0
  new_rating.positive = True
  new_rating.save()

def like_user(username, like_cost):
  new_rating = UserProfile.objects.get(username=username)
  if new_rating.positive == True:
    sum = new_rating.sum
    new_sum = sum + like_cost
    more_zero_user(new_sum, new_rating)
    return 0
  if new_rating.positive == False:
    sum = new_rating.sum
    new_sum = like_cost - sum
    if new_sum < 0:
      less_zero_user(new_sum, new_rating)
    if new_sum > 0:
      more_zero_user(new_sum, new_rating)
    if new_sum == 0:
      standart_user(new_rating)
    return 0

def dislike_user(username, like_cost):
  new_rating = UserProfile.objects.get(username=username)
  if new_rating.positive == True:
    sum = new_rating.sum
    new_sum = sum - like_cost
    if new_sum > 0:
      more_zero_user(new_sum, new_rating)
    if new_sum < 0:
      less_zero_user(new_sum, new_rating)
    if new_sum == 0:
      standart_user(new_rating)
    return 0
  if new_rating.positive == False:
    sum = new_rating.sum
    new_sum = sum + like_cost
    less_zero_user(new_sum, new_rating)
    return 0

def more_zero_publ(new_sum, new_rating, pos):
  start_sum = list(Rating.objects.values('level', 'like', 'sum').filter(sum__lte=new_sum).order_by("-level"))[0]
  finish_sum = list(Rating.objects.values('level', 'like', 'sum').filter(sum__gt=new_sum).order_by("level"))[0]
  balance = round((finish_sum['sum'] - new_sum) / (finish_sum['sum'] - start_sum['sum']), 2)
  new_level = start_sum['level'] + (1 - balance)
  new_rating.level = new_level
  new_rating.sum = new_sum
  new_rating.positive = True
  if pos == True:
    new_rating.sum_like += 1
  if pos == False:
    new_rating.sum_dislike += 1
  new_rating.save()

def less_zero_publ(new_sum, new_rating, pos):
  new_sum = abs(new_sum)
  start_sum = list(Rating.objects.values('level', 'like', 'sum').filter(sum__lte=new_sum).order_by("-level"))[0]
  finish_sum = list(Rating.objects.values('level', 'like', 'sum').filter(sum__gt=new_sum).order_by("level"))[0]
  balance = round((finish_sum['sum'] - new_sum) / (finish_sum['sum'] - start_sum['sum']), 2)
  new_level = start_sum['level'] + (1 - balance)
  new_rating.level = new_level
  new_rating.sum = new_sum
  new_rating.positive = False
  if pos == True:
    new_rating.sum_like += 1
  if pos == False:
    new_rating.sum_dislike += 1
  new_rating.save()

def standart_publ(new_rating, pos):
  new_rating.level = 1
  new_rating.sum = 0
  new_rating.positive = True
  if pos == True:
    new_rating.sum_like += 1
  if pos == False:
    new_rating.sum_dislike += 1
  new_rating.save()

def like_publ(id, like_cost):
  new_rating = PublRating.objects.get(publication=id)
  if new_rating.positive == True:
    sum = new_rating.sum
    new_sum = sum + like_cost
    more_zero_publ(new_sum, new_rating, True)
    return 0
  if new_rating.positive == False:
    sum = new_rating.sum
    new_sum = like_cost - sum
    if new_sum < 0:
      less_zero_publ(new_sum, new_rating, True)
    if new_sum > 0:
      more_zero_publ(new_sum, new_rating, True)
    if new_sum == 0:
      standart_publ(new_rating, True)
    return 0

def dislike_publ(id, like_cost):
  new_rating = PublRating.objects.get(publication=id)
  if new_rating.positive == True:
    sum = new_rating.sum
    new_sum = sum - like_cost
    if new_sum > 0:
      more_zero_publ(new_sum, new_rating, False)
    if new_sum < 0:
      less_zero_publ(new_sum, new_rating, False)
    if new_sum == 0:
      standart_publ(new_rating, False)
    return 0
  if new_rating.positive == False:
    sum = new_rating.sum
    new_sum = sum + like_cost
    less_zero_publ(new_sum, new_rating, False)
    return 0

def add_cost(id, pub_user, username, like_cost, positive):
  add_cost = PublRatingUser.objects.create()
  id = Publ.objects.get(id=id)
  username = User.objects.get(username=username)
  add_cost.publication = id
  add_cost.username = username
  add_cost.publ_user = int(pub_user.id)
  add_cost.like = like_cost
  add_cost.positive = positive
  add_cost.save()

def check_text_censor(word):
  censor = CurseWords.objects.values_list('word',flat=True).all()
  d = {'а': ['а', 'a', '@'],
       'б': ['б', '6', 'b'],
       'в': ['в', 'b', 'v'],
       'г': ['г', 'r', 'g'],
       'д': ['д', 'd'],
       'е': ['е', 'e'],
       'ё': ['ё', 'e'],
       'ж': ['ж', 'zh', '*'],
       'з': ['з', '3', 'z'],
       'и': ['и', 'u', 'i'],
       'й': ['й', 'u', 'i'],
       'к': ['к', 'k', 'i{', '|{'],
       'л': ['л', 'l', 'ji'],
       'м': ['м', 'm'],
       'н': ['н', 'h', 'n'],
       'о': ['о', 'o', '0'],
       'п': ['п', 'n', 'p'],
       'р': ['р', 'r', 'p'],
       'с': ['с', 'c', 's'],
       'т': ['т', 'm', 't'],
       'у': ['у', 'y', 'u'],
       'ф': ['ф', 'f'],
       'х': ['х', 'x', 'h', '}{'],
       'ц': ['ц', 'c', 'u,'],
       'ч': ['ч', 'ch'],
       'ш': ['ш', 'sh'],
       'щ': ['щ', 'sch'],
       'ь': ['ь', 'b'],
       'ы': ['ы', 'bi'],
       'ъ': ['ъ'],
       'э': ['э', 'e'],
       'ю': ['ю', 'io'],
       'я': ['я', 'ya']
       }

  for key, value in d.items():
    for letter in value:
      for phr in word:
        if letter == phr:
          word = word.replace(phr, key)

  for part in range(len(word)):
    for cen in censor:
      fragment = word[part: part + len(cen)]
      if cen == fragment and cen and fragment:
        return True

def strip_links(text):
  link_regex = re.compile('((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', re.DOTALL)
  links = re.findall(link_regex, text)
  for link in links:
    text = text.replace(link[0], ', ')
  return text


def strip_all_entities(text):
  entity_prefixes = ['@', '#']
  for separator in string.punctuation:
    if separator not in entity_prefixes:
      text = text.replace(separator, ' ')
  words = []
  for word in text.split():
    word = word.strip()
    if word:
      if word[0] not in entity_prefixes:
        words.append(word)
  return ' '.join(words)

def clean_text(text):
  text = strip_all_entities(strip_links(text))
  text = text.lower().split()
  text = [tx for tx in text if tx.isdigit() == False]
  return text


def detector_nude(image):
  detector = NudeClassifierLite()
  result = detector.classify(image)
  unsafe = result[image]['unsafe']
  if unsafe > 0.8:
    return True
  else:
    return False





