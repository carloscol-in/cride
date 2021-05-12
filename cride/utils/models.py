"""Django models utilities."""

# import django
from django.db import models

class CRideModel(models.Model):
    """Comparte Ride base model.
    
    CRideModel acts as an abstract base model from which every other models in the project
    will inherit. This class provides every table with the following attributes:
        + created (Datetime): Store the date in which the object was created.
        + modified (Datetime): Store the last datetime the object was modified."""

    created = models.DateTimeField(
        'created_at',
        auto_now_add=True,
        help_text='Datetime on which the object was created'
    )
    modified = models.DateTimeField(
        'modified_at',
        auto_now=True,
        help_text='Datetime on which the object was modified'
    )

    class Meta:
        """Meta option."""

        abstract = True

        get_latest_by = 'created'
        ordering = ['-created', '-modified']