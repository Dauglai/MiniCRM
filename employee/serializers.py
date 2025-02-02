from django.contrib.auth.models import User
from pkg_resources import require
from rest_framework import serializers
from .models import Task, Profile, Comment, Result, Coordination, MentionNotification, Role


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['name', 'surname', 'patronymic', 'work', 'personal', 'job', 'birthday', 'photo', 'author']

class ProfileCreateSerializer(serializers.ModelSerializer):
    author = serializers.CurrentUserDefault()
    class Meta:
        model = Profile
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    task_id = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), source='task', required=False)
    owner_id = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all(), source='owner', required=False)
    mentions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Profile.objects.all(), required=False
    )
    owner = ProfileSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['task_id', 'owner_id', 'text', 'datetime', 'owner', 'mentions']

    def create(self, validated_data):
        mentions = validated_data.pop('mentions', [])
        comment = super().create(validated_data)
        for user in mentions:
            MentionNotification.objects.create(comment=comment, mentioned_user=user)
        return comment


class ResultSerializer(serializers.ModelSerializer):
    author = serializers.CurrentUserDefault()
    class Meta:
        model = Result
        fields = '__all__'

    def create(self, validated_data):
        # validated_data будет содержать объект Task, так как task_id преобразуется в task
        return Result.objects.create(**validated_data)

class CoordinationSerializer(serializers.ModelSerializer):
    task_id = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), source='task', required=False)
    coordinator_id = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all(), source='coordinator', required=False)
    class Meta:
        model = Coordination
        fields = ['task_id', 'coordinator_id', 'is_agreed', 'datetime']
        
    def create(self, validated_data):
        # validated_data будет содержать объект Task, так как task_id преобразуется в task
        return Coordination.objects.create(**validated_data)

class TaskCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    file = serializers.FileField(required=False)

    class Meta:
        model = Task
        fields = ['id','author', 'name', 'deadline', 'description', 'file', 'addressee', 'observers', 'coordinators']



class TaskSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    addressee = ProfileSerializer(read_only=True)
    coordination_set = CoordinationSerializer(many=True, read_only=True)
    comment_set = CommentSerializer(many=True, read_only=True)
    result_set = ResultSerializer(many=True, read_only=True)
    observer_set = ProfileSerializer(many=True, read_only=True, source='observers')
    coordinator_set = ProfileSerializer(many=True, read_only=True, source='coordinators')
    class Meta:
        model = Task
        fields = ['id','name', 'datetime', 'deadline', 'description', 'file', 'author', 'addressee', 'status',
                  'observers', 'coordinators', 'observer_set', 'is_agreed', 'coordinator_set', 'coordination_set',
                  'comment_set', 'result_set']


class RoleSerializer(serializers.ModelSerializer):
    worker = ProfileSerializer(read_only=True, source='profile')

    class Meta:
        model = Role
        fields = ['id', 'name', 'worker', 'profile', 'outlet']