from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    ROLE_CHOISES = (
        ("Собственник", "Собственник"),
        ("Администратор", "Администратор"),
        ("Продавец", "Продавец"))

    author = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    photo = models.ImageField(blank=True, null=True)
    surname = models.CharField(verbose_name="Фамилия", max_length=100)
    name = models.CharField(verbose_name="Имя", max_length=100)
    patronymic = models.CharField(verbose_name="Отчество", max_length=100, null=True, blank=True)
    birthday = models.DateField(verbose_name="Дата рождения", null=True, blank=True)
    role = models.CharField(verbose_name="Название роли", choices=ROLE_CHOISES, default='Продавец', max_length=100)
    personal = models.CharField(verbose_name="Личный телефон", max_length=10)
    work = models.CharField(verbose_name="Рабочий телефон", max_length=10)

    def __str__(self):
        return f'{self.surname} {self.name} {self.patronymic}'


class Topic(models.Model):
    name = models.CharField(verbose_name="Название темы", max_length=255)

    def __str__(self):
        return self.name



class Task(models.Model):
    STATUS_CHOISES = (
        ("На согласовании", "На согласовании"),
        ("В работе", "В работе"),
        ("Выполнена", "Выполнена"),
        ("Завершена", "Завершена"),
        ("Отменена", "Отменена"))

    name = models.CharField(verbose_name="Название задачи", max_length=255)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    datetime = models.DateTimeField(verbose_name="Время создания", auto_now=True)
    deadline = models.DateField(verbose_name="Ожидаемый срок выполнения")
    description = models.TextField(verbose_name="Описание", max_length=10000)
    file = models.FileField(verbose_name="Файлы", null=True, blank=True)
    author = models.ForeignKey(User, verbose_name="Автор", on_delete=models.CASCADE)
    addressee = models.ForeignKey(User, related_name="addressee", on_delete=models.CASCADE, null=True)
    status = models.CharField(verbose_name="Название роли", choices=STATUS_CHOISES, default='На согласовании', max_length=100)
    observers = models.ManyToManyField(User, related_name="observers", blank=True)
    is_agreed = models.BooleanField(verbose_name="Завершена", default=False)
    coordinators = models.ManyToManyField(User, related_name="coordinators", blank=True)

    def __str__(self):
        return self.name


class Coordination(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    is_agreed = models.BooleanField(verbose_name="Согласовано", default=False)
    coordinator = models.ForeignKey(User, verbose_name="Автор", on_delete=models.CASCADE)
    datetime = models.DateTimeField(verbose_name="Время создания", auto_now=True)


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Комментарий")
    datetime = models.DateTimeField(verbose_name="Время создания", auto_now=True)


class Result(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_end = models.BooleanField(verbose_name="Выполнена", default=False)
    description = models.TextField(verbose_name="Описание", max_length=10000)
    file = models.FileField(verbose_name="Файлы")
