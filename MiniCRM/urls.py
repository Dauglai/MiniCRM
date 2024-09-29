from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from employee.views import *
from rest_framework import routers

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,)
)

router = routers.SimpleRouter()
router.register(r'topic', TopicViewSet)
router.register(r'comment', CommentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/v1/', include(router.urls)),
    path('accounts/profile/', ProfileAPIList.as_view()),
    path('profile/<int:pk>/', ProfileAPIUpdate.as_view()),
    path('profiledelete/<int:pk>/', ProfileAPIDestroy.as_view()),
    path('task/', TaskAPIList.as_view()),
    path('task/<int:pk>/', TaskAPIUpdate.as_view()),
    path('coordination/', CoordinationApiView.as_view()),
    path('result/', ResultAPIList.as_view()),
    path('result/<int:pk>/', ResultAPIUpdate.as_view()),
    path('resultdelete/<int:pk>/', ResultAPIDestroy.as_view()),
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)