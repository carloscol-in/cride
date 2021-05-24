"""Circle membership views."""

# DRF
from rest_framework import viewsets, mixins
from rest_framework.generics import get_object_or_404

# permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions.memberships import (
    IsActiveCircleMember,
    IsCircleAdmin,
)

# serializers
from cride.circles.serializers import MembershipModelSerializer

# models
from cride.circles.models import Circle, Membership

class MembershipViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
    ):
    """Circle membership view set."""

    serializer_class = MembershipModelSerializer

    def dispatch(self, request, *args, **kwargs):
        """Verify that the circle exists."""

        slug_name = kwargs['slug_name']

        self.circle = get_object_or_404(
            Circle,
            slug_name=slug_name,
        )

        return super(MembershipViewSet, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Assign permissions based on action."""
        permissions = [IsAuthenticated, IsActiveCircleMember, IsCircleAdmin]
        # import pdb; pdb.set_trace()
        return [p() for p in permissions]

    def get_queryset(self):
        """Override queryset that returns circle members."""
        return Membership.objects.filter(
            circle=self.circle,
            is_active=True,
        )

    def get_object(self):
        """Return the circle member by using the user's username."""
        # import pdb; pdb.set_trace()
        return get_object_or_404(
            Membership,
            user__username=self.kwargs['pk'],
            circle=self.circle,
            is_active=True
        )

    def perform_destroy(self, instance):
        """Disable membership."""
        instance.is_active = False
        instance.save()