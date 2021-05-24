"""Circle views."""

# Django REST Framework
from rest_framework import viewsets, mixins

# Permissions
from cride.circles.permissions.circles import IsCircleAdmin
from rest_framework.permissions import IsAuthenticated

# cride serializers
from cride.circles.serializers import CircleModelSerializer

# models
from cride.circles.models import Circle, Membership

class CircleViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet,
    ):
    """Circle viewset."""

    serializer_class = CircleModelSerializer
    lookup_field = 'slug_name'

    def get_queryset(self):
        """Override the queryset to filter only the public circles."""
        queryset = Circle.objects.all()

        if self.action == 'list' or self.action == 'retrieve':
            return queryset.filter(is_public=True)
        
        return queryset

    def get_permissions(self):
        """Assign permissions based on actions to perform."""
        permissions = [IsAuthenticated]

        print(self.action)

        if self.action in ['update', 'partial_update']:
            permissions.append(IsCircleAdmin)

        return [permission() for permission in permissions]

    def perform_create(self, serializer):
        """Assign circle admin."""
        circle = serializer.save()
        user = self.request.user
        profile = user.profile
        Membership.objects.create(
            user=user,
            profile=profile,
            circle=circle,
            is_admin=True,
            remaining_invitations=10,
        )