# my_app/permissions.py

from rest_framework.permissions import BasePermission

from my_auth.authentication import CustomTokenAuthentication


class IsLogined(BasePermission):
    def has_permission(self, request, view):
        # Your custom permission logic here
        return CustomTokenAuthentication.authenticate(self,request)
