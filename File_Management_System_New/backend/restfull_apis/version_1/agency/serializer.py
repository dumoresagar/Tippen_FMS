from django.utils.translation import gettext as _
from rest_framework import serializers
from core.models import Document,District,Taluka,Village,Department
from users.models import User,Agency
from django.core.exceptions import ValidationError


class AgencySerialzier(serializers.ModelSerializer):

    class Meta:
        model = Agency
        fields = "__all__"

class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = "__all__"


class UserListSerializer(serializers.ModelSerializer):
    user_role = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id','username','user_role']
    
    def get_user_role(self,obj):
        if obj and obj.user_role:
            return obj.user_role.role_name
        else:
            return None