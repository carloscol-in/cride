"""Rides serializers."""

# DRF
from rest_framework import serializers

# Django
from django.utils import timezone

# Models
from cride.rides.models import Ride

# Utilities
from datetime import timedelta


class CreateRideSerializer(serializers.ModelSerializer):
    """Create ride serializer."""

    offered_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    available_seats = serializers.IntegerField(min_value=1, max_value=15)

    class Meta:
        """Meta class."""

        model = Ride
        exclude = ['offered_in', 'passengers', 'rating', 'is_active']

    def validate_departure_date(self, data):
        """Validate the departure date is after the date this method is
        called on the request. We don't want to show to the user
        rides that have finished or already took off."""

        min_date = timezone.now() + timedelta(minutes=30)

        if data < min_date:
            raise serializers.ValidationError(
                "Departure time must be at least 30 minutes from now."
            )

        return data