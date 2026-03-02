from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard_redirect, name='dashboard_redirect'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # مسارات الإدارة (الخاصة بالتطبيق غير Django Admin)
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/add-teacher/', views.admin_add_teacher, name='admin_add_teacher'),
    path('dashboard/admin/add-student/', views.admin_add_student, name='admin_add_student'),
    path('dashboard/admin/add-grade/', views.admin_add_grade, name='admin_add_grade'),
    path('dashboard/admin/add-section/', views.admin_add_section, name='admin_add_section'),
    path('dashboard/admin/add-subject/', views.admin_add_subject, name='admin_add_subject'),
    path('dashboard/admin/add-schedule/', views.admin_add_schedule, name='admin_add_schedule'),
    path('api/generate-enrollment/', views.generate_enrollment_number, name='generate_enrollment_number'),

    # الجداول باستخدام HTMX
    path('dashboard/admin/schedules/', views.admin_schedule_view, name='admin_schedule_view'),
    path('dashboard/admin/schedules/section/<int:section_id>/', views.get_section_schedule, name='get_section_schedule'),

    # مسارات عامة
    path('change-password/', views.change_password, name='change_password'),

    # مسارات المعلم
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/attendance/', views.teacher_dashboard, name='teacher_attendance'), # سيتم استبدال هذه بـ views الحضور لاحقاً
    path('teacher/grades/', views.teacher_dashboard, name='teacher_grading'), # سيتم استبدال هذه بـ views التقييم لاحقاً
    
    # مسارات الطالب
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/grades/', views.student_dashboard, name='student_grades'), # سيتم استبدال هذه بـ views الدرجات لاحقاً
]
