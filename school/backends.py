from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        
        try:
            # Try to fetch the user by username first (For Admins)
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            # If not found by username, try fetching by enrollment_number (For Teachers and Students)
            try:
                user = UserModel.objects.get(enrollment_number=username)
            except UserModel.DoesNotExist:
                return None
        
        # Check if the fetched user has the correct password and is active
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
