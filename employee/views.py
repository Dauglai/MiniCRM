from datetime import timezone

from django.shortcuts import render, get_object_or_404
from drf_yasg.utils import swagger_auto_schema

from .serializers import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import viewsets, generics, permissions, status
from .models import Task, Topic, Profile, Comment, Result, Coordination
from rest_framework.response import Response
from .permissions import IsAuthorOrReadOnly, IsAddresseeOrReadonly
from rest_framework.views import APIView
import datetime


class TaskAPIList(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)


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
        return Response(serializer.data)


class ProfileAPIList(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, )


class ProfileAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthorOrReadOnly,)

class ProfileAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class ResultAPIList(generics.ListCreateAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = (IsAuthenticated,)


class ResultAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class ResultAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class CommentApiView(APIView):
    def get(self, request):
        coordination = Comment.objects.all()
        return Response(CommentSerializer(coordination, many=True).data)

    @swagger_auto_schema(request_body=CommentSerializer)
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
            serializer.save(datetime=datetime.datetime.now())
            set_count = coordination_set.filter(is_agreed=True).count()
            count = coordinators.count()
            if count == set_count:
                task.status = "В работе"
                task.save()
            return Response({'message': 'Задача соглосованна.'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Вас нет в списке соглосователей.'}, status=status.HTTP_400_BAD_REQUEST)

class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = (IsAuthenticated,)


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
            serializer.save(datetime=datetime.datetime.now())
            set_count = coordination_set.filter(is_agreed=True).count()
            count = coordinators.count()
            if count == set_count:
                task.status = "В работе"
                task.save()
            return Response({'message': 'Задача соглосованна.'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Вас нет в списке соглосователей.'}, status=status.HTTP_400_BAD_REQUEST)


