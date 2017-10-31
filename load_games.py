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
        player = Player(**player_dict)
    player.save()
    return player

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
        game_game_url = game_url + 'game.xml'
        try:
            gamecenter_xml = urllib2.urlopen(gamecenter_url).read()
            gamecenter_root = ET.fromstring(gamecenter_xml)
            gamecenter_attrib = gamecenter.attrib
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

        except:
            break
        
        try:
            game = Game.objects.get(id=game_id)
        except:
            game = Game(id=game_id,)
        
        home_prob_player = add_player({'id': home_prob_id,
                                       'first': home_prob_first,
                                       'last': home_prob_last,})
        away_prob_player = add_player({'id': away_prob_id,
                                       'first': away_prob_first,
                                       'last': away_prob_last,})

        game.home_team = home_team
        game.away_team = away_team
        game.home_probable = home_prob_player
        game.away_probable = away_prob_player
        game.status = game_status
        game.type = game_type
        game.save()

        if game.status == 'F':
            box_url = game_url + 'boxscore.xml'
            box_xml = urllib2.urlopen(box_url).read()
            box_root = ET.fromstring(box_xml)
            box_attrib = box.attrib
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
