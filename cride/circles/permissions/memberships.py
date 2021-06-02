"""Membership permissions."""

# DRF
from rest_framework.permissions import BasePermission

# models
from cride.circles.models import Membership

class IsActiveCircleMember(BasePermission):
    """Circle member is active user.
    
    Expect that the views implementing this permission 
    have a `circle` attribute assigned."""

    def has_permission(self, request, view):
        """Verify user is an active member of the circle."""
        try:
            Membership.objects.get(
                user=request.user,
                circle=view.circle,
                is_active=True,
            )
        except Membership.DoesNotExist:
            return False
        return True

class IsSelfMember(BasePermission):
    """Allow access only to member owners."""

    def has_permission(self, request, view):
        """Let object permission grant access."""
        obj = view.get_object()
        return self.has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        """Allow access only if member is owned by the requesting user."""
        return request.user == obj.user

class IsCircleAdmin(BasePermission):
    """Permission to check if current user is circle's admin."""

    def has_permission(self, request, view):
        """Verify the user is circle's admin."""
        has_permission = False

        membership = view.get_object()

        if membership.user == request.user:
            has_permission = True

        try:
            if view.action == 'destroy':
                Membership.objects.filter(
                    circle=view.circle,
                    user=request.user,
                    is_admin=True,
                    is_active=True
                )
        except Membership.DoesNotExist:
            has_permission = False
        else:
            has_permission = True

        return has_permission