from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.utils.timezone import now
from django.contrib import messages
from django.core.exceptions import ValidationError 
import random, string

from .models import CustomUser, Qualification

# LOGIN VIEW
def custom_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')


        user = authenticate(request, email=email, password=password)
        #user = authenticate(request, email=email, password=password)

        if user is not None:
            # if not user.is_active:
            #     return render(request, 'login/login.html', {'error': 'Account deactivated'})

            login(request, user)
            # redirect based on role
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'moderator':
                return redirect('moderator_dev_dashboard')
            elif user.role == 'internal_mod':
                return redirect('internal_moderator_dashboard')
            elif user.role == 'assessor_dev':
                return redirect('assessor_dev_dashboard')
            elif user.role == 'assessor_marker':
                return redirect('assessor_marker_dashboard')
            elif user.role == 'etqa':
                return redirect('etqa_dashboard')
            elif user.role == 'qcto':
                return redirect('qcto_dashboard')
            elif user.role == 'learner':
                return redirect('learner_dashboard')
        else:
            return render(request, 'login/login.html', {'error': 'Invalid credentials'})

    return render(request, 'login/login.html')

# ADMIN USER MANAGEMENT VIEWS
@login_required
@staff_member_required
def users(request):
    # Get status filter from URL (default to showing active qualifications)
    status_filter = request.GET.get('status', 'active')
    
    # Filter qualifications based on status
    qualifications = Qualification.objects.all()
    if status_filter == 'active':
        qualifications = qualifications.filter(is_active=True)
    elif status_filter == 'inactive':
        qualifications = qualifications.filter(is_active=False)
    # 'all' shows all qualifications (no filter applied)
    
    # Get user list (excluding superusers)
    user_list = CustomUser.objects.exclude(is_superuser=True)
    
    return render(request, 'admin/users.html', {
        'users': user_list,
        'qualifications': qualifications,
        'role_choices': CustomUser.ROLE_CHOICES,
        'current_status_filter': status_filter  # Pass the current filter to template
    })
#create user view
@login_required
@staff_member_required
def create_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        email = request.POST.get('email').strip().lower()
        role = request.POST.get('role')
        qualification_id = request.POST.get('qualification')  # Can be None/empty
        
        # Input validation
        if not all([first_name, last_name, email, role]):
            messages.error(request, 'All required fields must be filled')
            return redirect('users')
        
        # Generate random password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        try:
            # Get qualification if provided (and exists)
            qualification = None
            if qualification_id:
                try:
                    qualification = Qualification.objects.get(id=qualification_id, is_active=True)
                except Qualification.DoesNotExist:
                    messages.warning(request, 'Selected qualification not found or inactive - user created without qualification')
            
            user = CustomUser.objects.create_user(
                username=email,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role,
                qualification=qualification,
                password=password,  # Set password directly in create_user
                is_active=True,
                activated_at=now(),
            )
            
            # Send email with credentials
            send_mail(
                'Your CHIETA LMS Account Details',
                f'''Hi {first_name},
                
Your CHIETA LMS account has been created:
Email: {email}
Password: {password}

Please change your password after first login.
                ''',
                'noreply@chieta.co.za',
                [email],
                fail_silently=False,
            )
            
            messages.success(request, f'User {email} created successfully. Password emailed.')
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
    
    return redirect('users')

# view to activate or deactivate user
@login_required
@staff_member_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = not user.is_active
    if user.is_active:
        user.activated_at = now()
        user.deactivated_at = None
    else:
        user.deactivated_at = now()
    user.save()
    return redirect('users')

# view to create qualification 
@login_required
@staff_member_required
def create_qualification(request):
    if request.method == 'POST':
        name = request.POST.get('name').strip()
        saqa_id = request.POST.get('saqa_id').strip()
        
        if not (name and saqa_id):  # Check if required fields are filled
            messages.error(request, 'Name and SAQA ID are required')
            return redirect('users')
            
        try:
            # Check for uniqueness before creation
            if Qualification.objects.filter(name=name).exists():
                messages.error(request, 'A qualification with this name already exists')
                return redirect('users')
                
            if Qualification.objects.filter(saqa_id=saqa_id).exists():
                messages.error(request, 'A qualification with this SAQA ID already exists')
                return redirect('users')
            
            # Create the qualification (is_active=True by default from model)
            Qualification.objects.create(
                name=name,
                saqa_id=saqa_id
            )
            messages.success(request, f'Qualification "{name}" created successfully')
            
        except Exception as e:
            messages.error(request, f'Error creating qualification: {str(e)}')
    
    return redirect('users')

# view to activate or deactivate qualification (toggle)
@login_required
@staff_member_required
def toggle_qualification_status(request, qualification_id):
    try:
        qualification = Qualification.objects.get(id=qualification_id)
        
        # Toggle the is_active status
        qualification.is_active = not qualification.is_active
        qualification.save()
        
        action = "activated" if qualification.is_active else "deactivated"
        messages.success(request, f'Qualification "{qualification.name}" has been {action}')
        
    except Qualification.DoesNotExist:
        messages.error(request, 'Qualification not found')
    except Exception as e:
        messages.error(request, f'Error updating qualification: {str(e)}')
    
    return redirect('users')
    
# View to delete user
@login_required
@staff_member_required
def delete_user(request, user_id):
    if request.method == 'POST':
        try:
            user = get_object_or_404(CustomUser, id=user_id)
            email = user.email
            user.delete()
            messages.success(request, f'User {email} deleted successfully')
        except Exception as e:
            messages.error(request, f'Error deleting user: {str(e)}')
    return redirect('users')

# view to update users
@login_required
@staff_member_required
def update_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        try:
            # Update basic fields
            user.first_name = request.POST.get('first_name', user.first_name).strip()
            user.last_name = request.POST.get('last_name', user.last_name).strip()
            user.email = request.POST.get('email', user.email).strip().lower()
            user.role = request.POST.get('role', user.role)
            
            # Handle qualification change (including clearing it)
            new_qualification_id = request.POST.get('qualification')
            if new_qualification_id == '':  # Empty string means remove qualification
                user.qualification = None
            elif new_qualification_id:  # New qualification selected
                new_qualification = get_object_or_404(Qualification, id=new_qualification_id, is_active=True)
                user.qualification = new_qualification
            
            # Email uniqueness check (if email changed)
            if CustomUser.objects.exclude(id=user.id).filter(email=user.email).exists():
                messages.error(request, 'This email is already in use by another user')
                return redirect('users')
            
            user.save()
            messages.success(request, f'User {user.email} updated successfully')
            
        except ValidationError as e:
            messages.error(request, f'Validation error: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
        
        return redirect('users')
    
    return redirect('users')  # GET requests redirect back

# GENERAL DASHBOARD
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

# ADMIN DASHBOARDS
@login_required
def admin_dashboard(request):
    return render(request, 'admin/admin_dashboard.html')

@login_required
def centre(request):
    return render(request, 'admin/centre.html')

@login_required
def databank(request):
    return render(request, 'admin/databank.html')

# MODERATOR DASHBOARDS
@login_required
def moderator_dev_dashboard(request):
    return render(request, 'moderator/moderator_dev_dashboard.html')

@login_required
def internal_moderator_dashboard(request):
    return render(request, 'moderator/internal_moderator_dashboard.html')

# ASSESSOR DASHBOARDS
@login_required
def assessor_dev_dashboard(request):
    return render(request, 'assessor-developer/assessor_dev_dashboard.html')

@login_required
def assessment_archive(request):
    return render(request, 'assessor-developer/assessment_archive.html')

@login_required
def assessor_reports(request):
    return render(request, 'assessor-developer/assessor_reports.html')

@login_required
def generate_tool(request):
    return render(request, 'assessor-developer/generate_tool.html')

@login_required
def upload_assessment(request):
    return render(request, 'assessor-developer/upload_assessment.html')

@login_required
def view_assessment(request):
    return render(request, 'assessor-developer/view_assessment.html')

@login_required
def assessor_marker_dashboard(request):
    return render(request, 'assessor/assessor_marker_dashboard.html')

@login_required
def marker_analytics(request):
    return render(request, 'assessor/marker_analytics.html')

@login_required
def marker_batch(request):
    return render(request, 'assessor/marking_batch_view.html')

# QCTO DASHBOARDS
@login_required
def etqa_dashboard(request):
    return render(request, 'qcto/etqa_dashboard.html')

@login_required
def qcto_archive(request):
    return render(request, 'qcto/qcto_archive.html')

@login_required
def qcto_assessment_review(request):
    return render(request, 'qcto/qcto_assessment_review.html')

@login_required
def qcto_compliance_check(request):
    return render(request, 'qcto/qcto_compliance_check.html')

@login_required
def qcto_compliance(request):
    return render(request, 'qcto/qcto_compliance.html')

@login_required
def qcto_dashboard(request):
    return render(request, 'qcto/qcto_dashboard.html')

@login_required
def qcto_report(request):
    return render(request, 'qcto/qcto_report.html')

@login_required
def qcto_view_assessment(request):
    return render(request, 'qcto/qcto_view_assessment.html')

# LEARNER VIEWS
@login_required
def learner_dashboard(request):
    return render(request, 'student/learner_dashboard.html')

@login_required
def learner_assessment(request):
    return render(request, 'student/assessment.html')

@login_required
def learner_notification(request):
    return render(request, 'student/notification.html')

@login_required
def learner_online_learning(request):
    return render(request, 'student/online_learning.html')

@login_required
def learner_previous_assessment(request):
    return render(request, 'student/previous_assessment.html')

@login_required
def learner_previous_paper(request):
    return render(request, 'student/previous_paper.html')

@login_required
def learner_trial_assessment(request):
    return render(request, 'student/trial_assessment.html')

# LOGOUT VIEW
def custom_logout(request):
    logout(request)
    return redirect('login')
