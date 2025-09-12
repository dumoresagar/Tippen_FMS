from django.urls import path, include
from .api import (
    ProtoTypeLookUp, CustomLoginAPIView, RegisterAPIView, CustomPasswordChangeView, CustomPasswordResetView,
    CustomPasswordResetConfirmView,UpdateUserAPIView,RegisterAgencyUserAPIView,RegisterDistrictAdminAPIView,RegisterTalukaAdminAPIView,
)


app_name = "authentication"

urlpatterns = [
    path('init/', ProtoTypeLookUp.as_view(), name='init-rest'),

    path('login/', CustomLoginAPIView.as_view(), name='login-rest'),
    path('register/', RegisterAPIView.as_view(), name='register-rest'),
    path('register_agency_user/', RegisterAgencyUserAPIView.as_view(), name='register-agencyuser'),
    path('register_district_admin/', RegisterDistrictAdminAPIView.as_view(), name='register-dist-admin'),
    path('register_taluka_admin/', RegisterTalukaAdminAPIView.as_view(), name='register-taluka-admin'),
    path('update-user/<int:pk>/', UpdateUserAPIView.as_view(), name='register-rest'),


    path('change-password/', CustomPasswordChangeView.as_view(), name='change-password-reset'),
    path('forgot-password/', CustomPasswordResetView.as_view(), name='forgot-password-rest'),
    path('forgot-password/confirm/', CustomPasswordResetConfirmView.as_view(), name='forgot-password-confirm-rest'),
    
]



