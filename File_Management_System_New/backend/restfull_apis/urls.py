from django.urls import path, include
from .version_0 import urls as version_0_urls
from .version_1 import urls as version_1_urls
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


app_name = "api"

schema_view = get_schema_view(
   openapi.Info(
      title="",
      default_version='',
      description="",
      terms_of_service="",
      contact=openapi.Contact(email=""),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path("version_0/", include(version_0_urls), name="v0"),
    path("version_1/", include(version_1_urls), name="v1"),
    path('document/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("swagger/", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
