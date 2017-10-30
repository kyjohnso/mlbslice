#!/usr/bin/env python

import os
import xml.etree.ElementTree
import urllib2
import datetime

from bs4 import BeautifulSoup
from django.db.models import Max

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mlbslicedb.settings")
import django
django.setup()

from gd2.models import Pitch, Atbat, Action, Inning, Game, Player, Team

base_url = 'http://gd2.mlb.com/components/game/mlb/'

recent_datetime_dict = Game.objects.all().aggregate(Max('start_datetime'))
recent_datetime = recent_datetime_dict['start_datetime__max']
if recent_datetime:
    start_datetime = recent_datetime - datetime.timedelta(days=1)
else:
    start_datetime = datetime.datetime(2007, 3, 1, 0, 0, 0)
cur_datetime = start_datetime
end_datetime = datetime.datetime.now() + datetime.timedelta(days=1)

while cur_datetime < end_datetime:
    day_url = base_url + 'year_%d/month_%02d/day_%02d/' % (cur_datetime.year,
                                                           cur_datetime.month,
                                                           cur_datetime.day,)

    try:
        day_html = urllib2.urlopen(day_url).read()
        day_soup = BeautifulSoup(day_html, 'html.parser')
        game_links = [link.get('href') 
                        for link in day_soup.find_all('a')
                          if link.get('href').find('gid_') >= 0]
    
    except urllib2.HTTPError:
        game_links = []
        pass

    for game_link in game_links:
        game_url = day_url + game_link
        gamecenter_url = game_url + 'gamecenter.xml'
        try:
            gamecenter_xml = urllib2.urlopen(gamecenter_url).read()
            gamecenter_root = ET.fromstring(gamecenter_xml)
            probables_element = gamecenter_root.findall('probables')[0]
            home_probable_element = probables_element.findall('home')[0]
            home_prob_id = home_probable_element.findall('player_id')[0].text
            home_prob_first = home_probable_element.findall('useName')[0].text
            home_prob_last = home_probable_element.findall('lastName')[0].text
            
            away_probable_element = probables_element.findall('away')[0]
            away_prob_id = home_probable_element.findall('player_id')[0].text
            away_prob_first = home_probable_element.findall('useName')[0].text
            away_prob_last = home_probable_element.findall('lastName')[0].text


