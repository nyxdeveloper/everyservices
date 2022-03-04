# django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User
from helpdesk.models import HelpdeskMessage


class HelpdeskMessagesUserInline(admin.StackedInline):
    model = HelpdeskMessage
    fk_name = "user"
    extra = 0


class HelpdeskMessagesToInline(admin.StackedInline):
    model = HelpdeskMessage
    fk_name = "to"
    extra = 0


class HelpdeskMessagesInline(admin.TabularInline):
    model = HelpdeskMessage
    inlines = [HelpdeskMessagesUserInline, HelpdeskMessagesToInline]
    fk_name = "user"


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = (
        'name', 'phone', 'email', 'is_active', 'is_staff', 'is_superuser', 'approve_email',
        'approve_phone', 'auto_confirm', 'rating', 'min_record_time'
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'approve_email', 'approve_phone', 'auto_confirm',)
    fieldsets = (
        ('Основная информация', {'fields': (('first_name', 'last_name'), 'avatar', 'phone', 'email', 'password')}),
        ('Права', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('Прочее', {'fields': ('approve_email', 'approve_phone', 'auto_confirm')}),
        ('Подписка', {'fields': ('service_package',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'email', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser')}
         ),
    )
    search_fields = ('email', 'phone', 'first_name', 'last_name',)
    ordering = (
        'phone', 'email', 'is_active', 'is_staff', 'is_superuser', 'approve_email', 'approve_phone',
        'auto_confirm'
    )
    inlines = (HelpdeskMessagesUserInline, HelpdeskMessagesToInline)


admin.site.register(User, CustomUserAdmin)
