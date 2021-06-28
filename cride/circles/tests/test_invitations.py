"""Testing of inviations"""

# Django
from django.test import TestCase

# Models
from django.contrib.auth import get_user_model
from cride.circles.models import Invitation, Circle

User = get_user_model()

class InvitationManagerTestCase(TestCase):
    """Invitations manager test case."""
    
    def setUp(self):
        """Test initialization"""
        self.user = User.objects.create(
            first_name='Carlos',
            last_name='Colin',
            email='carlos@test-mail.com',
            username='carloscolin',
            password='admin123'
        )
        self.circle = Circle.objects.create(
            name='Golf Interlomas',
            slug_name='golf-interlomas',
            about='Circulo para ir a "rides" que vayan la practica de golf a lo largo de la semana',
            verified=True
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