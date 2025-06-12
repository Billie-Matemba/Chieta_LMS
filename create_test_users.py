import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chieta_lms.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from users.models import Qualification  # Make sure this import path is correct

def create_test_users():
    User = get_user_model()
    
    # Create test qualification
    qualification, created = Qualification.objects.get_or_create(
        name="Test Qualification",
        defaults={'created_at': timezone.now()}
    )
    
    # Define test users
    test_users = [
        # {'email': 'moderator@test.com', 'password': 'moderator123', 'role': 'moderator', 'first_name': 'Moderator', 'last_name': 'User'},
        # {'email': 'internal_mod@test.com', 'password': 'internal123', 'role': 'internal_mod', 'first_name': 'Internal', 'last_name': 'Moderator'},
        {'email': 'assessor_marker@test.com', 'password': 'marker123', 'role': 'assessor_marker', 'first_name': 'Assessor', 'last_name': 'Marker'},
        {'email': 'etqa@test.com', 'password': 'etqa123', 'role': 'etqa', 'first_name': 'ETQA', 'last_name': 'Officer'},
        {'email': 'qcto@test.com', 'password': 'qcto123', 'role': 'qcto', 'first_name': 'QCTO', 'last_name': 'Validator'},
        {'email': 'external_mod@test.com', 'password': 'external123', 'role': 'external_mod', 'first_name': 'External', 'last_name': 'Moderator'},
        
    ]


    print("Creating test users:\n")
    
    for user_data in test_users:
        user = User.objects.create_user(
            username=user_data['email'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role'],
            qualification=qualification,
            is_active=True
        )
        print(f"Created {user.get_role_display()} user:")
        print(f"• Email: {user.email}")
        print(f"• Password: {user_data['password']}")
        print(f"• Name: {user.first_name} {user.last_name}\n")

    print("All test users created successfully!")

if __name__ == '__main__':
    create_test_users()