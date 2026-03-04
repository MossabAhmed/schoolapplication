import datetime
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.http import HttpResponse, HttpResponseForbidden
from .models import CustomUser, TeacherProfile, StudentProfile, Section, Subject, Schedule, Attendance
from .forms.admin_forms import TeacherCreationForm, StudentCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
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

# --- دوال عرض قوائم وتعديل الطلاب والمعلمين ---
from .forms.admin_forms import StudentEditForm, TeacherEditForm

@login_required
def admin_students_list(request):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return redirect('dashboard_redirect')
        
    sections = Section.objects.all()
    # By default, we might not load students unless they search or click a section.
    # But let's load all or none. Let's load none explicitly, wait for interaction.
    # Or load all initially if no section is active.
    
    return render(request, 'school/admin/students_list.html', {
        'sections': sections,
    })

@login_required
def admin_get_students(request):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return HttpResponseForbidden()
        
    section_id = request.GET.get('section_id')
    query = request.GET.get('q', '')
    
    students = StudentProfile.objects.select_related('user', 'section', 'section__grade').all()
    
    if section_id and section_id.isdigit():
        students = students.filter(section_id=section_id)
        
    if query:
        from django.db.models import Q
        students = students.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query)
        )
        
    # If the request comes from the search box specifically targeting `#students-tbody`, 
    # we should only return the rows so we don't duplicate the search bar.
    if request.headers.get('HX-Target') == 'students-tbody':
        return render(request, 'school/admin/partials/students_table_rows.html', {'students': students})
        
    return render(request, 'school/admin/partials/students_table.html', {'students': students, 'section_id': section_id, 'query': query})

@login_required
def admin_edit_student(request, user_id):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return redirect('dashboard_redirect')
    
    student_user = get_object_or_404(CustomUser, pk=user_id, role='Student')
    
    if request.method == 'POST':
        form = StudentEditForm(request.POST, instance=student_user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل بيانات الطالب بنجاح.')
            return redirect('admin_students_list')
    else:
        form = StudentEditForm(instance=student_user)
        
    return render(request, 'school/admin/add_generic.html', {
        'form': form, 
        'title': f'تعديل بيانات الطالب: {student_user.get_full_name()}'
    })

@login_required
def admin_teachers_list(request):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return redirect('dashboard_redirect')
        
    query = request.GET.get('q', '')
    teachers = TeacherProfile.objects.select_related('user').all()
    
    if query:
        from django.db.models import Q
        teachers = teachers.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query)
        )

    if request.headers.get('HX-Request') == 'true':
        if request.headers.get('HX-Target') == 'teachers-tbody':
            return render(request, 'school/admin/partials/teachers_table_rows.html', {'teachers': teachers})
        # If it's a general HTMX request but not tbody (e.g. some full refresh), we can just return rows or the full page.
        # Below we ensure the search targets just rows.

    return render(request, 'school/admin/teachers_list.html', {'teachers': teachers, 'query': query})

@login_required
def admin_edit_teacher(request, user_id):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return redirect('dashboard_redirect')
    
    teacher_user = get_object_or_404(CustomUser, pk=user_id, role='Teacher')
    
    if request.method == 'POST':
        form = TeacherEditForm(request.POST, instance=teacher_user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل بيانات المعلم بنجاح.')
            return redirect('admin_teachers_list')
    else:
        form = TeacherEditForm(instance=teacher_user)
        
    return render(request, 'school/admin/add_generic.html', {
        'form': form, 
        'title': f'تعديل بيانات المعلم: {teacher_user.get_full_name()}'
    })

@login_required
def admin_toggle_user_status(request, user_id):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return HttpResponseForbidden()
        
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, pk=user_id)
        user.is_active = not user.is_active
        user.save()
        
        # Determine which template partial to return depending on exactly where we are,
        # but since we want to swap just the button, we can return just the button html.
        # It's cleaner to return a snippet. Let's create a small response right here or use a template.
        template_name = 'school/admin/partials/user_status_toggle.html'
        return render(request, template_name, {'user_obj': user})

@login_required
def admin_delete_user(request, user_id):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, pk=user_id)
        role = user.role
        user.delete()
        messages.success(request, 'تم حذف المستخدم بنجاح.')
        
        if role == 'Student':
            return redirect('admin_students_list')
        elif role == 'Teacher':
            return redirect('admin_teachers_list')
            
    return redirect('admin_dashboard')


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
        
    try:
        teacher_profile = request.user.teacher_profile
    except TeacherProfile.DoesNotExist:
        return redirect('login')
        
    # احسب عدد الشعب التي يدرسها المعلم من خلال جداول الحصص
    sections_taught_ids = Schedule.objects.filter(teacher=teacher_profile).values_list('section_id', flat=True).distinct()
    sections_count = sections_taught_ids.count()
    
    # احسب عدد الطلاب الإجمالي في تلك الشعب
    students_count = StudentProfile.objects.filter(section_id__in=sections_taught_ids).count()
    
    # يمكن مستقبلاً حساب عدد التقييمات المعلقة
    pending_assignments_count = 0
    
    import datetime
    
    # تحديد اليوم الحالي
    # في Python: 0=Monday, 6=Sunday
    # لكن حسب أيام النظام التي عرفناها: 'Sunday', 'Monday', ...
    day_map = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }
    today_name = day_map[datetime.datetime.today().weekday()]
    
    # جلب حصص اليوم للمعلم مرتبة حسب الحصة
    today_schedules = Schedule.objects.filter(
        teacher=teacher_profile,
        day_of_week=today_name
    ).select_related('section', 'subject', 'section__grade').order_by('period')
    
    context = {
        'sections_count': sections_count,
        'students_count': students_count,
        'pending_assignments_count': pending_assignments_count,
        'today_schedules': today_schedules,
    }
    
    return render(request, 'school/teacher/dashboard.html', context)

@login_required
def teacher_schedule(request):
    if request.user.role != 'Teacher':
        return redirect('dashboard_redirect')
        
    try:
        teacher_profile = request.user.teacher_profile
    except TeacherProfile.DoesNotExist:
        return redirect('login')

    schedules = Schedule.objects.filter(teacher=teacher_profile).select_related('section', 'subject', 'section__grade')
    
    # بناء مصفوفة الجدول
    # الصفوف: الأيام, الأعمدة: الحصص
    days_keys = [choice[0] for choice in Schedule.DAYS_OF_WEEK]
    periods = range(1, 8)
    
    schedule_matrix = {day: {p: [] for p in periods} for day in days_keys}
    
    for s in schedules:
        if s.day_of_week in schedule_matrix and s.period in schedule_matrix[s.day_of_week]:
            schedule_matrix[s.day_of_week][s.period].append(s)

    context = {
        'schedule_matrix': schedule_matrix,
        'days': Schedule.DAYS_OF_WEEK,
        'periods': periods,
    }
        
    return render(request, 'school/teacher/schedule.html', context)

@login_required
def teacher_students_list(request):
    if request.user.role != 'Teacher':
        return redirect('dashboard_redirect')
        
    try:
        teacher_profile = request.user.teacher_profile
    except TeacherProfile.DoesNotExist:
        return redirect('login')

    sections_taught_ids = Schedule.objects.filter(teacher=teacher_profile).values_list('section_id', flat=True).distinct()
    sections = Section.objects.filter(id__in=sections_taught_ids).select_related('grade')
    
    return render(request, 'school/teacher/students_list.html', {
        'sections': sections,
    })

@login_required
def teacher_get_students(request):
    if request.user.role != 'Teacher':
        return HttpResponseForbidden()
        
    try:
        teacher_profile = request.user.teacher_profile
    except TeacherProfile.DoesNotExist:
        return HttpResponseForbidden()

    sections_taught_ids = Schedule.objects.filter(teacher=teacher_profile).values_list('section_id', flat=True).distinct()

    section_id = request.GET.get('section_id')
    query = request.GET.get('q', '')
    
    students = StudentProfile.objects.filter(section_id__in=sections_taught_ids).select_related('user', 'section', 'section__grade')
    
    if section_id and section_id.isdigit():
        if int(section_id) in sections_taught_ids:
            students = students.filter(section_id=section_id)
        else:
            students = StudentProfile.objects.none()
            
    if query:
        from django.db.models import Q
        students = students.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query)
        )

    if request.headers.get('HX-Target') == 'students-tbody':
        return render(request, 'school/teacher/partials/students_table_rows.html', {'students': students})
        
    return render(request, 'school/teacher/partials/students_table.html', {'students': students, 'section_id': section_id, 'query': query})

@login_required
def teacher_attendance(request):
    if request.user.role != 'Teacher':
        return redirect('dashboard_redirect')
    
    try:
        teacher_profile = request.user.teacher_profile
    except TeacherProfile.DoesNotExist:
        return redirect('login')
        
    date_str = request.GET.get('date', datetime.date.today().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = datetime.date.today()
        
    day_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    day_name = day_map[selected_date.weekday()]
    
    schedules = Schedule.objects.filter(teacher=teacher_profile, day_of_week=day_name).select_related('section', 'subject', 'section__grade').order_by('period')
    
    auto_schedule_id = request.GET.get('schedule_id', '')
    target_section = request.GET.get('target_section')
    if target_section and not auto_schedule_id:
        # Check if there is a schedule for this section today
        sec_sched = schedules.filter(section_id=target_section).first()
        if sec_sched:
            auto_schedule_id = sec_sched.id
            
    context = {
        'selected_date': selected_date,
        'schedules': schedules,
        'auto_schedule_id': auto_schedule_id,
    }
    
    if request.headers.get('HX-Request') == 'true' and 'fetch_schedules' in request.GET:
        return render(request, 'school/teacher/partials/attendance_schedules_options.html', context)
        
    return render(request, 'school/teacher/attendance.html', context)

@login_required
def teacher_get_attendance_list(request):
    if request.user.role != 'Teacher':
        return redirect('dashboard_redirect')
        
    date_str = request.GET.get('date')
    schedule_id = request.GET.get('schedule_id')
    
    if not date_str or not schedule_id:
        return HttpResponse("يرجى تحديد التاريخ والحصة", status=400)
        
    try:
        selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        schedule = Schedule.objects.select_related('section').get(id=schedule_id, teacher=request.user.teacher_profile)
    except (ValueError, Schedule.DoesNotExist):
        return HttpResponse("بيانات غير صالحة", status=400)
        
    # Get students in the section
    students = StudentProfile.objects.filter(section=schedule.section).select_related('user')
    
    # Get existing attendances, if any
    existing_attendances = Attendance.objects.filter(schedule=schedule, date=selected_date)
    attendance_map = {att.student_id: att for att in existing_attendances}

    student_data = []
    for student in students:
        att_record = attendance_map.get(student.id)
        student_data.append({
            'profile': student,
            'status': att_record.status if att_record else 'Present',
            'notes': att_record.notes if att_record and att_record.notes else ''
        })

    arabic_days = {'Monday': 'الاثنين', 'Tuesday': 'الثلاثاء', 'Wednesday': 'الأربعاء', 'Thursday': 'الخميس', 'Friday': 'الجمعة', 'Saturday': 'السبت', 'Sunday': 'الأحد'}
    arabic_months = {1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل', 5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس', 9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'}
    day_name_en = selected_date.strftime('%A')
    formatted_arabic_date = f"{arabic_days.get(day_name_en, day_name_en)}، {selected_date.day} {arabic_months.get(selected_date.month, '')} {selected_date.year}"

    context = {
        'schedule': schedule,
        'selected_date': selected_date,
        'formatted_arabic_date': formatted_arabic_date,
        'student_data': student_data,
    }

    return render(request, 'school/teacher/partials/attendance_student_list.html', context)

@require_POST
@login_required
def teacher_save_attendance(request):
    if request.user.role != 'Teacher':
        return redirect('dashboard_redirect')
        
    date_str = request.POST.get('date')
    schedule_id = request.POST.get('schedule_id')
    
    try:
        selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        schedule = Schedule.objects.get(id=schedule_id, teacher=request.user.teacher_profile)
    except (ValueError, Schedule.DoesNotExist):
        return HttpResponse("بيانات غير صالحة", status=400)
        
    students = StudentProfile.objects.filter(section=schedule.section)
    
    for student in students:
        status = request.POST.get(f'status_{student.id}')
        notes = request.POST.get(f'notes_{student.id}', '')
        if status in ['Present', 'Absent']:
            Attendance.objects.update_or_create(
                student=student,
                schedule=schedule,
                date=selected_date,
                defaults={'status': status, 'notes': notes}
            )
            
    messages.success(request, 'تم حفظ الحضور والغياب بنجاح')
    return HttpResponse(status=204, headers={'HX-Redirect': reverse('teacher_attendance')})

@login_required
def teacher_grading(request):
    if request.user.role != 'Teacher':
        return redirect('dashboard_redirect')
        
    try:
        teacher_profile = request.user.teacher_profile
    except TeacherProfile.DoesNotExist:
        return redirect('login')
        
    # Get distinct sections taught by this teacher by looking at their schedules
    schedules = Schedule.objects.filter(teacher=teacher_profile).select_related('section', 'section__grade')
    sections = {}
    for s in schedules:
        if s.section.id not in sections:
            sections[s.section.id] = s.section
    sections_list = list(sections.values())
    
    context = {
        'sections': sections_list,
    }
    return render(request, 'school/teacher/grading.html', context)

@login_required
def teacher_get_grading_list(request):
    if request.user.role != 'Teacher':
        return redirect('dashboard_redirect')
        
    section_id = request.GET.get('section_id')
    if not section_id:
        return HttpResponse("الرجاء اختيار شعبة", status=400)
        
    section = get_object_or_404(Section, id=section_id)
    students = StudentProfile.objects.filter(section=section).select_related('user')
    
    from .models import GradeRecord
    past_exams = list(GradeRecord.objects.filter(student__section=section)
                      .exclude(exam_title__isnull=True)
                      .exclude(exam_title__exact='')
                      .values_list('exam_title', flat=True)
                      .distinct())

    context = {
        'section': section,
        'students': students,
        'past_exams': past_exams,
    }
    return render(request, 'school/teacher/partials/grading_student_list.html', context)


@require_POST
@login_required
def teacher_save_grades(request):
    if request.user.role != 'Teacher':
        return redirect('dashboard_redirect')
        
    section_id = request.POST.get('section_id')
    exam_title = request.POST.get('exam_title')
    
    if not section_id or not exam_title:
        messages.error(request, 'الرجاء إدخال عنوان التقييم وتحديد الشعبة.')
        return HttpResponse(status=204, headers={'HX-Redirect': reverse('teacher_grading')})
        
    section = get_object_or_404(Section, id=section_id)
    students = StudentProfile.objects.filter(section=section)
    
    saved_count = 0
    from .models import GradeRecord
    
    for student in students:
        score = request.POST.get(f'score_{student.id}')
        notes = request.POST.get(f'notes_{student.id}')
        if score:
            try:
                score_val = float(score)
                GradeRecord.objects.create(
                    student=student,
                    exam_title=exam_title,
                    score=score_val,
                    notes=notes
                )
                saved_count += 1
            except ValueError:
                pass
                
    if saved_count > 0:
        messages.success(request, f'تم حفظ {saved_count} درجة للتقييم "{exam_title}" بنجاح.')
    else:
        messages.warning(request, 'لم يتم إدخال أي درجات صالحة.')
        
    return HttpResponse(status=204, headers={'HX-Redirect': reverse('teacher_grading')})


@login_required
def teacher_load_exam_grades(request):
    """Loads all student grades for a specific past exam in a section"""
    if request.user.role != 'Teacher':
        return redirect('dashboard_redirect')
        
    section_id = request.GET.get('section_id')
    exam_title = request.GET.get('exam_title')
    
    if not section_id or not exam_title:
        return HttpResponse("بيانات غير مكتملة", status=400)
        
    section = get_object_or_404(Section, id=section_id)
    students = StudentProfile.objects.filter(section=section).select_related('user')
    
    from .models import GradeRecord
    
    # Store grades keyed by student id
    student_grades = {}
    records = GradeRecord.objects.filter(student__section=section, exam_title=exam_title)
    for record in records:
        student_grades[record.student_id] = record

    context = {
        'section': section,
        'students': students,
        'exam_title': exam_title,
        'student_grades': student_grades,
    }
    return render(request, 'school/teacher/partials/grading_history_list.html', context)


@require_POST
@login_required
def teacher_update_exam_grades(request):
    """Updates the grades of an existing exam"""
    if request.user.role != 'Teacher':
        return redirect('dashboard_redirect')
        
    section_id = request.POST.get('section_id')
    exam_title = request.POST.get('exam_title')
    
    if not section_id or not exam_title:
         messages.error(request, 'بيانات غير مكتملة.')
         return HttpResponse(status=204, headers={'HX-Redirect': reverse('teacher_grading')})

    section = get_object_or_404(Section, id=section_id)
    students = StudentProfile.objects.filter(section=section)
    
    saved_count = 0
    from .models import GradeRecord
    
    for student in students:
        score_val_str = request.POST.get(f'score_{student.id}')
        notes = request.POST.get(f'notes_{student.id}')
        if score_val_str:
            try:
                score_val = float(score_val_str)
                # update or create
                record, created = GradeRecord.objects.update_or_create(
                    student=student,
                    exam_title=exam_title,
                    defaults={'score': score_val, 'notes': notes}
                )
                saved_count += 1
            except ValueError:
                pass
                
    if saved_count > 0:
        messages.success(request, f'تم تحديث درجات "{exam_title}" بنجاح.')
    else:
        messages.warning(request, 'لم يتم إدخال أو تحديث أي درجات.')
        
    return HttpResponse(status=204, headers={'HX-Redirect': reverse('teacher_grading')})


@login_required
def student_dashboard(request):
    if request.user.role != 'Student':
         return redirect('dashboard_redirect')
         
    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('login')
        
    section = student_profile.section
    
    # Calculate attendance percentage
    total_attendances = Attendance.objects.filter(student=student_profile).count()
    present_attendances = Attendance.objects.filter(student=student_profile, status='Present').count()
    attendance_rate = 100
    if total_attendances > 0:
        attendance_rate = int((present_attendances / total_attendances) * 100)
        
    from .models import GradeRecord
    grades_count = GradeRecord.objects.filter(student=student_profile).count()
    recent_grades = GradeRecord.objects.filter(student=student_profile).order_by('-recorded_at')[:5]
    
    day_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    today_name = day_map[datetime.datetime.today().weekday()]
    
    today_schedules = []
    if section:
        today_schedules = Schedule.objects.filter(section=section, day_of_week=today_name).select_related('subject', 'teacher__user').order_by('period')
    
    context = {
        'student_profile': student_profile,
        'attendance_rate': attendance_rate,
        'grades_count': grades_count,
        'recent_grades': recent_grades,
        'today_schedules': today_schedules,
    }
    return render(request, 'school/student/dashboard.html', context)
@login_required
def admin_add_generic(request, form_class, model_class, template_name, success_message, title, edit_url_name=None):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return redirect('dashboard_redirect')
        
    existing_items = model_class.objects.all()

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, success_message)
            return redirect(request.path_info)
    else:
        form = form_class()
        
    return render(request, template_name, {
        'form': form, 
        'title': title, 
        'items': existing_items,
        'edit_url_name': edit_url_name
    })

@login_required
def admin_edit_generic(request, pk, form_class, model_class, template_name, success_message, title, redirect_url_name):
    if request.user.role != 'Admin' and not request.user.is_superuser:
        return redirect('dashboard_redirect')
    
    item = get_object_or_404(model_class, pk=pk)
    
    if request.method == 'POST':
        form = form_class(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, success_message)
            return redirect(redirect_url_name)
    else:
        form = form_class(instance=item)
    
    return render(request, template_name, {
        'form': form, 
        'title': title
        # No 'items' or 'edit_url_name' needed here as this is the edit page itself, 
        # usually we don't show the list below the edit form to avoid clutter/confusion, 
        # but we could if we wanted. For now, simple edit form.
    })

from .forms.admin_forms import GradeForm, SectionForm, SubjectForm, ScheduleForm
from .models import Grade, Section, Subject, Schedule

@login_required
def admin_add_grade(request):
    return admin_add_generic(request, GradeForm, Grade, 'school/admin/add_generic.html', 'تمت إضافة الصف بنجاح.', 'إضافة صف جديد', 'admin_edit_grade')

@login_required
def admin_edit_grade(request, pk):
    return admin_edit_generic(request, pk, GradeForm, Grade, 'school/admin/add_generic.html', 'تم تعديل الصف بنجاح.', 'تعديل صف', 'admin_add_grade')

@login_required
def admin_add_section(request):
    return admin_add_generic(request, SectionForm, Section, 'school/admin/add_generic.html', 'تمت إضافة الشعبة بنجاح.', 'إضافة شعبة/فصل جديد', 'admin_edit_section')

@login_required
def admin_edit_section(request, pk):
    return admin_edit_generic(request, pk, SectionForm, Section, 'school/admin/add_generic.html', 'تم تعديل الشعبة بنجاح.', 'تعديل شعبة', 'admin_add_section')

@login_required
def admin_add_subject(request):
    return admin_add_generic(request, SubjectForm, Subject, 'school/admin/add_generic.html', 'تمت إضافة المادة بنجاح.', 'إضافة مادة دراسية', 'admin_edit_subject')

@login_required
def admin_edit_subject(request, pk):
    return admin_edit_generic(request, pk, SubjectForm, Subject, 'school/admin/add_generic.html', 'تم تعديل المادة بنجاح.', 'تعديل مادة', 'admin_add_subject')

@login_required
def admin_add_schedule(request):
    # This might need a custom view later as schedule view is more complex usually
    return admin_add_generic(request, ScheduleForm, Schedule, 'school/admin/add_generic.html', 'تمت إضافة الحصة للجدول بنجاح.', 'إضافة حصة للجدول')


from django.contrib.auth import update_session_auth_hash
from school.forms.auth_forms import CustomPasswordChangeForm

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # لمنع تسجيل خروج المستخدم بعد تغيير كلمته
            messages.success(request, 'تم تغيير كلمة المرور بنجاح.')
            return redirect('dashboard_redirect')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = CustomPasswordChangeForm(request.user)
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
from django.http import HttpResponse, HttpResponseForbidden

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
             response = get_section_schedule(request, section_id, form, show_modal=True)
             return response
            
    return render(request, 'school/admin/schedule_manager.html', {
        'sections': sections, 
        'form': form
    })

@login_required
def get_section_schedule(request, section_id, form=None, show_modal=False):
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
        
    # بناء قاموس المعلمين وموادهم
    teachers = TeacherProfile.objects.prefetch_related('subjects').all()
    teacher_subjects_map = {}
    for t in teachers:
        teacher_subjects_map[t.id] = [{'id': sub.id, 'name': sub.name} for sub in t.subjects.all()]
        
    import json
    
    return render(request, 'school/admin/partials/schedule_table.html', {
        'schedule_matrix': schedule_matrix,
        'days': Schedule.DAYS_OF_WEEK,
        'periods': periods,
        'section_id': section_id,
        'form': form,
        'show_modal': show_modal,
        'teacher_subjects_map': teacher_subjects_map
    })

@login_required
def student_grades(request):
    if request.user.role != 'Student':
         return redirect('dashboard_redirect')
         
    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('login')
        
    from .models import GradeRecord
    # Get all grades ordered by latest
    grades = GradeRecord.objects.filter(student=student_profile).order_by('-recorded_at')
    
    context = {
        'grades': grades,
    }
    return render(request, 'school/student/grades.html', context)

