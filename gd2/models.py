from __future__ import unicode_literals
from django.db import models

class Pitch(models.Model):
    atbat = models.ForeignKey('Atbat', on_delete=models.CASCADE)
    description = models.TextField(null=True)
    description_spanish = models.TextField(null=True)
    local_id = models.IntegerField(null=True)
    pitch_type = models.CharField(max_length=8, null=True)
    tfs = models.IntegerField(null=True)
    tfs_zulu = models.DateTimeField(null=True)
    x = models.FloatField(null=True)
    y = models.FloatField(null=True)
    event_num = models.IntegerField(null=True)
    sv_id = models.CharField(max_length=16, null=True)
    play_guid = models.CharField(max_length=64, null=True)
    start_speed = models.FloatField(null=True)
    end_speed = models.FloatField(null=True)
    sz_top = models.FloatField(null=True)
    sz_bot = models.FloatField(null=True)
    pfx_x = models.FloatField(null=True)
    pfx_z = models.FloatField(null=True)
    px = models.FloatField(null=True)
    pz = models.FloatField(null=True)
    x0 = models.FloatField(null=True)
    y0 = models.FloatField(null=True)
    z0 = models.FloatField(null=True)
    vx0 = models.FloatField(null=True)
    vy0 = models.FloatField(null=True)
    vz0 = models.FloatField(null=True)
    ax = models.FloatField(null=True)
    ay = models.FloatField(null=True)
    az = models.FloatField(null=True)
    break_y = models.FloatField(null=True)
    break_angle = models.FloatField(null=True)
    break_length = models.FloatField(null=True)
    pitch_type = models.CharField(max_length=8, null=True)
    type_confidence = models.FloatField(null=True)
    zone = models.IntegerField(null=True)
    nasty = models.FloatField(null=True)
    spin_dir = models.FloatField(null=True)
    spin_rate = models.FloatField(null=True)
    hit_distance = models.FloatField(null=True)
    launch_speed = models.FloatField(null=True)
    launch_angle = models.FloatField(null=True)

class Runner(models.Model):
    atbat = models.ForeignKey('Atbat', on_delete=models.CASCADE)
    runner = models.ForeignKey('Player', related_name='runner_atbat_set', 
                                on_delete=models.CASCADE)
    start = models.CharField(max_length=2, null=True)
    end = models.CharField(max_length=2, null=True)
    event = models.CharField(max_length=64, null=True)
    event_num = models.IntegerField(null=True)
 
class Atbat(models.Model):
    inning = models.ForeignKey('Inning',on_delete=models.CASCADE)
    num = models.IntegerField(null=True)
    b = models.IntegerField(null=True)
    s = models.IntegerField(null=True)
    o = models.IntegerField(null=True)
    start_tfs = models.IntegerField(null=True)
    start_tfs_zulu = models.DateTimeField(null=True, db_index=True)
    batter = models.ForeignKey('Player', related_name='batter_atbat_set', 
                                on_delete=models.CASCADE)
    stand = models.CharField(max_length=8, null=True)
    b_height = models.CharField(max_length=8, null=True)
    pitcher = models.ForeignKey('Player', related_name='pitcher_atbat_set', 
                                on_delete=models.CASCADE)
    p_throws = models.CharField(max_length=8, null=True)
    description = models.TextField(null=True)
    description_spanish = models.TextField(null=True)
    event = models.TextField(null=True)
    event_spanish = models.TextField(null=True)
    event_num = models.IntegerField(null=True)
    play_guid = models.CharField(max_length=64, null=True)
    home_team_runs = models.IntegerField(null=True)
    away_team_runs = models.IntegerField(null=True)

class Action(models.Model):
    inning = models.ForeignKey('Inning', on_delete=models.CASCADE)
    b = models.IntegerField(null=True)
    s = models.IntegerField(null=True)
    o = models.IntegerField(null=True)
    description = models.TextField(null=True)
    description_spanish = models.TextField(null=True)
    event = models.TextField(null=True)
    event_es = models.TextField(null=True)
    tfs = models.IntegerField(null=True)
    tfs_zulu = models.DateTimeField(null=True)

class Inning(models.Model):
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    num = models.IntegerField(null=False)
    top_bottom = models.CharField(max_length=8)
    away_team = models.ForeignKey('Team', 
                                  related_name='away_team_inning_set', 
                                  on_delete=models.CASCADE,)
    home_team = models.ForeignKey('Team', 
                                  related_name='home_team_inning_set',
                                  on_delete=models.CASCADE,)
    next = models.CharField(max_length=2)

class Game(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    start_datetime=models.DateTimeField(null=True)
    type = models.CharField(max_length=2, null=True)
    status = models.CharField(max_length=2, null=True)
    away_team = models.ForeignKey('Team',
                                  related_name='away_game_set',
                                  null=True,
                                  on_delete=models.SET_NULL,)
    home_team = models.ForeignKey('Team',
                                  related_name='home_game_set',
                                  null=True,
                                  on_delete=models.SET_NULL,)
    away_runs = models.IntegerField(null=True)
    home_runs = models.IntegerField(null=True)
    away_hits = models.IntegerField(null=True)
    home_hits = models.IntegerField(null=True)
    home_probable = models.ForeignKey('Player', 
                                      related_name='home_probable_game_set',
                                      null=True,
                                      on_delete=models.SET_NULL,)
    away_probable = models.ForeignKey('Player', 
                                      related_name='away_probable_game_set',
                                      null=True,
                                      on_delete=models.SET_NULL,)

class Player(models.Model):
    id = models.IntegerField(primary_key=True)
    first = models.CharField(max_length=64)
    last = models.CharField(max_length=64)

class Team(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    abbrev = models.CharField(max_length=4)
