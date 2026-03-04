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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'subjects':
                 continue 
            classes = 'w-full px-4 py-2 border border-gray-300 rounded-lg outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors'
            if field_name == 'enrollment_number':
                 classes = 'w-full px-4 py-2 border border-gray-300 rounded-r-lg outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'
            field.widget.attrs.update({'class': classes})

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

class TeacherEditForm(forms.ModelForm):
    first_name = forms.CharField(label="الاسم الأول", max_length=30)
    last_name = forms.CharField(label="اسم العائلة", max_length=30)
    enrollment_number = forms.CharField(label="الرقم الوظيفي", disabled=True, required=False) # readonly
    subjects = forms.ModelMultipleChoiceField(label="المواد التي يدرسها", queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate fields from the user instance if provided
        if self.instance.pk:
            self.fields['first_name'].initial = self.instance.first_name
            self.fields['last_name'].initial = self.instance.last_name
            self.fields['enrollment_number'].initial = self.instance.username
            
            # Try to get profile
            try:
                profile = self.instance.teacher_profile
                self.fields['subjects'].initial = profile.subjects.all()
            except TeacherProfile.DoesNotExist:
                pass

        for field_name, field in self.fields.items():
            if field_name == 'subjects':
                 continue 
            classes = 'w-full px-4 py-2 border border-gray-300 rounded-lg outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors'
            if field_name == 'enrollment_number':
                 classes += ' bg-gray-100 cursor-not-allowed'
            field.widget.attrs.update({'class': classes})

    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            profile, created = TeacherProfile.objects.get_or_create(user=user)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            classes = 'w-full px-4 py-2 border border-gray-300 rounded-lg outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors'
            if field_name == 'enrollment_number':
                classes = 'w-full px-4 py-2 border border-gray-300 rounded-r-lg outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'
            field.widget.attrs.update({'class': classes})

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

class StudentEditForm(forms.ModelForm):
    first_name = forms.CharField(label="الاسم الأول", max_length=30)
    last_name = forms.CharField(label="اسم العائلة", max_length=30)
    enrollment_number = forms.CharField(label="رقم القيد", disabled=True, required=False)
    section = forms.ModelChoiceField(label="الفصل / الشعبة", queryset=Section.objects.all(), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['first_name'].initial = self.instance.first_name
            self.fields['last_name'].initial = self.instance.last_name
            self.fields['enrollment_number'].initial = self.instance.username
            try:
                profile = self.instance.student_profile
                self.fields['section'].initial = profile.section
            except StudentProfile.DoesNotExist:
                pass
                
        for field_name, field in self.fields.items():
            classes = 'w-full px-4 py-2 border border-gray-300 rounded-lg outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors'
            if field_name == 'enrollment_number':
                 classes += ' bg-gray-100 cursor-not-allowed'
            field.widget.attrs.update({'class': classes})
            
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            profile, created = StudentProfile.objects.get_or_create(user=user)
            profile.section = self.cleaned_data['section']
            profile.save()
        return user


class GradeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors'
            })
    
    class Meta:
        model = Grade
        fields = ['name']
        labels = {'name': 'اسم الصف (مثال: الأول الثانوي)'}

class SectionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors'
            })
    
    class Meta:
        model = Section
        fields = ['grade', 'name']
        labels = {
            'grade': 'الصف',
            'name': 'اسم الشعبة (مثال: أ, ب)'
        }

class SubjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors'
            })
    
    class Meta:
        model = Subject
        fields = ['name']
        labels = {'name': 'اسم المادة (مثال: رياضيات, فيزياء)'}

class ScheduleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors'
            })

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

