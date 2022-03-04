# rest framework
from rest_framework.permissions import BasePermission

# импорты приложений
from accounts.choices import SERVICE_PACKAGES


class MediumSubscribePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        elif request.user.service_package == SERVICE_PACKAGES[1]:
            return True
        return False


class PremiumSubscribePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        elif request.user.service_package == SERVICE_PACKAGES[2]:
            return True
        return False
