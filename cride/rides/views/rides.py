"""Rides views."""

# DRF
from rest_framework import mixins
from rest_framework.generics import get_object_or_404
# Permissions
from rest_framework.permissions import IsAuthenticated

# Serializers
from cride.rides.serializers import CreateRideSerializer
# Models
from cride.circles.models import Circle
# Views
from cride.utils.views import RelatedToCircle
# Permissions
from cride.circles.permissions.memberships import IsActiveCircleMember

class RideViewSet(
        mixins.CreateModelMixin,
        mixins.GenericViewSet,
        RelatedToCircle,
    ):
    """Rides view set."""

    serializer_class = CreateRideSerializer
    permission_classes = [IsAuthenticated, IsActiveCircleMember]

    # def dispatch(self, request, *args, **kwargs):
    #     """Verify that the circle exists."""

    #     slug_name = kwargs['slug_name']

    #     self.circle = get_object_or_404(
    #         Circle,
    #         slug_name=slug_name,
    #     )

    #     return super(RideViewSet, self).dispatch(request, *args, **kwargs)