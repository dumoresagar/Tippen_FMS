from django.urls import path, include
from .views import (HomePageView,ExperimentScript,CreateKumbhAssetGenericAPI,KumbhAssetGenericAPI,ListAssetAPIView,CreateAssetQuationAnswerGenericAPI,
                    GetAssetDetailsGenericAPI,list_media_documents)


app_name = "core"


urlpatterns = [
    path('', HomePageView.as_view(), name='core-home-page'),
    path('data-import/',ExperimentScript),
    path("asset-list/", ListAssetAPIView.as_view(), name="asset-list"),
    path("create-asset/", CreateKumbhAssetGenericAPI.as_view(), name="create-asset"),
    path("get-asset/<str:asset_code>/", GetAssetDetailsGenericAPI.as_view(), name="get-asset"),
    path("update-asset/<int:pk>/", KumbhAssetGenericAPI.as_view(), name="update-asset"),
    path("create-asset-quetion/", CreateAssetQuationAnswerGenericAPI.as_view(), name="create-asset-quetion"),
    path("get-asset-quetion/<int:pk>/", CreateAssetQuationAnswerGenericAPI.as_view(), name="get-asset-quetion"),

    path("documents/", list_media_documents, name="documents_list"),

]