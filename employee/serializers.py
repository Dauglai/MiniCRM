from rest_framework import serializers
from .models import Task, Topic, Profile, Comment, Result, Coordination


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    author = serializers.CurrentUserDefault()
    class Meta:
        model = Profile
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class ResultSerializer(serializers.ModelSerializer):
    author = serializers.CurrentUserDefault()
    class Meta:
        model = Result
        fields = '__all__'

class CoordinationSerializer(serializers.ModelSerializer):
    coordinator = serializers.CurrentUserDefault()
    class Meta:
        model = Coordination
        fields = ['coordinator', 'is_agreed', 'datetime']


class TaskSerializer(serializers.ModelSerializer):
    author = serializers.CurrentUserDefault()
    topic = TopicSerializer(read_only=True)
    coordination_set = CoordinationSerializer(many=True, read_only=True)
    comment_set = CommentSerializer(many=True, read_only=True)
    result = ResultSerializer(many=True, read_only=True)
    class Meta:
        model = Task
        fields = ['name', 'topic', 'datetime', 'deadline', 'description', 'file', 'author', 'addressee', 'status',
                  'observers', 'is_agreed', 'coordinators', 'coordination_set', 'comment_set', 'result']