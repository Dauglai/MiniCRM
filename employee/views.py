import re
from django.http import HttpResponseRedirect
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from rest_framework import viewsets, generics, permissions, status, pagination
from .models import Task, Profile, Comment, Result, Coordination, Progress
from rest_framework.response import Response
from .permissions import *
from rest_framework.views import APIView
import datetime
from django.db.models import Q
from django_filters import rest_framework as filters
from .models import Task
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from .consumers import online_users

User = get_user_model()

@api_view(["GET"])
def get_online_status(request):
    users = User.objects.all()
    data = [
        {"id": user.id, "name": user.get_full_name(), "status": "online" if user.id in online_users else "offline"}
        for user in users
    ]
    return Response(data)


class ProfileSearchAPIView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name', 'surname', 'status', 'id', 'author__surname', 'addressee__surname', 'outlet__name']


class TaskFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    status = filters.CharFilter(field_name='status', lookup_expr='iexact')
    deadline = filters.DateFilter(field_name='deadline')
    author = filters.NumberFilter(field_name='author__id')
    addressee = filters.NumberFilter(field_name='addressee__id')
    created_after = filters.DateFilter(field_name='datetime', lookup_expr='gte')
    created_before = filters.DateFilter(field_name='datetime', lookup_expr='lte')
    task_id = filters.NumberFilter(field_name='id')
    orderId = filters.NumberFilter(field_name='order__id')

    class Meta:
        model = Task
        fields = ['name', 'status', 'deadline', 'author', 'addressee', 'created_after', 'created_before', 'task_id', 'orderId']



class TaskAPIListPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class TaskAPIList(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = TaskAPIListPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = TaskFilter


    def get_queryset(self):
        user = self.request.user
        role = self.request.query_params.get('role', 'author')

        if role == 'addressee':
            return Task.objects.filter(addressee=user.profile).order_by('id')
        if role == 'author':
            return Task.objects.filter(author=user.profile).order_by('id')
        if role == 'coordinator':
            return Task.objects.filter(coordinators=user.profile).order_by('id')
        if role == 'observer':
            return Task.objects.filter(observers=user.profile).order_by('id')
        return Task.objects.filter(
            Q(addressee=user.profile) |
            Q(coordinators=user.profile) |
            Q(author=user.profile) |
            Q(observers=user.profile)
        ).distinct().order_by('id')


class TaskAPICreate(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)

class TaskAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    http_method_names = ['get', 'put', 'patch']


    def retrieve(self, request, pk):
        task = Task.objects.get(pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def update(self, request, pk, partial=False):
        task = Task.objects.get(pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)

        is_agreed = request.data.get('is_agreed', None)

        if task.status == "Отменена":
            task.coordination_set.all().delete()
            serializer.save(datetime=datetime.datetime.now(), status="На согласовании")
            Progress.objects.create(task=task, author=request.user.profile, record="Рассмотрение")
        elif task.status == "Выполнена" and is_agreed:
            serializer.save(datetime=datetime.datetime.now(), status="Завершена")
            Progress.objects.create(task=task, author=request.user.profile, record="Завершение")
        else:
            serializer.save(datetime=datetime.datetime.now())

        Progress.objects.create(task=task, author=request.user.profile, record="Изменение задачи")

        return Response({'message': 'Принято', 'data': serializer.data}, status=status.HTTP_201_CREATED)


class ProfileAPIList(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        # Возвращает профиль текущего пользователя
        return Profile.objects.filter(author=self.request.user)


class ProfileAPICreate(generics.CreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileCreateSerializer
    permission_classes = (IsAuthenticated, )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)


class ProfileAPIUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_object(self):
        return Profile.objects.get(author=self.request.user)


class ProfileAnyAPIUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAdminUser,)


class CommentAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrReadOnly,)

class CommentApiView(APIView):
    def get(self, request,*args, **kwargs):
        pk = kwargs.get('pk')
        task = Task.objects.get(pk=pk)
        comments = Comment.objects.filter(task=task).filter(
            Q(recipient__isnull=True) | Q(recipient=request.user.profile) | Q(owner=request.user.profile))

        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)



    @swagger_auto_schema(request_body=CommentSerializer)
    def post(self, request, *args, **kwargs):
        print("Полученные данные:", request.data)
        pk = kwargs.get('pk')
        task = Task.objects.get(pk=pk)
        data = request.data.copy()
        data['task_id'] = task.id
        data['owner_id'] = request.user.id

        if self.has_access(request.user.profile, task):
            serializer = CommentSerializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            print("Валидные данные:", serializer.validated_data)  # Должен быть recipient_id
            comment = serializer.save(datetime=datetime.datetime.now())
            if comment.recipient:
                MentionNotification.objects.create(mentioned_user=comment.recipient, comment=comment)

            return Response({'message': 'Комментарий создан', 'data': serializer.data}, status=status.HTTP_201_CREATED)

        return Response({'message': 'Доступ запрещен'}, status=status.HTTP_204_NO_CONTENT)

    def has_access(self, profile, task):
        return (
                task.addressee == profile or
                task.author == profile or
                profile in task.coordinators.all() or
                profile in task.observers.all()
        )


class MentionNotificationUpdateView(APIView):
    def post(self, request, notif_id):
        notif = MentionNotification.objects.get(id=notif_id)
        action = request.data.get('action')

        if action == 'accept':
            notif.is_accepted = True
        elif action == 'dismiss':
            notif.is_accepted = False
        notif.is_viewed = True
        notif.save()

        return Response({'status': 'updated'})

class CoordinationApiView(APIView):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        task = Task.objects.get(pk=pk)
        coordination = Coordination.objects.filter(task=task)
        return Response(CoordinationSerializer(coordination, many=True).data)

    @swagger_auto_schema(request_body=CoordinationSerializer)
    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        task = Task.objects.get(pk=pk)
        coordination_set = task.coordination_set
        coordinators = task.coordinators.all()
        data = request.data.copy()
        data['task_id'] = task.id
        data['coordinator_id'] = request.user.id
        is_agreed = data['is_agreed']
        if request.user.profile in coordinators:
            if coordination_set.filter(coordinator=request.user.profile).exists():
                return Response({'message': 'Задача уже была согласована вами'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = CoordinationSerializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(datetime=datetime.datetime.now())
            set_count = coordination_set.filter(is_agreed=True).count()
            count = coordinators.count()
            Progress.objects.create(task=task, author=request.user.profile, record="Согласование")
            if is_agreed == False:
                task.status = "Отменена"
                task.save()
            if count == set_count:
                task.status = "В работе"
                task.save()
            return Response({'message': 'Задача соглосованна.'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Вас нет в списке соглосователей.'}, status=status.HTTP_400_BAD_REQUEST)


class RoleAPIListCreate(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['outlet']


class RoleAPIUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = (IsAuthenticated,)


class ProgressListApi(APIView):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        task = Task.objects.get(pk=pk)
        progress = Progress.objects.filter(task=task)
        return Response(ProgressSerializer(progress, many=True).data)


class ResultAPIList(APIView):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        task = Task.objects.get(pk=pk)
        progress = Result.objects.filter(task=task)
        return Response(ResultSerializer(progress, many=True).data)

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        task = Task.objects.get(pk=pk)
        data = request.data.copy()
        if task.addressee == request.user.profile:
            serializer = ResultSerializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            Progress.objects.create(task=task, author=request.user.profile, record="Реузльтат")
            task.status = "Выполнена"
            task.save()
            return Response({'message': 'Резульат предоставлен.'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Вас нет в списке соглосователей.'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        task = Task.objects.get(pk=pk)
        try:
            result = Result.objects.get(task=task)
        except Result.DoesNotExist:
            return Response({'message': 'Результат не найден'}, status=status.HTTP_404_NOT_FOUND)

        if task.adresse == request.user.profile:
            serializer = ResultSerializer(result, data=request.data, partial=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            task.status = "Выполнена"
            task.save()
            Progress.objects.create(task=task, author=request.user.profile, record="Результат обновлен")
            return Response({'message': 'Результат обновлен.', 'data': serializer.data}, status=status.HTTP_200_OK)

        return Response({'message': 'Вы не можете изменить результат.'}, status=status.HTTP_403_FORBIDDEN)


class MentionNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = MentionNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MentionNotification.objects.filter(mentioned_user=self.request.user.profile, is_accepted=False)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_accepted = True
        instance.save()
        return Response({"message": "Уведомление помечено как прочитанное"}, status=status.HTTP_200_OK)