from django.contrib.auth.models import User
from django.db import models

from catalog.models import Outlet, Order


class Profile(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, db_index=True)
    photo = models.ImageField(blank=True, default='profile_pics/default.png', upload_to='profile_pics')
    surname = models.CharField(verbose_name="Фамилия", max_length=100, db_index=True)
    name = models.CharField(verbose_name="Имя", max_length=100, db_index=True)
    patronymic = models.CharField(verbose_name="Отчество", max_length=100, null=True, blank=True, db_index=True)
    birthday = models.DateField(verbose_name="Дата рождения", null=True, blank=True, db_index=True)
    job = models.CharField(verbose_name="Должность", default='Продавец', max_length=100, db_index=True)
    personal = models.CharField(verbose_name="Личный телефон", max_length=100, db_index=True)
    work = models.CharField(verbose_name="Рабочий телефон", max_length=100, db_index=True)

    def __str__(self):
        return f'{self.surname} {self.name} {self.patronymic}'


class Task(models.Model):
    STATUS_CHOISES = (
        ("На согласовании", "На согласовании"),
        ("В работе", "В работе"),
        ("Выполнена", "Выполнена"),
        ("Завершена", "Завершена"),
        ("Отменена", "Отменена"))

    name = models.CharField(verbose_name="Название задачи", max_length=255)
    datetime = models.DateTimeField(verbose_name="Время создания", auto_now=True)
    deadline = models.DateField(verbose_name="Ожидаемый срок выполнения")
    description = models.TextField(verbose_name="Описание", max_length=10000)
    file = models.FileField(verbose_name="Файлы", blank=True, upload_to="tasks/")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    author = models.ForeignKey(Profile, verbose_name="Автор", on_delete=models.CASCADE)
    addressee = models.ForeignKey(Profile, related_name="addressee", on_delete=models.CASCADE)
    status = models.CharField(verbose_name="Название роли", choices=STATUS_CHOISES, default='На согласовании', max_length=100)
    observers = models.ManyToManyField(Profile, related_name="observers", blank=True)
    is_agreed = models.BooleanField(verbose_name="Завершена", default=False)
    coordinators = models.ManyToManyField(Profile, related_name="coordinators", blank=True)

    def __str__(self):
        return self.name


class Coordination(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    is_agreed = models.BooleanField(verbose_name="Согласовано", default=False)
    coordinator = models.ForeignKey(Profile, verbose_name="Автор", on_delete=models.CASCADE)
    datetime = models.DateTimeField(verbose_name="Время создания", auto_now=True)


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Комментарий")
    recipient = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True,
                                  related_name="private_comments")  # Поле для приватных комментариев
    datetime = models.DateTimeField(verbose_name="Время создания", auto_now=True)


class MentionNotification(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    mentioned_user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Упоминание {self.mentioned_user} в комментарии {self.comment.id}"


class Result(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    is_end = models.BooleanField(verbose_name="Выполнена", default=False)
    description = models.TextField(verbose_name="Описание", max_length=10000)
    file = models.FileField(verbose_name="Файлы", blank=True, null=True)

class Role(models.Model):
    Role_CHOISES = (
        ("Продавец", "Продавец"),
        ("Администратор", "Администратор"))

    name = models.CharField(verbose_name="Название роли", choices=Role_CHOISES, default='Продавец', max_length=100)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="worker")
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE, related_name="outletInfo")

    def __str__(self):
        return f"{self.profile.name} - {self.name} ({self.outlet.name})"


class Progress(models.Model):
    RECORD_CHOISES = (
        ("Соглосование", "Задача соглосована"),
        ("Результат", "Реузльтат предоставлен"),
        ("Рассмотрение", "Задача изменена и подана на рассмотрение"),
        ("Завершение", "Задача завершена"),
    )


    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    record = models.CharField(verbose_name="Запись", choices=RECORD_CHOISES, max_length=100)
    datetime = models.DateTimeField(auto_now_add=True)
