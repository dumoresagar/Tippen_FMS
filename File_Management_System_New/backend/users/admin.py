from django.contrib import admin
from users.models import (User,Role,Agency,TeamMaster)
from .forms import UserCreationForm
from import_export.admin import ImportExportModelAdmin
from django import forms
from rest_framework.authtoken.models import Token

class UserAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form = UserCreationForm
    list_display = [
        'id', 'username', 'email','agency',
        'date_created', 'date_updated', 'active_status','is_deleted',  
    ]
    list_display_links=['id','username']
    exclude = ['peram_group']


class AgencyAdminForm(forms.ModelForm):

    class Meta:
        model = Agency
        fields = "__all__"


class AgencyAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form =AgencyAdminForm 
    list_display = [
        "agency_name",
        "address",
        "mobile_number",
        'aadhar_no',
        'active_status'
    ]

class RoleAdminForm(forms.ModelForm):

    class Meta:
        model = Role
        fields = "__all__"


class RoleAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form =RoleAdminForm 
    list_display = [
        "role_name",
    ]

class TeamMasterAdminForm(forms.ModelForm):

    class Meta:
        model = TeamMaster
        fields = "__all__"


class TeamMasterAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form =TeamMasterAdminForm 
    list_display = [
        "id",
        "team_name",
    ]

class TokenAdminForm(forms.ModelForm):

    class Meta:
        model = Token
        fields = "__all__"


class TokenAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form =TokenAdminForm 
    list_display = [
        "key",
        "user"
    ]


admin.site.register(User,UserAdmin)
admin.site.register(Role,RoleAdmin)
admin.site.register(Agency,AgencyAdmin)
admin.site.register(TeamMaster,TeamMasterAdmin)
admin.site.register(Token,TokenAdmin)