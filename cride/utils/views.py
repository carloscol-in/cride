"""Rides mixins."""

# DRF
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

# Models
from cride.circles.models import Circle

class RelatedToCircle(viewsets.GenericViewSet):
    """This class has to be inherited by all classes that need to
    dispatch circle objects related to their class."""

    def dispatch(self, request, *args, **kwargs):
        """Verify that the circle exists."""

        slug_name = kwargs['slug_name']

        self.circle = get_object_or_404(
            Circle,
            slug_name=slug_name,
        )

        return super(RelatedToCircle, self).dispatch(request, *args, **kwargs)