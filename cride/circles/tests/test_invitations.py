"""Testing of inviations"""

# Django
from django.test import TestCase

# DRF
from rest_framework import status
from rest_framework.test import APITestCase

# Models
from cride.users.models import Profile
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from cride.circles.models import Invitation, Circle, Membership

User = get_user_model()

class InvitationManagerTestCase(TestCase):
    """Invitations manager test case."""
    
    def setUp(self):
        """Test initialization"""
        self.user = User.objects.create(
            first_name='Joe',
            last_name='Doe',
            email='joe@test-mail.com',
            username='joedoe',
            password='admin123',
        )
        self.circle = Circle.objects.create(
            name='Hiking Vancouver',
            slug_name='hiking-vancouver',
            about='Circle where rides to go hiking get shared',
            verified=True,
        )

    def test_code_generation(self):
        """Random codes should be generated automatically."""
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle
        )
        self.assertIsNotNone(invitation.code)

    def test_code_usage(self):
        """Test that a user can use the code to join a circle."""
        code = 'holamundo'
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
            code=code
        )
        self.assertEqual(invitation.code, code)

    def test_code_generation_if_duplicated(self):
        """If given code is not unique a new one must be generated."""
        code = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
        ).code

        # Create another invitation with the passed code
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
            code=code
        )

        self.assertNotEqual(code, invitation.code)

class MembersInvitationsAPITestCase(APITestCase):
    """Test API endpoint"""

    def setUp(self):
        """Set up needed properties."""
        self.user = User.objects.create(
            first_name='Joe',
            last_name='Doe',
            email='joe@test-mail.com',
            username='joedoe',
            password='admin123',
        )
        self.profile = Profile.objects.create(
            user=self.user,
        )
        self.circle = Circle.objects.create(
            name='Hiking Vancouver',
            slug_name='hiking-vancouver',
            about='Circle where rides to go hiking get shared',
            verified=True,
        )
        self.membership = Membership.objects.create(
            user=self.user,
            profile=self.profile,
            circle=self.circle,
            remaining_invitations=10,
        )
        self.token = Token.objects.create(
            user=self.user,
        ).key

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

    def test_success(self):
        """Verify request succeeds."""
        url = f'/circles/{self.circle.slug_name}/members/{self.user.username}/invitations/'
        request = self.client.get(url)
        # import pdb; pdb.set_trace()
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    