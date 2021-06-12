"""Rides views."""

# DRF
from rest_framework.generics import mixins, get_object_or_404
# Permissions
from rest_framework.permissions import IsAuthenticated

# Serializers
from cride.rides.serializers import CreateRideSerializer
# Models
from cride.circles.models import Circle
# Permissions
from cride.circles.permissions.memberships import IsActiveCircleMember

class RideViewSet(
        mixins.CreateModelMixin,
        mixins.GenericViewSet,
    ):
    """Rides view set."""

    serializer_class = CreateRideSerializer
    permission_classes = [IsAuthenticated, IsActiveCircleMember]

    def dispatch(self, request, *args, **kwargs):
        """Verify that the circle exists."""

        slug_name = kwargs['slug_name']

        self.circle = get_object_or_404(
            Circle,
            slug_name=slug_name,
        )

        return super(RideViewSet, self).dispatch(request, *args, **kwargs)