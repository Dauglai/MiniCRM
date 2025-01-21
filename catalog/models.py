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

class Outlet(models.Model):
    name = models.CharField(max_length=256)
    address = models.CharField(max_length=1000)

    def __str__(self):
        return self.name


class Client(models.Model):
    surname = models.CharField(verbose_name="Фамилия", max_length=100, db_index=True)
    name = models.CharField(verbose_name="Имя", max_length=100, db_index=True)
    patronymic = models.CharField(verbose_name="Отчество", max_length=100, null=True, blank=True, db_index=True)
    address = models.CharField(max_length=1000)

    def __str__(self):
        return self.name

class Order(models.Model):
    product = models.ManyToManyField(Product, related_name='orders')
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(max_length=1000)

    def __str__(self):
        return self.product.name
