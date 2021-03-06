# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-07-26 03:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('b', models.IntegerField(null=True)),
                ('s', models.IntegerField(null=True)),
                ('o', models.IntegerField(null=True)),
                ('description', models.TextField(null=True)),
                ('description_spanish', models.TextField(null=True)),
                ('event', models.TextField(null=True)),
                ('event_es', models.TextField(null=True)),
                ('tfs', models.IntegerField(null=True)),
                ('tfs_zulu', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Atbat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField(null=True)),
                ('b', models.IntegerField(null=True)),
                ('s', models.IntegerField(null=True)),
                ('o', models.IntegerField(null=True)),
                ('start_tfs', models.IntegerField(null=True)),
                ('start_tfs_zulu', models.DateTimeField(null=True)),
                ('stand', models.CharField(max_length=8, null=True)),
                ('b_height', models.FloatField(null=True)),
                ('p_throws', models.CharField(max_length=8, null=True)),
                ('description', models.TextField(null=True)),
                ('description_spanish', models.TextField(null=True)),
                ('event_num', models.IntegerField(null=True)),
                ('event', models.TextField(null=True)),
                ('event_es', models.TextField(null=True)),
                ('play_guid', models.CharField(max_length=64, null=True)),
                ('home_team_runs', models.IntegerField(null=True)),
                ('away_team_runs', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('start_datetime', models.DateTimeField(null=True)),
                ('type', models.CharField(max_length=2, null=True)),
                ('status', models.CharField(max_length=2, null=True)),
                ('away_score', models.IntegerField(null=True)),
                ('home_score', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Inning',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField()),
                ('top_bottom', models.CharField(max_length=8)),
                ('next', models.CharField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Pitch',
            fields=[
                ('description', models.TextField(null=True)),
                ('description_spanish', models.TextField(null=True)),
                ('local_id', models.IntegerField(null=True)),
                ('tfs', models.IntegerField(null=True)),
                ('tfs_zulu', models.DateTimeField(null=True)),
                ('x', models.FloatField(null=True)),
                ('y', models.FloatField(null=True)),
                ('event_num', models.IntegerField(null=True)),
                ('sv_id', models.IntegerField(primary_key=True, serialize=False)),
                ('play_guid', models.CharField(max_length=64, null=True)),
                ('start_speed', models.FloatField(null=True)),
                ('end_speed', models.FloatField(null=True)),
                ('sz_top', models.FloatField(null=True)),
                ('sz_bot', models.FloatField(null=True)),
                ('pfx_x', models.FloatField(null=True)),
                ('pfx_z', models.FloatField(null=True)),
                ('px', models.FloatField(null=True)),
                ('pz', models.FloatField(null=True)),
                ('x0', models.FloatField(null=True)),
                ('y0', models.FloatField(null=True)),
                ('z0', models.FloatField(null=True)),
                ('vx0', models.FloatField(null=True)),
                ('vy0', models.FloatField(null=True)),
                ('vz0', models.FloatField(null=True)),
                ('ax', models.FloatField(null=True)),
                ('ay', models.FloatField(null=True)),
                ('az', models.FloatField(null=True)),
                ('break_y', models.FloatField(null=True)),
                ('break_angle', models.FloatField(null=True)),
                ('break_length', models.FloatField(null=True)),
                ('pitch_type', models.CharField(max_length=8, null=True)),
                ('type_confidence', models.FloatField(null=True)),
                ('zone', models.IntegerField(null=True)),
                ('nasty', models.FloatField(null=True)),
                ('spin_dir', models.FloatField(null=True)),
                ('spin_rate', models.FloatField(null=True)),
                ('hit_distance', models.FloatField(null=True)),
                ('launch_speed', models.FloatField(null=True)),
                ('launch_angle', models.FloatField(null=True)),
                ('atbat_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='gd2.Atbat')),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('first', models.CharField(max_length=64)),
                ('last', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('abbrev', models.CharField(max_length=4)),
            ],
        ),
        migrations.AddField(
            model_name='inning',
            name='away_team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='away_team_inning_set', to='gd2.Team'),
        ),
        migrations.AddField(
            model_name='inning',
            name='game_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='gd2.Game'),
        ),
        migrations.AddField(
            model_name='inning',
            name='home_team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='home_team_inning_set', to='gd2.Team'),
        ),
        migrations.AddField(
            model_name='game',
            name='away_probable_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='away_probable_game_set', to='gd2.Player'),
        ),
        migrations.AddField(
            model_name='game',
            name='home_probable_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='home_probable_game_set', to='gd2.Player'),
        ),
        migrations.AddField(
            model_name='atbat',
            name='batter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='batter_atbat_set', to='gd2.Player'),
        ),
        migrations.AddField(
            model_name='atbat',
            name='inning_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='gd2.Inning'),
        ),
        migrations.AddField(
            model_name='atbat',
            name='pitcher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='pitcher_atbat_set', to='gd2.Player'),
        ),
        migrations.AddField(
            model_name='action',
            name='inning_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='gd2.Inning'),
        ),
    ]
