# django
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Client


class ClientAdmin(ModelAdmin):
    model = Client
    list_display = (
        'user', 'name', 'phone', 'email', 'blacklist', 'comment', 'blacklist_comment', 'created',
    )
    list_filter = ('blacklist', 'created',)
    fieldsets = (
        (None, {'fields': ('user',)}),
        ("Основная информация", {'fields': (('name', 'phone', 'email'),)}),
        ("Дополнительная информация", {'fields': (('comment', 'blacklist_comment'),)}),
    )
    search_fields = ('user__first_name', 'user__last_name', 'name', 'phone', 'email', 'comment', 'blacklist_comment',)
    ordering = (
        'user', 'name', 'phone', 'email', 'blacklist', 'comment', 'blacklist_comment', 'created',
    )


admin.site.register(Client, ClientAdmin)
