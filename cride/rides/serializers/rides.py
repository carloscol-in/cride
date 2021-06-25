"""Rides serializers."""

# DRF
from rest_framework import serializers
from rest_framework.authentication import get_user_model
User = get_user_model()

# Django
from django.utils import timezone

# Models
from cride.circles.models import Membership
from cride.rides.models import Ride

# Serializers
from cride.users.serializers import UserModelSerializer

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

        min_date = timezone.now() + timedelta(minutes=10)

        if data < min_date:
            raise serializers.ValidationError(
                "Departure time must be at least 30 minutes from now."
            )

        return data

    def validate(self, data):
        """Validate.

        Verify that the person who offers the ride is a member
        and also the same user making the request.
        """
        user = data['offered_by']
        circle = self.context['circle']

        if self.context['request'].user != user:
            raise serializers.ValidationError("Rides offered on behalf on another person are not allowed.")

        try:
            membership = Membership.objects.get(
                user=user, 
                circle=circle,
                is_active=True
            )
        except Membership.DoesNotExist:
            raise serializers.ValidationError("User is not an active member.")
        else:
            self.context['membership'] = membership

        if data['arrival_date'] <= data['departure_date']:
            raise serializers.ValidationError("Departure should happen before arrival.")

        return data

    def create(self, data):
        """Create a ride and update stats."""

        circle = self.context['circle']

        # import pdb; pdb.set_trace()

        ride = Ride.objects.create(**data, offered_in=circle)

        # Circle
        circle.rides_offered += 1
        circle.save()

        # Membership
        membership = self.context['membership']
        membership.rides_offered += 1
        membership.save()

        # Profile
        profile = data['offered_by'].profile
        profile.rides_offered += 1
        profile.save()

        return ride

class RideModelSerializer(serializers.ModelSerializer):
    """Ride model serializer."""

    offered_by = UserModelSerializer(read_only=True)
    offered_in = serializers.StringRelatedField()

    passengers = UserModelSerializer(read_only=True, many=True)

    class Meta:
        """Meta class."""

        model = Ride
        fields = '__all__'
        read_only_fields = (
            'offered_by',
            'offered_in',
            'rating'
        )

    def update(self, instance, data):
        """Update ride data only before departure date."""

        now = timezone.now()

        if instance.departure_date <= now:
            raise serializers.ValidationError("Ongoing rides cannot be modified.")

        return super(RideModelSerializer, self).update(instance, data)

class JoinRideSerializer(serializers.ModelSerializer):
    """Join ride serializer."""

    passenger = serializers.IntegerField()

    class Meta:
        """Meta class."""

        model = Ride
        fields = ('passenger',)

    def validate_passenger(self, data):
        """Verify user is member of the circle and is not already on another trip simultaneously."""

        try:
            user = User.objects.get(pk=data)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid passenger.")

        circle = self.context['circle']

        try:
            membership = Membership.objects.get(
                user=user,
                circle=circle,
                is_active=True
            )
        except Membership.DoesNotExist:
            raise serializers.ValidationError("User is not an active member.")
        else:
            self.context['membership'] = membership

        self.context['user'] = user
        return data

    def validate(self, data):
        """Verify that the ride allows new passengers."""
        ride = self.context['ride']

        if ride.departure_date <= timezone.now():
            raise serializers.ValidationError("You can't join this ride now.")

        if ride.offered_by == self.context['user']:
            raise serializers.ValidationError("The ride's creator cannot join as a passenger.")

        if ride.available_seats < 1:
            raise serializers.ValidationError("There's not enough room for another passenger in this ride.")

        if Ride.objects.filter(passengers__pk=data['passenger']):
            raise serializers.ValidationError("Passenger is already registered for this trip.")

        return data

    def update(self, instance, data):
        """Add passenger to ride and update status."""
        ride = self.context['ride']
        user = self.context['user']

        # TODO: maybe should use F() to update models' fields

        # update ride status
        ride.passengers.add(user)
        ride.available_seats -= 1

        # update profile status
        profile = user.profile
        profile.rides_taken += 1
        profile.save()

        # update membership status
        membership = self.context['membership']
        membership.rides_taken += 1

        # update circle status
        circle = self.context['circle']
        circle.rides_taken += 1
        circle.save()

        return ride


class EndRideSerializer(serializers.ModelSerializer):
    """Use this serializer to finish a ride."""
    
    current_time = serializers.DateTimeField()

    class Meta:
        """Meta class. Should be defined on all model serializers."""

        model = Ride
        fields = ('is_active', 'current_time')

    def validate_current_time(self, data):
        """Verify ride has already started."""
        ride = self.context['view'].get_object()
        if data <= ride.departure_date:
            raise serializers.ValidationError("Ride has not started yet.")
        return data