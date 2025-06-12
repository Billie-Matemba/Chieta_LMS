"""
URL configuration for chieta_lms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from users.views import custom_login, custom_logout, admin_dashboard, assessor_dev_dashboard, assessor_marker_dashboard, internal_moderator_dashboard, moderator_dev_dashboard, etqa_dashboard, qcto_dashboard, learner_dashboard, databank, users, centre, marker_analytics, marker_batch, assessment_archive, assessor_reports, generate_tool, upload_assessment, view_assessment, qcto_archive, qcto_assessment_review, qcto_compliance, qcto_compliance_check, qcto_report, qcto_view_assessment, learner_assessment, learner_notification, learner_online_learning, learner_previous_assessment, learner_previous_paper, learner_trial_assessment, create_qualification, create_user, toggle_user_status, delete_qualification, delete_user, update_user

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('', custom_login, name='login'),

    # admin paths 
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/centre/', centre, name='centre'),
    path('dashboard/admin/users/', users, name='users'),
    path('dashboard/admin/databank/', databank, name='databank'),

    path('dashboard/admin/create-user/', create_user, name='create_user'),
    path('dashboard/admin/toggle-user/<int:user_id>/', toggle_user_status, name='toggle_user_status'),
    path('dashboard/admin/create-qualification/', create_qualification, name='create_qualification'),
    path('qualification/delete/<int:qualification_id>/', delete_qualification, name='delete_qualification'),
    path('user/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('users/<int:user_id>/update/', update_user, name='update_user'),

    # assessor paths
    path('dashboard/assessor/', assessor_marker_dashboard, name='assessor_marker_dashboard'),
    path('dashboard/assessor/marker_analytics', marker_analytics, name='marker_analytics'),
    path('dashboard/assessor/marker_batch', marker_batch, name='marker_batch'),
    path('dashboard/assessor-developer/', assessor_dev_dashboard, name='assessor_dev_dashboard'),

    # assessor-developer paths
    path('dashboard/assessor-developer/archive', assessment_archive, name='assessment_archive'),
    path('dashboard/assessor-developer/reports', assessor_reports, name='assessor_reports'),
    path('dashboard/assessor-developer/tool', generate_tool, name='generate_tool'),
    path('dashboard/assessor-developer/upload_assessment', upload_assessment, name='upload_assessment'),
    path('dashboard/assessor-developer/view_assessment', view_assessment, name='view_assessment'),

    # moderator paths
    path('dashboard/internal-moderator/', internal_moderator_dashboard, name='internal_moderator_dashboard'),
    path('dashboard/moderator-developer/', moderator_dev_dashboard, name='moderator_dev_dashboard'),

    # qcto paths 
    path('dashboard/etqa/', etqa_dashboard, name='etqa_dashboard'),
    path('dashboard/qcto/archive', qcto_archive, name='qcto_archive'),
    path('dashboard/qcto/assessment', qcto_assessment_review, name='qcto_assessment_review'),
    path('dashboard/qcto/compliance_check', qcto_compliance_check, name='qcto_compliance_check'),
    path('dashboard/qcto/compliance', qcto_compliance, name='qcto_compliance'),
    path('dashboard/qcto/', qcto_dashboard, name='qcto_dashboard'),
    path('dashboard/qcto/report', qcto_report, name='qcto_report'),
    path('dashboard/qcto/view_assessment', qcto_view_assessment, name='qcto_view_assessment'),


    # student paths
    path('dashboard/learner/assessment', learner_assessment, name='learner_dashboard'),
    path('dashboard/learner/', learner_dashboard, name='learner_dashboard'),
    path('dashboard/learner/notification', learner_notification, name='learner_notification'),
    path('dashboard/learner/online_learning', learner_online_learning, name='learner_online_learning'),
    path('dashboard/learner/previous_assessment', learner_previous_assessment, name='learner_previous_assessment'),
    path('dashboard/learner/previous_papers', learner_previous_paper, name='learner_previous_paper'),
    path('dashboard/learner/trial_assessment', learner_trial_assessment, name='learner_trial_assessment'),

    path('logout/', custom_logout, name='logout')
]
