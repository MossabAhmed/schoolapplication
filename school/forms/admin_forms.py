from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from school.models import TeacherProfile, StudentProfile, Subject, Section, Grade, Schedule

User = get_user_model()

# Regex لضمان أن رقم القيد مكون من 5 أرقام فقط
enrollment_validator = RegexValidator(
    regex=r'^\d{5}$',
    message="رقم القيد يجب أن يتكون من 5 أرقام فقط."
)

class TeacherCreationForm(forms.ModelForm):
    first_name = forms.CharField(label="الاسم الأول", max_length=30, required=True)
    last_name = forms.CharField(label="اسم العائلة", max_length=30, required=True)
    enrollment_number = forms.CharField(
        label="الرقم الوظيفي (رقم الدخول)",
        validators=[enrollment_validator],
        help_text="يجب أن يتكون من 5 أرقام. ستكون كلمة المرور الافتراضية مطابقة لهذا الرقم."
    )
    subjects = forms.ModelMultipleChoiceField(label="المواد التي يدرسها", queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = User
        fields = ['enrollment_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        enrollment_num = self.cleaned_data['enrollment_number']
        user.username = enrollment_num 
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # تعيين كلمة المرور الافتراضية بنفس قيمة رقم القيد
        user.set_password(enrollment_num)
        user.role = 'Teacher'
        
        if commit:
            user.save()
            profile = TeacherProfile.objects.create(user=user)
            profile.subjects.set(self.cleaned_data['subjects'])
        return user

class StudentCreationForm(forms.ModelForm):
    first_name = forms.CharField(label="الاسم الأول", max_length=30, required=True)
    last_name = forms.CharField(label="اسم العائلة", max_length=30, required=True)
    enrollment_number = forms.CharField(
        label="رقم القيد (رقم الدخول)",
        validators=[enrollment_validator],
        help_text="يجب أن يتكون من 5 أرقام. ستكون كلمة المرور الافتراضية مطابقة لهذا الرقم."
    )
    section = forms.ModelChoiceField(label="الفصل / الشعبة", queryset=Section.objects.all(), required=True)

    class Meta:
        model = User
        fields = ['enrollment_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        enrollment_num = self.cleaned_data['enrollment_number']
        user.username = enrollment_num
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # تعيين كلمة المرور الافتراضية بنفس قيمة رقم القيد
        user.set_password(enrollment_num)
        user.role = 'Student'
        
        if commit:
            user.save()
            StudentProfile.objects.create(user=user, section=self.cleaned_data['section'])
        return user

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['name']
        labels = {'name': 'اسم الصف (مثال: الأول الثانوي)'}

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['grade', 'name']
        labels = {
            'grade': 'الصف',
            'name': 'اسم الشعبة (مثال: أ, ب, 1, 2)'
        }

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']
        labels = {'name': 'اسم المادة (مثال: رياضيات, فيزياء)'}

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['teacher', 'subject', 'section', 'day_of_week', 'period']
        labels = {
            'teacher': 'المعلم',
            'subject': 'المادة',
            'section': 'الفصل/الشعبة',
            'day_of_week': 'اليوم',
            'period': 'رقم الحصة'
        }

