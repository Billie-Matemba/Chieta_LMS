from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.utils.timezone import now
from django.contrib import messages
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
    user_list = CustomUser.objects.exclude(is_superuser=True)
    predefined_qualifications = Qualification.objects.filter(
        qualification_type__in=Qualification.QUALIFICATION_SAQA_MAPPING.keys()
    )
    custom_qualifications = Qualification.objects.exclude(
        qualification_type__in=Qualification.QUALIFICATION_SAQA_MAPPING.keys()
    )
    
    role_choices = CustomUser.ROLE_CHOICES
    qualification_type_choices = Qualification.QUALIFICATION_CHOICES  
    
    return render(request, 'admin/users.html', {
        'users': user_list,
        'predefined_qualifications': predefined_qualifications,
        'custom_qualifications': custom_qualifications,
        'role_choices': role_choices,
        'qualification_type_choices': qualification_type_choices  
    })

# create users view
@login_required
@staff_member_required
def create_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        role = request.POST.get('role')
        qualification_id = request.POST.get('qualification')  # This can be None
        
        # Generate random password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        try:
            # Get qualification if provided, otherwise None
            qualification = Qualification.objects.get(id=qualification_id) if qualification_id else None
            
            user = CustomUser.objects.create_user(
                username=email,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role,
                qualification=qualification,
                activated_at=now(),
                is_active=True,
            )
            user.set_password(password)
            user.save()
            
            # Send email with password
            send_mail(
                'Your CHIETA LMS Password',
                f'Hi {first_name}, your password is: {password}',
                'noreply@chieta.co.za',
                [email],
                fail_silently=False,
            )
            
            messages.success(request, f'User {email} created successfully')
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
        name = request.POST.get('name')
        saqa_id = request.POST.get('saqa_id')
        qualification_type = request.POST.get('qualification_type')
        
        if name and saqa_id and qualification_type:
            Qualification.objects.create(
                name=name,
                saqa_id=saqa_id,
                qualification_type=qualification_type
            )
            messages.success(request, 'Qualification created successfully')
        else:
            messages.error(request, 'Please fill all required fields')
    
    return redirect('users')

# view to delete qualification but not the predefined one
@login_required
@staff_member_required
def delete_qualification(request, qualification_id):
    if request.method == 'POST':
        try:
            qualification = get_object_or_404(Qualification, id=qualification_id)
            
            if qualification.is_predefined():
                messages.error(request, 'Cannot delete predefined qualifications')
            else:
                name = qualification.name
                qualification.delete()
                messages.success(request, f'Qualification "{name}" deleted successfully')
                
        except Exception as e:
            messages.error(request, f'Error deleting qualification: {str(e)}')
    
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
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.role = request.POST.get('role', user.role)
        
        # Handle qualification change
        new_qualification_id = request.POST.get('qualification')
        if new_qualification_id:
            new_qualification = get_object_or_404(Qualification, id=new_qualification_id)
            user.qualification = new_qualification
        
        try:
            user.save()
            messages.success(request, f'User {user.email} updated successfully')
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
        
        return redirect('users')
    
    # For GET requests, you might want to render a form
    return redirect('users')  # Or render a specific update template

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
