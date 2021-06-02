"""Memberships serializer."""

# Django
from django.utils import timezone

# DRF
from rest_framework import serializers

# serializers
from cride.users.serializers import UserModelSerializer

# models
from cride.circles.models import Membership, Invitation


class MembershipModelSerializer(serializers.ModelSerializer):
    """Membership model serializer."""

    user = UserModelSerializer(read_only=True)
    invited_by = serializers.StringRelatedField()
    joined_at = serializers.DateTimeField(
        source='created',
        read_only=True,
    )

    class Meta:
        """Membership model serializer meta class."""
        model = Membership
        fields = (
            'user', 'is_admin',
            'is_active', 'used_invitations',
            'remaining_invitations',
            'invited_by', 'rides_taken',
            'rides_offered', 'joined_at'
        )
        read_only_fields = (
            'user', 'used_invitations',
            'invited_by', 'rides_taken',
            'rides_offered',
        )

class AddMemberSerializer(serializers.Serializer):
    """Add a member through an invitation code using this serializer."""

    invitation_code = serializers.CharField(min_length=8)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_user(self, data):
        """Verify user isn't already a member."""
        circle = self.context['circle']
        user = data
        q = Membership.objects.filter(circle=circle, user=user)

        if q.exists():
            raise serializers.ValidationError("User is already a circle's member.")

    def validate_invitation_code(self, data):
        """Verify that code exists and is related to the context's circle."""
        circle = self.context['circle']

        try:
            invitation = Invitation.objects.get(
                circle=circle,
                code=data,
                used=False
            )
        except Invitation.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation code.")
        else:
            self.context['invitation'] = invitation

        return data

    def validate(self, data):
        """Verify circle has enough room for new members."""

        circle = self.context['circle']

        if circle.is_limited and circle.members.count() >= circle.members_limit:
            raise serializers.ValidationError("Circle doesn't have room for more members.")

    def create(self, data):
        """Create new circle's member."""

        circle = self.context['circle']
        invitation = self.context['invitation']
        user = data['user']

        # membership creation
        member = Membership.objects.create(
            user=user,
            profile=user.profile,
            circle=circle,
            invited_by=invitation.issued_by
        )

        # update invitation
        invitation.used_by = user
        invitation.used = True
        invitation.used_at = timezone.now()
        invitation.save()

        # update issuer data
        issuer = Membership.objects.get(
            user=invitation.issued_by,
            circle=circle,
        )
        issuer.used_invitations += 1
        issuer.remaining_invitation -= 1
        issuer.save()

        return member