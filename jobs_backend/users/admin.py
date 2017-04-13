from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import UserChangeForm, UserCreationForm
from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'name', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff')

    fieldsets = (
                (None, {'fields': ('email', 'password')}),
                ('Personal info', {'fields': ('name',)}),
                ('Permissions', {'fields': ('is_active', 'is_staff')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2')
        }),
    )

    search_fields = ('email', 'name')
    ordering = ('email',)
    filter_horizontal = ()
    readonly_fields = ('last_login',)
