from django.db import models


class Group(models.Model):
    name = models.CharField(verbose_name="Название группы", max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Название группы", max_length=100)
    price = models.IntegerField(verbose_name="Цена за штуку")
    count = models.PositiveIntegerField(verbose_name="Количество")
    article = models.IntegerField(verbose_name="Артикул")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.name


