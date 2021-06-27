"""Ratings model."""

# Django
from django.db import models

# Models
from cride.utils.models import CRideModel


class Rating(CRideModel):
    """Rating model."""

    ride = models.ForeignKey(
        'rides.Ride',
        on_delete=models.CASCADE,
        related_name='rated_ride'
    )
    circle = models.ForeignKey(
        'circles.Circle',
        on_delete=models.CASCADE
    )

    rating_user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        help_text="User that sends the rating",
        related_name="rating_user"
    )

    rated_user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        help_text="User that is being rated",
        related_name="rated_user"
    )

    comments = models.TextField(
        'ride comments',
        max_length=500,
        blank=True,
        null=True,
    )

    rating = models.PositiveSmallIntegerField(
        'ride rating',
        default=1,
        blank=True,
        null=True,
    )