from rest_framework import permissions

from employee.models import Task, Comment, Result


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.owner == request.user

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user


class IsAddresseeOrReadonly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.Addressee == request.user


class IsUsersInTaskOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Разрешить безопасные методы (GET, HEAD или OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Проверяем права для объектов типа Task
        if isinstance(obj, Task):
            return obj.addressee == request.user or obj.author == request.user

        # Проверяем права для объектов типа Comment
        if isinstance(obj, Comment):
            task = obj.task  # Получаем задачу, к которой привязан комментарий
            return task.addressee == request.user or task.author == request.user

        if isinstance(obj, Result):
            task = obj.task  # Получаем задачу, к которой привязан комментарий
            return task.addressee == request.user or task.author == request.user

        return False