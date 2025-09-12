from django.urls import path, include
from .api import (ProfileDetailsAPI, UpdateProfileAPI,AdminLoginAPI,AdminLogoutAPI,ChangePasswordView,SendPasswordResetEmailView,UserPasswordResetView,UserProfileDetailsAPI,CreateUserAPI,LogoutAPI,LogoutAllUsersExceptSuperAdminAPI
                )
from rest_framework.authtoken import views


app_name = "users"

urlpatterns = [
    path('api-token-auth/', views.obtain_auth_token),
    # path('admin-login/',AdminLogin,name='admin-login'),
    path("admin-login/", AdminLoginAPI.as_view(), name="admin-login"),
    path("logout/",LogoutAPI.as_view(),name = 'admin-logout'),
    path('api/logout-all-except-superadmin/', LogoutAllUsersExceptSuperAdminAPI.as_view(), name='logout-all-except-superadmin'),

    path("user_profile_details/", UserProfileDetailsAPI.as_view()),
    path("admin-logout/",AdminLogoutAPI.as_view(),name = 'admin-logout'),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),


    path("profile-details/", ProfileDetailsAPI.as_view(), name="profile-details-rest"),
    path("profile-update/", UpdateProfileAPI.as_view(), name="profile-update-rest"),

    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
    path('create_user/',CreateUserAPI.as_view())
]