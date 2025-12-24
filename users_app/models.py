from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# -------------------------- 细化角色模型（完全对应用例执行者） --------------------------
class Role(models.Model):
    ROLE_TYPE_CHOICES = [
        ('ADMIN', '系统管理员'),
        ('GENERAL_ACCOUNTANT', '总账会计'),
        ('PURCHASE_ACCOUNTANT', '采购会计'),
        ('SALES_ACCOUNTANT', '销售会计'),
        ('CASHIER', '出纳'),
        ('ACCOUNTANT_SUPERVISOR', '会计主管'),
        ('EMPLOYEE', '普通员工'),
        ('HR_STAFF', '人事专员'),
    ]
    role_code = models.CharField(max_length=30, primary_key=True, verbose_name="角色编码")
    role_name = models.CharField(max_length=50, choices=ROLE_TYPE_CHOICES, unique=True, verbose_name="角色名称")
    role_desc = models.TextField(blank=True, null=True, verbose_name="角色描述")
    related_use_cases = models.TextField(blank=True, null=True, verbose_name="关联用例（编号）")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = "角色"
        ordering = ['role_code']

    def __str__(self):
        return self.get_role_name_display()

# -------------------------- 用户扩展信息 --------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="关联用户")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, verbose_name="所属角色")
    department = models.CharField(max_length=50, verbose_name="所属部门")
    employee_id = models.CharField(max_length=20, unique=True, verbose_name="员工编号")
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name="联系电话")
    status = models.CharField(
        max_length=20,
        choices=[('ACTIVE', '启用'), ('INACTIVE', '停用')],
        default='ACTIVE',
        verbose_name="状态"
    )
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "用户扩展信息"
        verbose_name_plural = "用户扩展信息"
        ordering = ['employee_id']

    def __str__(self):
        return f"{self.user.username} - {self.role.get_role_name_display()} - {self.department}"

# -------------------------- 用户操作日志模型 --------------------------
class UserOperationLog(models.Model):
    OPERATE_TYPE_CHOICES = [
        ('LOGIN', '登录系统'),
        ('CREATE', '创建数据'),
        ('UPDATE', '修改数据'),
        ('DELETE', '删除数据'),
        ('AUDIT', '审核数据'),
        ('EXPORT', '导出数据'),
        ('BACKUP', '备份数据'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operation_logs', verbose_name="操作用户")
    operate_type = models.CharField(max_length=20, choices=OPERATE_TYPE_CHOICES, verbose_name="操作类型")
    operate_module = models.CharField(max_length=50, verbose_name="操作模块")
    operate_content = models.TextField(verbose_name="操作内容")
    operate_time = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    ip_address = models.CharField(max_length=50, blank=True, null=True, verbose_name="IP地址")

    class Meta:
        verbose_name = "用户操作日志"
        verbose_name_plural = "用户操作日志"
        ordering = ['-operate_time']

    def __str__(self):
        return f"{self.user.username} - {self.get_operate_type_display()} - {self.operate_module} - {self.operate_time}"