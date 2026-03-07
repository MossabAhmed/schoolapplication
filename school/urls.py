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
    path('dashboard/admin/sections/edit/<int:pk>/', views.admin_edit_section, name='admin_edit_section'),
    path('dashboard/admin/sections/delete/<int:pk>/', views.admin_delete_section, name='admin_delete_section'),
    path('dashboard/admin/subjects/edit/<int:pk>/', views.admin_edit_subject, name='admin_edit_subject'),
    path('dashboard/admin/subjects/delete/<int:pk>/', views.admin_delete_subject, name='admin_delete_subject'),
    path('dashboard/admin/grades/edit/<int:pk>/', views.admin_edit_grade, name='admin_edit_grade'),
    path('dashboard/admin/add-section/', views.admin_add_section, name='admin_add_section'),
    path('dashboard/admin/add-subject/', views.admin_add_subject, name='admin_add_subject'),
    path('dashboard/admin/add-schedule/', views.admin_add_schedule, name='admin_add_schedule'),
    path('api/generate-enrollment/', views.generate_enrollment_number, name='generate_enrollment_number'),

    # الجداول باستخدام HTMX
    path('dashboard/admin/schedules/', views.admin_schedule_view, name='admin_schedule_view'),
    path('dashboard/admin/schedules/section/<int:section_id>/', views.get_section_schedule, name='get_section_schedule'),
    
    # إدارة الطلاب والمعلمين
    path('dashboard/admin/students/', views.admin_students_list, name='admin_students_list'),
    path('dashboard/admin/students/edit/<int:user_id>/', views.admin_edit_student, name='admin_edit_student'),
    path('dashboard/admin/students/load/', views.admin_get_students, name='admin_get_students'),
    path('dashboard/admin/teachers/', views.admin_teachers_list, name='admin_teachers_list'),
    path('dashboard/admin/teachers/edit/<int:user_id>/', views.admin_edit_teacher, name='admin_edit_teacher'),
    path('dashboard/admin/users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('dashboard/admin/users/toggle-status/<int:user_id>/', views.admin_toggle_user_status, name='admin_toggle_user_status'),

    # مسارات عامة
    path('change-password/', views.change_password, name='change_password'),

    # مسارات المعلم
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/schedule/', views.teacher_schedule, name='teacher_schedule'),
    path('teacher/students/', views.teacher_students_list, name='teacher_students_list'),
    path('teacher/students/load/', views.teacher_get_students, name='teacher_get_students'),
    path('teacher/attendance/', views.teacher_attendance, name='teacher_attendance'),
    path('teacher/attendance/load-list/', views.teacher_get_attendance_list, name='teacher_get_attendance_list'),
    path('teacher/attendance/save/', views.teacher_save_attendance, name='teacher_save_attendance'),
    path('teacher/grades/', views.teacher_grading, name='teacher_grading'),
    path('teacher/grades/load/', views.teacher_get_grading_list, name='teacher_get_grading_list'),
    path('teacher/grades/save/', views.teacher_save_grades, name='teacher_save_grades'),
    path('teacher/grades/history/load/', views.teacher_load_exam_grades, name='teacher_load_exam_grades'),
    path('teacher/grades/history/update/', views.teacher_update_exam_grades, name='teacher_update_exam_grades'),
    path('teacher/resources/', views.teacher_resources, name='teacher_resources'),
    path('teacher/resources/delete/<int:resource_id>/', views.teacher_delete_resource, name='teacher_delete_resource'),
    path('teacher/feedbacks/', views.teacher_feedbacks, name='teacher_feedbacks'),
    path('teacher/feedbacks/load-students/', views.load_students_for_feedback, name='load_students_for_feedback'),

    # مسارات الطالب
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/grades/', views.student_grades, name='student_grades'),
    path('student/schedule/', views.student_schedule, name='student_schedule'),
    path('student/attendance/', views.student_attendance, name='student_attendance'),
    path('student/resources/', views.student_resources, name='student_resources'),
    path('student/feedbacks/', views.student_feedbacks, name='student_feedbacks'),
]
