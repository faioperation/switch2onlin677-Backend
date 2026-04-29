from rest_framework import permissions
from django.conf import settings

class IsAIBotOrAdmin(permissions.BasePermission):
    """
    Allows access to AI Bot via API Key or to Admin users.
    """
    def has_permission(self, request, view):
        # 1. Check if it's an Admin user (standard JWT auth)
        if request.user and request.user.is_staff:
            return True
        
        # 2. Check for the Secret API Key in headers (for AI Bot)
        api_key = request.headers.get("X-Api-Key")
        expected_key = getattr(settings, "LEADS_API_KEY", None)
        
        if api_key and expected_key and api_key == expected_key:
            return True
            
        return False
