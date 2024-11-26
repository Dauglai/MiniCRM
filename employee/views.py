from django.http import HttpResponseRedirect
from drf_yasg.utils import swagger_auto_schema

from .serializers import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import viewsets, generics, permissions, status, pagination
from .models import Task, Profile, Comment, Result, Coordination
from rest_framework.response import Response
from .permissions import *
from rest_framework.views import APIView
import datetime
from django.db.models import Q
from django_filters import rest_framework as filters
from .models import Task

class TaskFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    status = filters.CharFilter(field_name='status', lookup_expr='iexact')
    deadline = filters.DateFilter(field_name='deadline')
    author = filters.NumberFilter(field_name='author__id')  # фильтр по автору
    addressee = filters.NumberFilter(field_name='addressee__id')  # фильтр по ответственному
    created_after = filters.DateFilter(field_name='datetime', lookup_expr='gte')  # начальная дата
    created_before = filters.DateFilter(field_name='datetime', lookup_expr='lte')  # конечная дата
    task_id = filters.NumberFilter(field_name='id')  # фильтр по ID задачи

    class Meta:
        model = Task
        fields = ['name', 'status', 'deadline', 'author', 'addressee', 'created_after', 'created_before', 'task_id']



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
        role = self.request.query_params.get('role', 'author')  # Получаем роль из параметра запроса

        # Возвращаем задачи, где текущий пользователь
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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)

class TaskAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def retrieve(self, request, pk):
        task = Task.objects.get(pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def update(self, request, pk):
        task = Task.objects.get(pk=pk)
        serializer = TaskSerializer(task, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        task.coordination_set.all().delete()
        serializer.save(datetime=datetime.datetime.now(), status="На согласовании")
        return HttpResponseRedirect(redirect_to='/tasks/', status=status.HTTP_303_SEE_OTHER)


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


class ProfileAPIUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_object(self):
        # Возвращает профиль текущего пользователя
        return Profile.objects.get(author=self.request.user)


class ProfileAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileCreateSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class ResultAPIList(generics.ListCreateAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = (IsUsersInTaskOrReadOnly,)


class CommentAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrReadOnly,)

class CommentApiView(APIView):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        task = Task.objects.get(pk=pk)
        comment = Comment.objects.filter(task=task)
        return Response(CommentSerializer(comment, many=True).data)

    @swagger_auto_schema(request_body=CommentSerializer)
    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')  # ID задачи
        task = Task.objects.get(pk=pk)
        coordinators = task.coordinators.all()
        observers = task.observers.all()

        data = request.data.copy()
        data['task_id'] = task.id
        data['owner_id'] = request.user.id  # ID профиля владельца

        # Проверяем, имеет ли пользователь доступ к задаче
        if (
            task.addressee == request.user.profile or
            task.author == request.user.profile or
            request.user.profile in coordinators or
            request.user.profile in observers
        ):
            # Создаем сериализатор
            serializer = CommentSerializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            comment = serializer.save(datetime=datetime.datetime.now())
            # Обрабатываем упоминания
            if 'mentions' in data:
                mentions = Profile.objects.filter(id__in=data['mentions'])
                comment.mentions.set(mentions)
                # Создаем уведомления для каждого упомянутого пользователя
                for mentioned_user in mentions:
                    MentionNotification.objects.create(comment=comment, mentioned_user=mentioned_user)
            return Response({'message': 'Комментарий создан', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        # Если доступ запрещен
        return Response({'message': 'Вы не участвуете в работе над этой задачей'}, status=status.HTTP_400_BAD_REQUEST)


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
        if request.user.profile in coordinators:
            if coordination_set.filter(coordinator=request.user.profile).exists():
                return Response({'message': 'Задача уже была согласована вами'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = CoordinationSerializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(datetime=datetime.datetime.now())
            set_count = coordination_set.filter(is_agreed=True).count()
            count = coordinators.count()
            if count == set_count:
                task.status = "В работе"
                task.save()
            return Response({'message': 'Задача соглосованна.'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Вас нет в списке соглосователей.'}, status=status.HTTP_400_BAD_REQUEST)


