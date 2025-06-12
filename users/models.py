from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError

# Qualification creation    
class Qualification(models.Model):
    name = models.CharField(max_length=100, unique=True)
    saqa_id = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - SAQA ID: {self.saqa_id}"
    
# User creation   
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('assessor_dev', 'Assessor (Developer)'),
        ('moderator', 'Moderator (Developer)'),
        ('qcto', 'QCTO Validator'),
        ('etqa', 'ETQA'),
        ('learner', 'Learner'),  
        ('assessor_marker', 'Assessor (Marker)'),
        ('internal_mod', 'Internal Moderator'),
        ('external_mod', 'External Moderator (QALA)'),
    ]

    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='learner')
    qualification = models.ForeignKey(
        Qualification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'  # Added for reverse lookup
    )
    email = models.EmailField(unique=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(default=now)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    qualification_updated_at = models.DateTimeField(null=True, blank=True)  # New field
    last_updated_at = models.DateTimeField(auto_now=True)  # New field

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        """Track qualification changes"""
        if self.pk:  # Only for existing users
            original = CustomUser.objects.get(pk=self.pk)
            if original.qualification != self.qualification:
                self.qualification_updated_at = now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']  # New users appear first by default