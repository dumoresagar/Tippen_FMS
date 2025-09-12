from django.urls import path, include
from .views import (HomePageView,ExperimentScript,list_media_documents)


app_name = "core"


urlpatterns = [
    path('', HomePageView.as_view(), name='core-home-page'),
    path('data-import/',ExperimentScript),


    path("documents/", list_media_documents, name="documents_list"),

]