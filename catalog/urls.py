from django.urls import path, include
from rest_framework import routers

from employee.utils import download_employee_report
from .views import *

router = routers.SimpleRouter()


urlpatterns = [
    path('', include(router.urls)),
    path('orders/', OrderAPIList.as_view()),
    path('orders/create/', OrderAPICreate.as_view()),
    path('orders/<int:pk>/', OrderAPIUpdate.as_view()),
    path('outlets/', OutletAPIListCreate.as_view()),
    path('outlets/<int:pk>/', OutletAPIUpdate.as_view()),
    path('outlets_delete/<int:pk>/', OutletAPIDestroy.as_view()),
    path('products/', ProductAPIListCreate.as_view()),
    path('products/<int:pk>/', ProductAPIUpdate.as_view()),
    path('products_delete/<int:pk>/', ProductAPIDestroy.as_view()),
    path('clients/', ClientAPIListCreate.as_view()),
    path('clients/<int:pk>/', ClientAPIUpdate.as_view()),
    path('clients_delete/<int:pk>/', ClientAPIDestroy.as_view()),
    path('groups/', GroupAPIListCreate.as_view(), name='group-list-create'),
    path('groups/<int:pk>/', GroupAPIUpdateDestroy.as_view(), name='group-update-destroy'),
    path('products/import-export/', ProductImportExportView.as_view(), name='product-import-export'),
    path("analytics/download/", download_employee_report, name="download-employee-report"),


]