from django.contrib import admin
from .models import Product, Group,  Client, Order, Outlet

admin.site.register(Product)
admin.site.register(Group)
admin.site.register(Client)
admin.site.register(Order)
admin.site.register(Outlet)

# Register your models here.
