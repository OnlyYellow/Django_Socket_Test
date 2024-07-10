from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from authentication.models import User


class UserCheck(UserAdmin):
    list_display = ('email', 'user_name', 'is_staff', 'is_active')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'user_name')
    ordering = ('-date_joined',)
    
    # 사용자 수정할 때 입력폼
    fieldsets = (
        ('user', {'fields': ('password',)}),
        ('Personal Info', {'fields': ('user_name',)}),
    )
    
    # 사용자 추가할 때 입력폼
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_name', 'email', 'password1', 'password2')
        }),
    )
    
admin.site.register(User, UserCheck)