from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms.admin_forms import TeacherCreationForm, StudentCreationForm
from .models import CustomUser, TeacherProfile, StudentProfile
from django.contrib import messages

@login_required
def dashboard_redirect(request):
    """
    توجيه المستخدم إلى اللوحة الخاصة به بناءً على صلاحيته (Role)
    """
    if request.user.role == 'Admin' or request.user.is_superuser:
        return redirect('admin_dashboard')
    elif request.user.role == 'Teacher':
        return redirect('teacher_dashboard')
    elif request.user.role == 'Student':
        return redirect('student_dashboard')
    
    # في حال لم يكن له دور محدد
    return redirect('login')

@login_required
def admin_dashboard(request):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return redirect('dashboard_redirect')
        
    students_count = CustomUser.objects.filter(role='Student').count()
    teachers_count = CustomUser.objects.filter(role='Teacher').count()
    
    context = {
        'students_count': students_count,
        'teachers_count': teachers_count,
    }
    return render(request, 'school/admin/dashboard.html', context)

@login_required
def admin_add_teacher(request):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        form = TeacherCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تمت إضافة المعلم بنجاح.')
            return redirect('admin_dashboard')
    else:
        form = TeacherCreationForm()
        
    return render(request, 'school/admin/add_teacher.html', {'form': form})

@login_required
def admin_add_student(request):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تمت إضافة الطالب بنجاح.')
            return redirect('admin_dashboard')
    else:
        form = StudentCreationForm()
        
    return render(request, 'school/admin/add_student.html', {'form': form})

@login_required
def teacher_dashboard(request):
    if request.user.role != 'Teacher':
         return redirect('dashboard_redirect')
    return render(request, 'school/teacher/dashboard.html')

@login_required
def student_dashboard(request):
    if request.user.role != 'Student':
         return redirect('dashboard_redirect')
    return render(request, 'school/student/dashboard.html')
@login_required
def admin_add_generic(request, form_class, template_name, success_message, title):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, success_message)
            return redirect('admin_dashboard')
    else:
        form = form_class()
        
    return render(request, template_name, {'form': form, 'title': title})

from .forms.admin_forms import GradeForm, SectionForm, SubjectForm, ScheduleForm

@login_required
def admin_add_grade(request):
    return admin_add_generic(request, GradeForm, 'school/admin/add_generic.html', 'تمت إضافة الصف بنجاح.', 'إضافة صف جديد')

@login_required
def admin_add_section(request):
    return admin_add_generic(request, SectionForm, 'school/admin/add_generic.html', 'تمت إضافة الشعبة بنجاح.', 'إضافة شعبة/فصل جديد')

@login_required
def admin_add_subject(request):
    return admin_add_generic(request, SubjectForm, 'school/admin/add_generic.html', 'تمت إضافة المادة بنجاح.', 'إضافة مادة دراسية')

@login_required
def admin_add_schedule(request):
    return admin_add_generic(request, ScheduleForm, 'school/admin/add_generic.html', 'تمت إضافة الحصة للجدول بنجاح.', 'إضافة حصة للجدول')


from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # لمنع تسجيل خروج المستخدم بعد تغيير كلمته
            messages.success(request, 'تم تغيير كلمة المرور بنجاح.')
            return redirect('dashboard_redirect')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'school/change_password.html', {'form': form})

import random
from django.http import JsonResponse

@login_required
def generate_enrollment_number(request):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    while True:
        new_number = str(random.randint(10000, 99999))
        if not CustomUser.objects.filter(enrollment_number=new_number).exists():
            return JsonResponse({'number': new_number})
from .models import Schedule, Section
from django.http import HttpResponse

@login_required
def admin_schedule_view(request):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return redirect('dashboard_redirect')
        
    sections = Section.objects.all()
    form = ScheduleForm()
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save()
            messages.success(request, 'تمت إضافة الحصة للجدول بنجاح.')
            
            if request.headers.get('HX-Request') == 'true':
                return get_section_schedule(request, schedule.section.id)
            
            return redirect('admin_schedule_view')
        
        elif request.headers.get('HX-Request') == 'true':
             section_id = request.POST.get('section')
             response = get_section_schedule(request, section_id, form)
             # إعادة فتح المودال لإظهار الأخطاء
             response.content += b'<script>document.getElementById("add-schedule-modal").classList.remove("hidden");</script>'
             return response
            
    return render(request, 'school/admin/schedule_manager.html', {
        'sections': sections, 
        'form': form
    })

@login_required
def get_section_schedule(request, section_id, form=None):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return HttpResponse('Unauthorized', status=403)
        
    section = Section.objects.get(id=section_id)
    schedules = Schedule.objects.filter(section=section).order_by('period')
    
    days = [choice[0] for choice in Schedule.DAYS_OF_WEEK]
    periods = range(1, 8) 
    
    schedule_matrix = {day: {period: None for period in periods} for day in days}
    for schedule in schedules:
        schedule_matrix[schedule.day_of_week][schedule.period] = schedule
        
    # حقن الـ form حتى يتم استخدامه في الـ modal لجلب المعلمين والمواد
    from .forms.admin_forms import ScheduleForm
    if form is None:
        form = ScheduleForm()
        
    return render(request, 'school/admin/partials/schedule_table.html', {
        'schedule_matrix': schedule_matrix,
        'days': Schedule.DAYS_OF_WEEK,
        'periods': periods,
        'section_id': section_id,
        'form': form
    })
