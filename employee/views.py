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
from django_filters import rest_framework as filters
from django.db.models import Q


class TaskFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    status = filters.CharFilter(field_name='status', lookup_expr='iexact')
    deadline = filters.DateFilter(field_name='deadline')

    class Meta:
        model = Task
        fields = ['name', 'status', 'deadline']


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

        # Возвращаем задачи, где текущий пользователь - автор или адресат, в зависимости от роли
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
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, )


class ProfileAPICreate(generics.CreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileCreateSerializer
    permission_classes = (IsAuthenticated, )


class ProfileAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthorOrReadOnly,)

class ProfileAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileCreateSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class ResultAPIList(generics.ListCreateAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = (IsUsersInTaskOrReadOnly,)


class ResultAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class ResultAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class CommentApiList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsUsersInTaskOrReadOnly,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        task = Task.objects.get(pk=pk)
        serializer = CommentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task.id, datetime=datetime.datetime.now())
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        pk = kwargs.get('pk')
        task = Task.objects.get(pk=pk)
        coordinators = task.coordinators.all()
        observers = task.observers.all()
        data = request.data.copy()
        data['task_id'] = task.id
        data['owner_id'] = request.user.id
        if task.addressee == request.user or task.author == request.user or request.user in coordinators or request.user in observers:
            serializer = CommentSerializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(datetime=datetime.datetime.now())
            return Response({'message': 'Коментаррий создан'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Вы не участвуете в работе над этой задачей'}, status=status.HTTP_400_BAD_REQUEST)


class CoordinationApiView(APIView):
    def get(self, request):
        coordination = Coordination.objects.all()
        return Response(CoordinationSerializer(coordination, many=True).data)

    @swagger_auto_schema(request_body=CoordinationSerializer)
    def post(self, request):
        pk = request.data['task']
        task = Task.objects.get(pk=pk)
        coordination_set = task.coordination_set
        coordinators = task.coordinators.all()
        if request.user in coordinators:
            if coordination_set.filter(coordinator=request.user).exists():
                return Response({'message': 'Задача уже была согласована вами'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = CoordinationSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(datetime=datetime.datetime.now(), coordinator=request.user, task=task)
            set_count = coordination_set.filter(is_agreed=True).count()
            count = coordinators.count()
            if count == set_count:
                task.status = "В работе"
                task.save()
            return Response({'message': 'Задача соглосованна.'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Вас нет в списке соглосователей.'}, status=status.HTTP_400_BAD_REQUEST)


