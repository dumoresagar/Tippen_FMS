from django.urls import path
from .api import *


app_name = "dashboard"

urlpatterns = [
    path("dashboard-count/", DashboardView.as_view(), name="dashboard-count"),
    path("rectify-list/", RectifyDocumentListView.as_view(), name="rectify-list"),
    path("district-wise-count/", DistrictWiseDashboardView.as_view(), name="district-wise-count"),
    path("user-pagination-update/<int:pk>/", UserPaginationUpdateGenericAPI.as_view(), name="user-pagination-update"),
    path("user-wise-count/", UserWiseDocumentListAPI.as_view(), name="user-wise-count"),
    path("taluka-wise-count/<str:district_code>/", TalukaWiseDashboardView.as_view(), name="taluka-wise-count"),
    path("village-wise-count/<str:taluka_code>/", VillageWiseDashboardView.as_view(), name="taluka-wise-count"),
    path("maptype-wise-count/", MapTypeWiseDashboardView.as_view(), name="maptype-wise-count"),
    path("village-wise-maptype/<str:village_code>/", VillageWiseMapTypeDashboardView.as_view(), name="village-wise-maptype"),
    path("agency-wise-count/", AgencyWiseWiseDashboardView.as_view(), name="agency-wise-count"),

    path("today-maptype-wise-count/", TodayMapTypeWiseDocView.as_view(), name="today-maptype-wise-count"),

]