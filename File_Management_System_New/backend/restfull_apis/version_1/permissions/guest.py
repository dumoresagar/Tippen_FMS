from django.conf import settings
from rest_framework.permissions import BasePermission

class IsTrustedGuest(BasePermission):

    allowed_methods = ["POST", "GET"]

    def has_permission(self, request, view):
        guest_token = request.META.get("HTTP_GUEST_TOKEN", None)

        if guest_token and guest_token == settings.GUEST_TOKEN:
            return request.method in self.allowed_methods

        if request.user.is_superuser:
            return request.method in self.allowed_methods

        return False