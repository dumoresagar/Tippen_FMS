from django.urls import path
from .api import *


app_name = "agency"

urlpatterns = [
    path("create-agency/", PostAgencyAPIView.as_view(), name="create-agency"),
    path("department-list/", ListDepartmentAPIView.as_view(), name="department-list"),
    path("create-department/", PostDepartmentAPIView.as_view(), name="create-department"),
    path("department-user/<int:pk>/", DepartmentWiseUserListView.as_view(), name="department-user"),

    
]