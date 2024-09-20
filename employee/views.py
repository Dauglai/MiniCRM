from django.shortcuts import render
from .serializers import TaskSerializer, StatusSerializer, ProfileSerializer, TopicSerializer, ResultSerializer, \
    CommentSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import viewsets, generics, permissions
from .models import Task, Topic, Profile, Comment, Result

class TaskAPIList(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class TaskAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)


class TaskAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)


class ProfileAPIList(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class ProfileAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)


class ProfileAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = (IsAuthenticated,)

class ResultAPIList(generics.ListCreateAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class ResultAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = (IsAuthenticated,)


class ResultAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = (IsAuthenticated,)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)