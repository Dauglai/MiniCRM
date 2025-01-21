from rest_framework.permissions import IsAuthenticated

from employee.permissions import IsAuthorOrReadOnly
from .models import Product, Group
from rest_framework import viewsets, generics, permissions, status
from .models import *
from.serializers import *


class OutletAPIListCreate(generics.ListCreateAPIView):
    queryset = Outlet.objects.all()
    serializer_class = OutletSerializer
    permission_classes = (IsAuthenticated,)


class OutletAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Outlet.objects.all()
    serializer_class = OutletSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class OutletAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Outlet.objects.all()
    serializer_class = OutletSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class ProductAPIListCreate(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)

 
class ProductAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class ProductAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class OrderAPIListCreate(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)


class OrderAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class ClientAPIListCreate(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = (IsAuthenticated,)


class ClientAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class ClientAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = (IsAuthorOrReadOnly,)