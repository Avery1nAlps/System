from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users_app.models import Role, UserProfile, UserOperationLog  # 关键：改为users_app

# 内联显示用户扩展信息
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "用户扩展信息"
    fields = ('role', 'department', 'employee_id', 'phone', 'status')
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'role':
            if request.GET.get('department'):
                kwargs['queryset'] = Role.objects.filter(role_code__in=['GENERAL_ACCOUNTANT', 'PURCHASE_ACCOUNTANT', 'SALES_ACCOUNTANT', 'CASHIER', 'ACCOUNTANT_SUPERVISOR'])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# 自定义UserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'employee_id', 'role_name', 'department', 'status', 'is_staff')
    list_filter = ('profile__role__role_name', 'profile__department', 'profile__status')
    search_fields = ('username', 'profile__employee_id', 'profile__role__role_name')

    def employee_id(self, obj):
        return obj.profile.employee_id if hasattr(obj, 'profile') else '未配置'
    employee_id.short_description = "员工编号"

    def role_name(self, obj):
        # 修改点：1. 加判断 obj.profile.role 避免为空；2. 改为 get_role_name_display()
        return obj.profile.role.get_role_name_display() if (hasattr(obj, 'profile') and obj.profile.role) else '未配置'

    role_name.short_description = "角色名称"

    def department(self, obj):
        return obj.profile.department if hasattr(obj, 'profile') else '未配置'
    department.short_description = "所属部门"

    def status(self, obj):
        return obj.profile.get_status_display() if hasattr(obj, 'profile') else '未配置'
    status.short_description = "用户状态"

# 注册角色
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_code', 'role_name', 'related_use_cases', 'create_time')
    search_fields = ('role_code', 'role_name')
    list_filter = ('role_name',)
    readonly_fields = ('create_time',)

# 注册操作日志
@admin.register(UserOperationLog)
class UserOperationLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'operate_type', 'operate_module', 'operate_time', 'ip_address')
    search_fields = ('user__username', 'operate_module', 'operate_content')
    list_filter = ('operate_type', 'operate_module', 'operate_time')
    readonly_fields = ('user', 'operate_type', 'operate_module', 'operate_content', 'operate_time', 'ip_address')
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

# 注册用户扩展信息
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department', 'employee_id', 'phone', 'status')
    search_fields = ('user__username', 'employee_id', 'department', 'role__role_name')
    list_filter = ('role__role_name', 'department', 'status')
    readonly_fields = ('update_time',)

# 注销并重新注册User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)