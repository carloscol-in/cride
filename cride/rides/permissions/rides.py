"""Rides permissions."""

# DRF
from rest_framework.permissions import BasePermission


class IsRideOwner(BasePermission):
    """Verify request user is ride publisher."""

    def has_object_permission(self, request, view, obj):
        """Verify request user is the ride creator."""

        return request.user == obj.offered_by


class IsNotRideOwner(BasePermission):
    """Verify the user is not the ride publisher"""

    def has_object_permission(self, request, view, obj):
        """Verify the user is not the ride publisher."""

        return not request.user == obj.offered_by