"""Users serializers."""

# utils
from datetime import timedelta

# JWT
import jwt

# Django
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import authenticate, password_validation

# Django REST Framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# Tasks
from cride.taskapp.tasks import send_confirmation_email

# models
from cride.users.models import User, Profile

# serializers
from cride.users.serializers.profiles import ProfileModelSerializer

class AccountVerificationSerializer(serializers.Serializer):
    """Account verification serializer."""

    token = serializers.CharField()

    def validate_token(self, data):
        """Verify token is valid."""
        try:
            payload = jwt.decode(data, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError("Verification link has expired.")
        except jwt.PyJWTError:
            raise serializers.ValidationError("Invalid token.")
        
        if payload['type'] != 'email_confirmation':
            raise serializers.ValidationError("Invalid token.")

        self.context['payload'] = payload

        return data

    def save(self):
        """Update the users `verified` status."""
        payload = self.context['payload']
        user = User.objects.get(username=payload['user'])
        user.is_verified = True
        user.save()

class UserModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    profile = ProfileModelSerializer(read_only=True)
    
    class Meta:
        """Meta class."""
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'profile',
        )

class UserLoginSerializer(serializers.Serializer):
    """User login serializer.
    
    Handle the login request data."""

    email = serializers.EmailField()
    password = serializers.CharField(
        min_length=8,
        max_length=64,
    )

    def validate(self, data):
        """Verify credentials."""
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_verified:
            raise serializers.ValidationError("Account is not active yet.")
        self.context['user'] = user
        return data

    def create(self, data):
        """Generate or retrieve new token."""
        token, created = Token.objects.get_or_create(user=self.context['user'])
        return (self.context['user'], token.key)

class UserSignUpSerializer(serializers.Serializer):
    """Users sign-up serializer.
    
    Handle the sign-up request data validation and user/profile creation."""
    
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        min_length=4,
        max_length=20,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    # validate phone number using regex validator
    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message="Phone number must be entered in the format +999999999. Up to 15 digits allowed."
    )
    phone_number = serializers.CharField(validators=[phone_regex])

    # password
    password = serializers.CharField(
        min_length=8,
        max_length=64,
    )
    password_confirmation = serializers.CharField(
        min_length=8,
        max_length=64,
    )

    # name
    first_name = serializers.CharField(min_length=2, max_length=30)
    last_name = serializers.CharField(min_length=2, max_length=30)

    def validate(self, data):
        """Verify passwords match."""
        passwd = data['password']
        passwd_conf = data['password_confirmation']

        if passwd != passwd_conf:
            raise serializers.ValidationError({
                'password_confirmation': 'Passwords don\'t match.'
            })

        password_validation.validate_password(passwd)
        return data

    def create(self, data):
        """Handle user/profile creation."""
        data.pop('password_confirmation')

        try:
            user = User.objects.create_user(**data, is_verified=False, is_client=True)
        except IntegrityError as e:
            raise serializers.ValidationError('Username or Email already exists.')

        Profile.objects.create(user=user)

        # send email
        send_confirmation_email.delay(user_pk=user.pk)

        return user