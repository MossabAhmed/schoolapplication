from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('Admin', 'مسؤول'),
        ('Teacher', 'معلم'),
        ('Student', 'طالب'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Student', verbose_name="الصلاحية")
    enrollment_number = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="رقم القيد", error_messages={'unique': 'رقم القيد هذا مستخدم بالفعل في النظام.'})

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

class Grade(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="اسم الصف (مثال: الأول)", error_messages={'unique': 'هذا الصف موجود بالفعل.'})
    level = models.IntegerField(default=0, verbose_name="الترتيب الأكاديمي")

    class Meta:
        ordering = ['level']

    def __str__(self):
        return self.name

class Section(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='sections', verbose_name="الصف")
    name = models.CharField(max_length=50, verbose_name="الشعبة (مثال: أ، ب)")

    class Meta:
        ordering = ['grade__level', 'name']
        unique_together = ['grade', 'name']

    def __str__(self):
        return f"{self.grade.name} - شعبة {self.name}"

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم المادة", error_messages={'unique': 'اسم هذه المادة موجود بالفعل.'})

    def __str__(self):
        return self.name

class TeacherProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'Teacher'}, related_name="teacher_profile", verbose_name="المعلم")
    subjects = models.ManyToManyField(Subject, related_name='teachers', verbose_name="المواد التي يدرسها")

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'Student'}, related_name="student_profile", verbose_name="الطالب")
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, related_name="students", verbose_name="الفصل/الشعبة")

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Schedule(models.Model):
    DAYS_OF_WEEK = (
        ('Sunday', 'الأحد'),
        ('Monday', 'الاثنين'),
        ('Tuesday', 'الثلاثاء'),
        ('Wednesday', 'الأربعاء'),
        ('Thursday', 'الخميس'),
    )
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="schedules", verbose_name="المعلم")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="schedules", verbose_name="المادة")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="schedules", verbose_name="الفصل")
    day_of_week = models.CharField(max_length=15, choices=DAYS_OF_WEEK, verbose_name="اليوم")
    period = models.IntegerField(verbose_name="الحصة (رقم)")

    def __str__(self):
        return f"{self.subject.name} - {self.section} - {self.get_day_of_week_display()} الحصة {self.period}"

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('Present', 'حاضر'),
        ('Absent', 'غائب'),
    )
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="attendances", verbose_name="الطالب")
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="attendances", verbose_name="الجدول")
    date = models.DateField(verbose_name="التاريخ")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Present', verbose_name="الحالة")
    notes = models.CharField(max_length=255, null=True, blank=True, verbose_name="ملاحظات")

    class Meta:
        unique_together = ('student', 'schedule', 'date')

    def __str__(self):
        return f"{self.student} - {self.date} - {self.get_status_display()}"

class Assignment(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="assignments", verbose_name="المعلم")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assignments", verbose_name="المادة")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="assignments", verbose_name="الفصل")
    title = models.CharField(max_length=200, verbose_name="عنوان الواجب")
    description = models.TextField(blank=True, verbose_name="الوصف")
    due_date = models.DateTimeField(verbose_name="تاريخ التسليم")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    def __str__(self):
        return f"{self.title} - {self.section}"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions", verbose_name="الواجب")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="submissions", verbose_name="الطالب")
    file = models.FileField(upload_to='submissions/', null=True, blank=True, verbose_name="ملف التسليم")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت التسليم")

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"تسليم {self.student} لـ {self.assignment.title}"

class GradeRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="grades", verbose_name="الطالب")
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=True, blank=True, related_name="grades", verbose_name="الواجب (اختياري)")
    exam_title = models.CharField(max_length=100, null=True, blank=True, verbose_name="عنوان الامتحان (إن لم يكن واجباً)")
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="الدرجة")
    notes = models.CharField(max_length=255, null=True, blank=True, verbose_name="ملاحظات")
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"درجة {self.student}: {self.score}"

class Resource(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان المصدر")
    file = models.FileField(upload_to='resources/', verbose_name="الملف المرفق")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="resources", verbose_name="المادة")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="resources", verbose_name="الفصل المعني")
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="resources", verbose_name="المعلم")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Feedback(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="sent_feedbacks", verbose_name="المرسل (المعلم)")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="received_feedbacks", verbose_name="المستلم (الطالب)")
    message = models.TextField(verbose_name="الرسالة/الملاحظة")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ملاحظة من {self.teacher} لـ {self.student}"
