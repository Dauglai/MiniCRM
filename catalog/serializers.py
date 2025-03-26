from rest_framework import serializers
from .models import Product, Group, Outlet, Client, Order


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    group_name = serializers.ReadOnlyField(source='group.name')

    class Meta:
        model = Product
        fields = ['id', 'group', 'group_name', 'name', 'price', 'count', 'article', 'description']


class OutletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outlet
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

from rest_framework import serializers
from .models import Order, OrderItem, Product

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'name']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    task = serializers.SerializerMethodField(read_only=True)
    client_info = ClientSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'outlet', 'description', 'items', 'task', 'client', 'client_info']

    def get_task(self, obj):
        from employee.serializers import TaskSerializer
        from employee.models import Task

        task = Task.objects.filter(order=obj.id).first()
        return TaskSerializer(task).data if task else None

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            if product.count < quantity:
                raise serializers.ValidationError(f"Недостаточно товара {product.name}, в наличии {product.count}")

            # Вычитаем количество товара
            product.count -= quantity
            product.save()

            # Создаем OrderItem
            OrderItem.objects.create(order=order, product=product, quantity=quantity)

        return order