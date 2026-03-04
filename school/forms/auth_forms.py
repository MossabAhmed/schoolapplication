from django.contrib.auth.forms import PasswordChangeForm
from django import forms

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        
        # تعريب العناوين والنصوص الإرشادية
        if 'old_password' in self.fields:
            self.fields['old_password'].label = "كلمة المرور الحالية"
        if 'new_password1' in self.fields:
            self.fields['new_password1'].label = "كلمة المرور الجديدة"
            self.fields['new_password1'].help_text = "يجب أن تحتوي كلمة المرور على 8 أحرف على الأقل، ولا تكون مشابهة جداً لمعلوماتك الشخصية أو كلمة مرور شائعة."
        if 'new_password2' in self.fields:
            self.fields['new_password2'].label = "تأكيد كلمة المرور الجديدة"
            self.fields['new_password2'].help_text = "أدخل نفس كلمة المرور الجديدة للتحقق من مطابقتها."

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white shadow-sm'
            })
