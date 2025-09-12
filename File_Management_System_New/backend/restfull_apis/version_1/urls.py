from django.urls import path, include
from .authentication import urls as authentication_urls
from .users import urls as users_urls
from .location import urls as location_urls
from .document import urls as document_urls
from .dashboard import urls as dashboard_urls
from .agency import urls as agency_urls

app_name = "v1"

urlpatterns = [
    path("authentication/", include(authentication_urls), name='authentication'),
    path("users/", include(users_urls), name='users'),
    path("location/", include(location_urls), name='location'),
    path("document/",include(document_urls), name="document"),
    path("dashboard/",include(dashboard_urls), name="dashboard"),
    path("agency/",include(agency_urls),name ='agency')
]
