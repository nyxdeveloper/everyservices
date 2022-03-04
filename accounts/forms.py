# django
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = (
            "phone",
            "email",
            "password",
            "first_name",
            "last_name",
            "avatar",
            "approve_email",
            "approve_phone",
            "is_staff",
            "is_superuser",
            "is_active",
            "auto_confirm"
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "phone",
            "email",
            "password",
            "first_name",
            "last_name",
            "avatar",
            "approve_email",
            "approve_phone",
            "is_staff",
            "is_superuser",
            "is_active",
            "auto_confirm"
        )
