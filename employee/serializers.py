from django.contrib.auth.models import User
from pkg_resources import require
from rest_framework import serializers

from catalog.models import Order
from catalog.serializers import OrderSerializer
from .consumers import online_users
from .models import Task, Profile, Comment, Result, Coordination, MentionNotification, Role, Progress
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.core.exceptions import ObjectDoesNotExist

def send_password_email(email, password):
    """Функция отправки сгенерированного пароля на почту пользователя"""
    subject = "Ваш аккаунт создан"
    message = f"Здравствуйте!\n\nВаш аккаунт был успешно создан.\nВаш пароль: {password}\n\nПожалуйста, измените его при первой возможности."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", required=False)
    password = serializers.CharField(write_only=True, required=False)
    author = UserSerializer(read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['author', "name", "surname", "patronymic", "birthday", "work", "job", "personal", "photo", "email", "password", "status"]

    def get_status(self, obj):
        return "online" if obj.author.id in online_users else "offline"

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        email = user_data.get("email")
        password = validated_data.pop("password", None)

        if email:
            instance.user.email = email
            instance.user.save()

        if password:
            instance.user.set_password(password)
            instance.user.save()

        if "photo" in validated_data:
            instance.photo = validated_data["photo"]

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

def generate_password():
    """Генерация случайного пароля из 12 символов"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(12))


class ProfileCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, required=False)
    phone = serializers.CharField()

    class Meta:
        model = Profile
        fields = ['author', 'email', 'password', 'name', 'surname', 'phone']
        extra_kwargs = {'author': {'required': False}}  # Чтобы избежать ошибки валидации

    def create(self, validated_data):
        email = validated_data.pop("email")
        password = validated_data.pop("password", generate_password())
        name =  validated_data.pop("name")
        surname =  validated_data.pop("surname")
        phone = validated_data.pop("phone")

        # Проверяем, существует ли уже пользователь
        user, created = User.objects.get_or_create(
            username=email,
            defaults={"email": email, "password": password, "first_name": name, "last_name": surname}
        )

        if not created:
            raise serializers.ValidationError({"email": "Пользователь с таким email уже существует."})

        # Создаем или обновляем профиль
        profile, created = Profile.objects.get_or_create(author=user, defaults={"phone": phone, "name": name, "surname": surname})
        if not created:
            profile.phone = phone
            profile.name = name
            profile.surname = surname
            profile.save()

        # send_password_email(email, password)
        return profile

class CommentSerializer(serializers.ModelSerializer):
    task_id = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), source='task', required=False)
    owner_id = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all(), source='owner', required=False)
    recipient_id = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all(), source='recipient', required=False, allow_null=True)
    owner = ProfileSerializer(read_only=True)
    recipient = ProfileSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['task_id', 'owner_id','recipient_id', 'text', 'datetime', 'owner', 'recipient']


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
    coordinator = ProfileSerializer(read_only=True)
    class Meta:
        model = Coordination
        fields = ['task_id', 'coordinator_id', 'is_agreed', 'datetime', 'coordinator']
        
    def create(self, validated_data):
        # validated_data будет содержать объект Task, так как task_id преобразуется в task
        return Coordination.objects.create(**validated_data)

class TaskCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    file = serializers.FileField(required=False, allow_null=True)
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ['id','author', 'name', 'deadline', 'description', 'file', 'addressee', 'observers', 'coordinators', 'order']



class TaskSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    addressee = ProfileSerializer(read_only=True)
    coordination_set = CoordinationSerializer(many=True, read_only=True)
    comment_set = CommentSerializer(many=True, read_only=True)
    result = ResultSerializer(read_only=True)
    observer_set = ProfileSerializer(many=True, read_only=True, source='observers')
    coordinator_set = ProfileSerializer(many=True, read_only=True, source='coordinators')
    class Meta:
        model = Task
        fields = ['id','name', 'datetime', 'deadline', 'description', 'file', 'author', 'addressee', 'status',
                  'observers', 'coordinators', 'observer_set', 'is_agreed', 'coordinator_set', 'coordination_set',
                  'comment_set', 'result']


class RoleSerializer(serializers.ModelSerializer):
    worker = ProfileSerializer(read_only=True, source='profile')
    class Meta:
        model = Role
        fields = ['id', 'name', 'worker', 'profile', 'outlet']


class ProgressSerializer(serializers.ModelSerializer):

    author = ProfileSerializer(read_only=True)
    class Meta:
        model = Progress
        fields = ['id', 'task', 'datetime', 'author', 'record']

from rest_framework import serializers
from .models import MentionNotification

class MentionNotificationSerializer(serializers.ModelSerializer):
    comment_text = serializers.CharField(source="comment.text", read_only=True)
    task_id = serializers.IntegerField(source="comment.task.id", read_only=True)

    class Meta:
        model = MentionNotification
        fields = ['id', 'comment_text', 'task_id', 'is_accepted', 'created_at']
