from rest_framework import serializers
from gd2.models import Pitch, Atbat, Action, Inning, Game, Player, Team

class PitchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pitch
        fields = '__all__'

class AtbatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atbat 
        fields = '__all__'

class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action 
        fields = '__all__'

class InningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inning
        fields = '__all__'

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'
