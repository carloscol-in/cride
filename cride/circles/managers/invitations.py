"""Circle invitation managers."""

# Django
from django.db import models

# Utilities
import random
from string import ascii_letters, digits

def generate_random_code(code_length: int, choices_pool: str) -> str:
    """Generate random code."""
    return ''.join(random.choices(choices_pool, k=code_length))

class InvitationManager(models.Manager):
    """Invitation manager.
    
    Used to handle the creation of invitation codes."""

    CODE_LENGTH = 10

    def create(self, **kwargs):
        """Create a new invitation."""

        pool = ascii_letters + digits
        code = kwargs.get('code', generate_random_code(self.CODE_LENGTH, pool))
        while self.filter(code=code).exists():
            code = generate_random_code(self.CODE_LENGTH, pool)
        kwargs['code'] = code
        return super(InvitationManager, self).create(**kwargs)