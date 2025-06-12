from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError

# Qualification creation    
class Qualification(models.Model):
    QUALIFICATION_CHOICES = [
        ('Maintenance Planner', 'Maintenance Planner'),
        ('Quality Controller', 'Quality Controller'),
        ('Chemical Plant', 'Chemical Plant'),
    ]

    QUALIFICATION_SAQA_MAPPING = {
        'Maintenance Planner': '101874',
        'Quality Controller': '117309',
        'Chemical Plant': '102156',
    }
    
    name = models.CharField(max_length=100, unique=True)
    saqa_id = models.CharField(max_length=20, unique=True)
    qualification_type = models.CharField(
        max_length=50,
        choices=QUALIFICATION_CHOICES,
        default='Chemical Plant',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - SAQA ID: {self.saqa_id}"

    def clean(self):
        """Validate SAQA ID matches predefined mapping"""
        if self.qualification_type in self.QUALIFICATION_SAQA_MAPPING:
            expected_saqa_id = self.QUALIFICATION_SAQA_MAPPING[self.qualification_type]
            if self.saqa_id != expected_saqa_id:
                raise ValidationError(
                    f"SAQA ID for {self.qualification_type} must be {expected_saqa_id}"
                )
            
    def is_predefined(self):
        """Check if this is one of the predefined qualifications"""
        return self.qualification_type in self.QUALIFICATION_SAQA_MAPPING.keys()
    
# User creation   
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('assessor_dev', 'Assessor (Developer)'),
        ('moderator', 'Moderator (Developer)'),
        ('qcto', 'QCTO Validator'),
        ('etqa', 'ETQA'),
        ('learner', 'Learner'),  # Fixed typo (was 'Learner')
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