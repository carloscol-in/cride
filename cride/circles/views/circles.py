"""Circle views."""

# Django REST Framework
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

# serializers
from cride.circles.serializers import CircleModelSerializer

# models
from cride.circles.models import Circle, Membership


class CircleViewSet(viewsets.ModelViewSet):
    """Circle viewset."""
    queryset = Circle.objects.all()
    serializer_class = CircleModelSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Override the queryset to filter only the public circles."""
        queryset = Circle.objects.all()

        if self.action == 'list' or self.action == 'retrieve':
            return queryset.filter(is_public=True)
        
        return queryset

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