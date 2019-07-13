#!/usr/bin/env python

import os
import re
import urllib2
import datetime
import xml.etree.ElementTree as ET 

from pytz import UTC
from bs4 import BeautifulSoup
from django.db import transaction
from django.db.models import Max

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mlbslicedb.settings")
import django
django.setup()

from gd2.models import Pitch, Runner, Atbat, Action, Inning, Game, Player, Team

action_fields = set(f.name for f in Action._meta.get_fields())
atbat_fields = set(f.name for f in Atbat._meta.get_fields())
pitch_fields = set(f.name for f in Pitch._meta.get_fields())
runner_fields = set(f.name for f in Runner._meta.get_fields())

def clean_zero_len_string(obj_dict):
    for k,v in obj_dict.items():
        if v == '':
            obj_dict[k] = None
    return obj_dict

def add_team(team_dict):
    try:
        team = Team.objects.get(id=team_dict['id'])
        team.name = team_dict['name']
        team.abbrev = team_dict['abbrev']
    except Team.DoesNotExist:
        team = Team(**team_dict)
    team.save()
    return team

def add_player(player_dict):
    try:
        player = Player.objects.get(id=player_dict['id'])
        player.first = player_dict['first']
        player.last = player_dict['last']
    except Player.DoesNotExist:
        player = Player(id=player_dict['id'],
                        first=player_dict['first'],
                        last=player_dict['last'],)
    player.save()
    return player

@transaction.atomic
def add_game(game_url):
    gamecenter_url = game_url + 'gamecenter.xml'
    game_game_url = game_url + 'game.xml'
    gamecenter_xml = urllib2.urlopen(gamecenter_url).read()
    gamecenter_root = ET.fromstring(gamecenter_xml)
    gamecenter_attrib = gamecenter_root.attrib
    game_id = gamecenter_attrib['id']
    game_status = gamecenter_attrib['status']
    game_type = gamecenter_attrib['type']
    probables_element = gamecenter_root.findall('probables')[0]
    home_probable_element = probables_element.findall('home')[0]
    home_prob_id = home_probable_element.findall('player_id')[0].text
    home_prob_first = home_probable_element.findall('useName')[0].text
    home_prob_last = home_probable_element.findall('lastName')[0].text
    
    away_probable_element = probables_element.findall('away')[0]
    away_prob_id = home_probable_element.findall('player_id')[0].text
    away_prob_first = home_probable_element.findall('useName')[0].text
    away_prob_last = home_probable_element.findall('lastName')[0].text

    game_game_xml = urllib2.urlopen(game_game_url).read()
    game_game_root = ET.fromstring(game_game_xml)
    game_game_attrib = game_game_root.attrib
    team_elements = game_game_root.findall('team')
    for team_element in team_elements:
        team_attrib = team_element.attrib
        team_dict = {'id': team_attrib['id'],
                     'name': team_attrib['name'],
                     'abbrev': team_attrib['abbrev'],}
        if team_attrib['type'] == 'home':
            home_team = add_team(team_dict)
        elif team_attrib['type'] == 'away':
            away_team = add_team(team_dict)
        else:
            pass

    try:
        game = Game.objects.get(id=game_id)
        print 'game already exists: %s' % game_id
        return
    except Game.DoesNotExist:
        game = Game(id=game_id,)
    
    if home_prob_id:
        home_prob_player = add_player({'id': int(home_prob_id),
                                       'first': home_prob_first,
                                       'last': home_prob_last,})
        game.home_probable = home_prob_player

    if away_prob_id:
        away_prob_player = add_player({'id': int(away_prob_id),
                                       'first': away_prob_first,
                                       'last': away_prob_last,})
        game.away_probable = away_prob_player

    game.home_team = home_team
    game.away_team = away_team
    game.status = game_status
    game.type = game_type

    if game.status == 'F':
        box_url = game_url + 'boxscore.xml'
        box_xml = urllib2.urlopen(box_url).read()
        box_root = ET.fromstring(box_xml)
        box_attrib = box_root.attrib
        linescore_element = box_root.findall('linescore')[0]
        linescore_attrib = linescore_element.attrib
        away_runs = linescore_attrib['away_team_runs']
        away_hits = linescore_attrib['away_team_hits']
        home_runs = linescore_attrib['home_team_runs']
        home_hits = linescore_attrib['home_team_hits']
        game.away_runs = away_runs
        game.away_hits = away_hits
        game.home_runs = home_runs
        game.home_hits = home_hits 
        game.save()
        
        players_url = game_url + 'players.xml'
        players_xml = urllib2.urlopen(players_url).read()
        players_root = ET.fromstring(players_xml)

        for team_elem in players_root.findall('team'):
            for player_elem in team_elem.findall('player'):
                add_player(player_elem.attrib)                

        innings_url = game_url + 'inning/'
        innings_html = urllib2.urlopen(innings_url).read()
        innings_soup = BeautifulSoup(innings_html, 'html.parser')
        inning_links = [link.get('href') for 
                            link in innings_soup.find_all('a') 
                                if re.search('inning_\d',link.get('href'))]

        for inning_link in inning_links:
            inning_url = innings_url + inning_link
            inning_xml = urllib2.urlopen(inning_url).read()
            inning_root = ET.fromstring(inning_xml)

            for half_elem in inning_root.getchildren():
                inning_dict = {'game': Game.objects.get(id=game_id),
                               'top_bottom': half_elem.tag,
                               'num': int(inning_root.attrib['num']),
                               'away_team': away_team,
                               'home_team': home_team,
                               'next': inning_root.attrib['next'],}
                inning_dict = clean_zero_len_string(inning_dict)
                inning = Inning(**inning_dict)
                inning.save()
                
                for event_elem in half_elem.getchildren():
                    if event_elem.tag.lower() == 'atbat':
                        atbat_dict = dict(event_elem.items())
                        atbat_dict['inning'] = inning
                        atbat_dict['batter'] = Player.objects.get(
                                                id=atbat_dict['batter'])
                        atbat_dict['pitcher'] = Player.objects.get(
                                                id=atbat_dict['pitcher'])
                        atbat_dict['description'] = \
                                        atbat_dict.pop('des', None)
                        atbat_dict['description_spanish'] = \
                                        atbat_dict.pop('des_es', None)

                        atbat_dict = {k: v for k, v in atbat_dict.items()
                                        if k in atbat_fields}
                        atbat_dict = clean_zero_len_string(atbat_dict)
                        atbat = Atbat(**atbat_dict)
                        atbat.save()
                        
                        for pitch_runner_elem in event_elem.getchildren():
                            if pitch_runner_elem.tag.lower() == 'pitch':
                                pitch_elem = pitch_runner_elem
                                pitch_dict = dict(pitch_elem.items())
                                pitch_dict['atbat'] = atbat
                                pitch_dict['local_id'] = pitch_dict.pop(
                                                                'id', None)
                                pitch_dict['description'] = \
                                            pitch_dict.pop('des', None)
                                pitch_dict['description_spanish'] = \
                                            pitch_dict.pop('des_es', None)
                                pitch_dict = {k: v for k, v in 
                                                pitch_dict.items() if 
                                                    k in pitch_fields}
                                pitch_dict = clean_zero_len_string(
                                                pitch_dict)
                                pitch = Pitch(**pitch_dict)
                                pitch.save()
                            
                            elif pitch_runner_elem.tag.lower() == 'runner':
                                runner_elem = pitch_runner_elem
                                runner_dict = dict(runner_elem.items())
                                runner_dict['atbat'] = atbat
                                runner_dict['runner'] = \
                                    Player.objects.get(id=runner_dict['id'])
                                runner_dict = {k: v for k, v in 
                                                runner_dict.items() if 
                                                    k in runner_fields}
                                runner_dict = clean_zero_len_string(
                                                runner_dict)
                                runner = Runner(**runner_dict)
                                runner.save()

                    elif event_elem.tag.lower() == 'action':
                        action_dict = dict(event_elem.items())
                        action_dict['inning'] = inning
                        action_dict['description'] = \
                                        action_dict.pop('des', None)
                        action_dict['description_spanish'] = \
                                        action_dict.pop('des_es', None)

                        action_dict = {k: v for k, v in action_dict.items()
                                        if k in action_fields}
                        action_dict = clean_zero_len_string(action_dict)
                        action = Action(**action_dict)
                        action.save()
        game.start_datetime = game.inning_set.first(
                                ).atbat_set.first(
                                ).start_tfs_zulu
        game.save()
    return

if __name__ == "__main__":
  base_url = 'http://gd2.mlb.com/components/game/mlb/'
  
  recent_datetime_dict = Game.objects.all().aggregate(Max('start_datetime'))
  recent_datetime = recent_datetime_dict['start_datetime__max']
  if recent_datetime:
      start_datetime = recent_datetime - datetime.timedelta(days=1)
  else:
      start_datetime = datetime.datetime(2011, 3, 1, 0, 0, 0).replace(
                                                                tzinfo=UTC)
  cur_datetime = start_datetime
  end_datetime = datetime.datetime.now().replace(tzinfo=UTC) + \
                 datetime.timedelta(days=1)
  
  while cur_datetime < end_datetime:
      print 'loading games from ' + cur_datetime.date().isoformat()
      day_url = base_url + 'year_%d/month_%02d/day_%02d' % (cur_datetime.year,
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
  
      for game_link in game_links:
          game_url = day_url + '/' + game_link[game_link.find('/')+1:]
          print 'game url: %s' % game_url
          try:
              add_game(game_url)
          except:
              print 'error reading game at: %s' % game_url
              continue 
  
      cur_datetime += datetime.timedelta(days=1)
