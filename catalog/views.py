import openpyxl
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse

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
    permission_classes = (IsAuthenticated,)


class OutletAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Outlet.objects.all()
    serializer_class = OutletSerializer
    permission_classes = (IsAuthenticated,)


class ProductAPIListCreate(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['group']

 
class ProductAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)


class ProductAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)


class OrderAPIListCreate(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)


class OrderAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)


class ClientAPIListCreate(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = (IsAuthenticated,)


class ClientAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = (IsAuthenticated,)


class ClientAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = (IsAuthenticated,)


class GroupAPIListCreate(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class GroupAPIUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer



class ProductImportExportView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        """Импорт продуктов из Excel файла"""
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "Файл не предоставлен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active

            for row in sheet.iter_rows(min_row=2, values_only=True):
                group_name, name, price, count, article, description = row
                group, _ = Group.objects.get_or_create(name=group_name)
                Product.objects.create(
                    article=article,
                    group=group,
                    name=name,
                    price=price,
                    count=count,
                    description=description
                )

            return Response({"message": "Продукты успешно импортированы"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



    def get(self, request):
        """Экспорт продуктов в Excel файл"""
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(["Группа", "Название", "Цена", "Количество", "Артикул", "Описание"])

        products = Product.objects.select_related('group').all()
        for product in products:
            sheet.append([
                product.group.name,
                product.name,
                product.price,
                product.count,
                product.article,
                product.description,
            ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=products.xlsx'

        # Save workbook to response
        workbook.save(response)  # Important: Save workbook directly to the HttpResponse object
        return response
