from rest_framework.permissions import BasePermission

class DistrictPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST' and request.user.user_role.filter(role_name='Agency Admin').exists():
            return True
        elif request.method == 'GET' and request.user.user_role.filter(role_name='Agency Admin').exists():
            return True
        elif request.method == 'PUT' and request.user.user_role.filter(role_name='Agency Admin').exists():
            return True
        elif request.method == 'DELETE' and request.user.user_role.filter(role_name='Agency Admin').exists():
            return True
        return False