from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError


# -------------------------- 会计科目表（accounts） --------------------------
class Account(models.Model):
    # 科目类型枚举（对应你的ENUM类型）
    ACCOUNT_TYPE_CHOICES = [
        ('ASSET', '资产类'),
        ('LIABILITY', '负债类'),
        ('EQUITY', '所有者权益类'),
        ('COST', '成本类'),
        ('PROFIT', '损益类'),
    ]
    # 余额方向枚举
    BALANCE_DIRECTION_CHOICES = [
        ('DEBIT', '借方'),
        ('CREDIT', '贷方'),
    ]
    # 状态枚举
    STATUS_CHOICES = [
        ('ACTIVE', '启用'),
        ('INACTIVE', '停用'),
    ]

    # 对应表字段
    account_code = models.CharField(max_length=20, primary_key=True, verbose_name="科目代码")
    account_name = models.CharField(max_length=100, null=False, blank=False, verbose_name="科目名称")
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        null=False,
        blank=False,
        verbose_name="科目类型"
    )
    # 父级科目（外键关联自身，on_delete=SET_NULL表示父科目删除时，子科目父级置空；related_name用于反向查询子科目）
    parent_account = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_accounts',
        verbose_name="父级科目"
    )
    balance_direction = models.CharField(
        max_length=10,
        choices=BALANCE_DIRECTION_CHOICES,
        null=False,
        blank=False,
        verbose_name="余额方向"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        null=False,
        blank=False,
        default='ACTIVE',
        verbose_name="状态"
    )
    # 新增创建/更新时间（便于追溯，可选但推荐）
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'accounts'  # 显式指定数据库表名，与你的表名一致
        verbose_name = "会计科目"
        verbose_name_plural = "会计科目"
        ordering = ['account_code']  # 按科目代码排序

    def __str__(self):
        # 打印对象时显示「科目代码-科目名称」，便于后台管理查看
        return f"{self.account_code} - {self.account_name}"


# -------------------------- 客户表（customers） --------------------------
class Customer(models.Model):
    # 状态枚举
    STATUS_CHOICES = [
        ('ACTIVE', '启用'),
        ('INACTIVE', '停用'),
    ]

    # 对应表字段
    customer_id = models.CharField(
        max_length=20,
        primary_key=True,
        verbose_name="客户ID",
        # 添加验证器，防止空值
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9_-]+$',
                message='客户ID只能包含字母、数字、下划线和连字符',
                code='invalid_customer_id'
            ),
            MinLengthValidator(1, message='客户ID不能为空')
        ],
        error_messages={
            'unique': '客户ID已存在',
            'max_length': '客户ID不能超过20个字符',
        }
    )
    customer_name = models.CharField(max_length=100, null=False, blank=False, verbose_name="客户名称")
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, null=False, blank=False,
                                       verbose_name="信用额度")
    current_receivable = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                             verbose_name="当前应收账款")
    contact_info = models.TextField(null=True, blank=True, verbose_name="联系信息")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        null=False,
        blank=False,
        default='ACTIVE',
        verbose_name="状态"
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'customers'  # 显式指定数据库表名
        verbose_name = "客户"
        verbose_name_plural = "客户"
        ordering = ['customer_id']

    def __str__(self):
        return f"{self.customer_id} - {self.customer_name}"


# -------------------------- 供应商表（suppliers） --------------------------
class Supplier(models.Model):
    # 状态枚举
    STATUS_CHOICES = [
        ('ACTIVE', '启用'),
        ('INACTIVE', '停用'),
    ]

    # 对应表字段
    supplier_id = models.CharField(max_length=20, primary_key=True, verbose_name="供应商ID")
    supplier_name = models.CharField(max_length=100, null=False, blank=False, verbose_name="供应商名称")
    payment_terms = models.CharField(max_length=50, null=True, blank=True, verbose_name="付款条件")
    current_payable = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                          verbose_name="当前应付账款")
    bank_account = models.CharField(max_length=50, null=True, blank=True, verbose_name="银行账号")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        null=False,
        blank=False,
        default='ACTIVE',
        verbose_name="状态"
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'suppliers'  # 显式指定数据库表名
        verbose_name = "供应商"
        verbose_name_plural = "供应商"
        ordering = ['supplier_id']

    def __str__(self):
        return f"{self.supplier_id} - {self.supplier_name}"


# -------------------------- 会计凭证核心模型 --------------------------

class Voucher(models.Model):
    """会计凭证主表"""
    STATUS_CHOICES = [
        ('DRAFT', '草稿'),
        ('SUBMITTED', '已提交'),
        ('AUDITED', '已审核'),
        ('POSTED', '已过账'),
    ]

    # 凭证编号（自动生成：V2024010001）
    voucher_id = models.CharField(max_length=20, unique=True, verbose_name="凭证编号")
    voucher_date = models.DateField(default=timezone.now, verbose_name="凭证日期")
    description = models.TextField(verbose_name="摘要")

    # 借贷总额（自动计算）
    total_debit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="借方总额")
    total_credit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="贷方总额")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        verbose_name="状态"
    )

    # 关联信息
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        related_name='created_vouchers',
        verbose_name="制单人"
    )
    audited_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audited_vouchers',
        verbose_name="审核人"
    )

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    audit_time = models.DateTimeField(null=True, blank=True, verbose_name="审核时间")

    class Meta:
        db_table = 'vouchers'
        verbose_name = "会计凭证"
        verbose_name_plural = "会计凭证"
        ordering = ['-voucher_date', 'voucher_id']

    def __str__(self):
        return f"{self.voucher_id} - {self.description[:30]}"

    def save(self, *args, **kwargs):
        # 自动生成凭证编号
        if not self.voucher_id:
            today = timezone.now().strftime('%Y%m')
            last_voucher = Voucher.objects.filter(
                voucher_id__startswith=f"V{today}"
            ).order_by('voucher_id').last()

            if last_voucher:
                last_num = int(last_voucher.voucher_id[-4:])
                new_num = last_num + 1
            else:
                new_num = 1

            self.voucher_id = f"V{today}{new_num:04d}"

        super().save(*args, **kwargs)

    def is_balanced(self):
        """检查借贷是否平衡"""
        return self.total_debit == self.total_credit


class JournalEntry(models.Model):
    """分录明细表"""
    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        related_name='entries',
        verbose_name="所属凭证"
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        verbose_name="会计科目"
    )

    # 借贷方向
    direction = models.CharField(
        max_length=10,
        choices=[('DEBIT', '借方'), ('CREDIT', '贷方')],
        verbose_name="方向"
    )

    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="金额")
    description = models.CharField(max_length=200, verbose_name="摘要", blank=True)

    # 辅助核算（可选）
    customer = models.CharField(
        max_length=100,
        verbose_name="客户",
        blank=True,
        null=True
    )
    supplier = models.CharField(
        max_length=100,
        verbose_name="供应商",
        blank=True,
        null=True
    )

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'journal_entries'
        verbose_name = "分录明细"
        verbose_name_plural = "分录明细"
        ordering = ['voucher', 'id']

    def __str__(self):
        return f"{self.voucher.voucher_id} - {self.account.account_name}"


class GeneralLedger(models.Model):
    """总分类账（用于财务报表）"""
    period = models.CharField(max_length=6, verbose_name="会计期间")  # 格式：202401
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name="科目")

    # 期初余额
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="期初余额")
    opening_direction = models.CharField(
        max_length=10,
        choices=[('DEBIT', '借方'), ('CREDIT', '贷方')],
        default='DEBIT',
        verbose_name="期初方向"
    )

    # 本期发生额
    debit_total = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="本期借方")
    credit_total = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="本期贷方")

    # 期末余额（自动计算）
    ending_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="期末余额")
    ending_direction = models.CharField(
        max_length=10,
        choices=[('DEBIT', '借方'), ('CREDIT', '贷方')],
        default='DEBIT',
        verbose_name="期末方向"
    )

    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'general_ledger'
        verbose_name = "总分类账"
        verbose_name_plural = "总分类账"
        unique_together = [['period', 'account']]

    def __str__(self):
        return f"{self.period}-{self.account.account_code}"

    def calculate_ending_balance(self):
        """计算期末余额"""
        if self.opening_direction == 'DEBIT':
            balance = self.opening_balance + self.debit_total - self.credit_total
        else:
            balance = self.opening_balance + self.credit_total - self.debit_total

        if balance >= 0:
            self.ending_direction = self.opening_direction
            self.ending_balance = balance
        else:
            self.ending_direction = 'DEBIT' if self.opening_direction == 'CREDIT' else 'CREDIT'
            self.ending_balance = abs(balance)

        return self.ending_balance


# -------------------------- 财务报表相关 --------------------------


class FinancialReport(models.Model):
    """财务报表基类"""
    REPORT_TYPE_CHOICES = [
        ('BALANCE', '资产负债表'),
        ('INCOME', '利润表'),
        ('CASH_FLOW', '现金流量表'),
    ]

    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, verbose_name="报表类型")
    period = models.CharField(max_length=6, verbose_name="会计期间")  # 格式：202401
    report_date = models.DateTimeField(auto_now_add=True, verbose_name="生成日期")
    generated_by = models.ForeignKey('auth.User', on_delete=models.PROTECT, verbose_name="生成人")
    is_final = models.BooleanField(default=False, verbose_name="是否定稿")

    class Meta:
        abstract = True
        ordering = ['-period', '-report_date']


class BalanceSheet(models.Model):
    """资产负债表"""
    period = models.CharField(max_length=6, unique=True, verbose_name="会计期间")
    report_date = models.DateTimeField(auto_now_add=True, verbose_name="生成日期")
    generated_by = models.ForeignKey('auth.User', on_delete=models.PROTECT, verbose_name="生成人")
    is_final = models.BooleanField(default=False, verbose_name="是否定稿")

    # 资产类
    current_assets = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="流动资产")
    fixed_assets = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="固定资产")
    intangible_assets = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="无形资产")
    other_assets = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="其他资产")

    # 负债类
    current_liabilities = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="流动负债")
    long_term_liabilities = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="长期负债")

    # 所有者权益类
    paid_in_capital = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="实收资本")
    retained_earnings = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="留存收益")
    current_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="本期利润")

    # 计算字段
    total_assets = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="资产总计")
    total_liabilities = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="负债总计")
    total_equity = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="所有者权益总计")

    # 平衡检查
    is_balanced = models.BooleanField(default=False, verbose_name="是否平衡")
    balance_diff = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="平衡差额")

    class Meta:
        db_table = 'balance_sheets'
        verbose_name = "资产负债表"
        verbose_name_plural = "资产负债表"
        ordering = ['-period']

    def __str__(self):
        return f"{self.period}资产负债表"

    def save(self, *args, **kwargs):
        # 计算总计
        self.total_assets = (
                self.current_assets +
                self.fixed_assets +
                self.intangible_assets +
                self.other_assets
        )

        self.total_liabilities = (
                self.current_liabilities +
                self.long_term_liabilities
        )

        self.total_equity = (
                self.paid_in_capital +
                self.retained_earnings +
                self.current_profit
        )

        # 检查平衡：资产 = 负债 + 所有者权益
        total_right = self.total_liabilities + self.total_equity
        self.balance_diff = self.total_assets - total_right
        self.is_balanced = abs(self.balance_diff) < 0.01  # 允许0.01的误差

        super().save(*args, **kwargs)


class IncomeStatement(models.Model):
    """利润表"""
    period = models.CharField(max_length=6, unique=True, verbose_name="会计期间")
    report_date = models.DateTimeField(auto_now_add=True, verbose_name="生成日期")
    generated_by = models.ForeignKey('auth.User', on_delete=models.PROTECT, verbose_name="生成人")
    is_final = models.BooleanField(default=False, verbose_name="是否定稿")

    # 营业收入
    operating_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="营业收入")
    other_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="其他收入")

    # 营业成本
    operating_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="营业成本")

    # 期间费用
    selling_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="销售费用")
    admin_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="管理费用")
    financial_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="财务费用")

    # 其他收支
    other_income = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="其他收益")
    other_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="其他支出")

    # 税金
    tax_expense = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="所得税费用")

    # 计算字段
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="收入总计")
    total_cost_expense = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="成本费用总计")
    gross_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="毛利润")
    operating_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="营业利润")
    profit_before_tax = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="利润总额")
    net_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="净利润")

    class Meta:
        db_table = 'income_statements'
        verbose_name = "利润表"
        verbose_name_plural = "利润表"
        ordering = ['-period']

    def __str__(self):
        return f"{self.period}利润表"

    def save(self, *args, **kwargs):
        # 计算各个利润指标
        self.total_revenue = self.operating_revenue + self.other_revenue

        self.total_cost_expense = (
                self.operating_cost +
                self.selling_expenses +
                self.admin_expenses +
                self.financial_expenses
        )

        self.gross_profit = self.operating_revenue - self.operating_cost

        self.operating_profit = (
                self.gross_profit -
                self.selling_expenses -
                self.admin_expenses -
                self.financial_expenses
        )

        self.profit_before_tax = (
                self.operating_profit +
                self.other_income -
                self.other_expenses
        )

        self.net_profit = self.profit_before_tax - self.tax_expense

        super().save(*args, **kwargs)


class ReportPeriod(models.Model):
    """报表期间管理"""
    period_code = models.CharField(max_length=6, unique=True, verbose_name="期间代码")
    period_name = models.CharField(max_length=50, verbose_name="期间名称")
    start_date = models.DateField(verbose_name="开始日期")
    end_date = models.DateField(verbose_name="结束日期")
    is_closed = models.BooleanField(default=False, verbose_name="是否已结账")
    closed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="结账人")
    closed_date = models.DateTimeField(null=True, blank=True, verbose_name="结账日期")

    class Meta:
        db_table = 'report_periods'
        verbose_name = "报表期间"
        verbose_name_plural = "报表期间"
        ordering = ['-period_code']

    def __str__(self):
        return f"{self.period_name} ({'已结账' if self.is_closed else '未结账'})"


class PurchaseOrder(models.Model):
    """采购订单"""
    ORDER_STATUS = [
        ('DRAFT', '草稿'),
        ('SUBMITTED', '已提交'),
        ('APPROVED', '已审核'),
        ('RECEIVED', '已收货'),
        ('CANCELLED', '已取消'),
    ]

    order_number = models.CharField('订单编号', max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='供应商')
    order_date = models.DateField('订单日期', default=timezone.now)
    expected_date = models.DateField('预计到货日期', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=ORDER_STATUS, default='DRAFT')

    # 金额信息
    total_amount = models.DecimalField('订单总额', max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField('税额', max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField('已付金额', max_digits=12, decimal_places=2, default=0)

    # 商品信息（简化版，可以只有商品名称和数量）
    product_name = models.CharField('商品名称', max_length=200)
    quantity = models.DecimalField('数量', max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2, default=0)

    # 备注信息
    notes = models.TextField('备注', blank=True)

    # 系统字段
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '采购订单'
        verbose_name_plural = '采购订单'
        ordering = ['-order_date', '-created_time']

    def __str__(self):
        return f'{self.order_number} - {self.supplier.name}'

    def save(self, *args, **kwargs):
        # 自动生成订单编号（如果为空）
        if not self.order_number:
            today = timezone.now().strftime('%Y%m%d')
            last_order = PurchaseOrder.objects.filter(
                order_number__startswith=f'PO{today}'
            ).order_by('-order_number').first()

            if last_order:
                last_num = int(last_order.order_number[10:])
                self.order_number = f'PO{today}{last_num + 1:04d}'
            else:
                self.order_number = f'PO{today}0001'

        # 自动计算总额
        self.total_amount = self.quantity * self.unit_price

        super().save(*args, **kwargs)


class SalesOrder(models.Model):
    """销售订单"""
    ORDER_STATUS = [
        ('DRAFT', '草稿'),
        ('SUBMITTED', '已提交'),
        ('APPROVED', '已审核'),
        ('DELIVERED', '已发货'),
        ('INVOICED', '已开票'),
        ('PAID', '已收款'),
        ('CANCELLED', '已取消'),
    ]

    order_number = models.CharField('订单编号', max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='客户')
    order_date = models.DateField('订单日期', default=timezone.now)
    delivery_date = models.DateField('交货日期', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=ORDER_STATUS, default='DRAFT')

    # 金额信息
    total_amount = models.DecimalField('订单总额', max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField('税额', max_digits=12, decimal_places=2, default=0)
    received_amount = models.DecimalField('已收金额', max_digits=12, decimal_places=2, default=0)

    # 商品信息
    product_name = models.CharField('商品名称', max_length=200)
    quantity = models.DecimalField('数量', max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2, default=0)

    # 运输信息
    shipping_address = models.TextField('送货地址', blank=True)
    shipping_method = models.CharField('运输方式', max_length=50, blank=True)

    # 备注信息
    notes = models.TextField('备注', blank=True)

    # 系统字段
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '销售订单'
        verbose_name_plural = '销售订单'
        ordering = ['-order_date', '-created_time']

    def __str__(self):
        return f'{self.order_number} - {self.customer.name}'

    def save(self, *args, **kwargs):
        # 自动生成订单编号
        if not self.order_number:
            today = timezone.now().strftime('%Y%m%d')
            last_order = SalesOrder.objects.filter(
                order_number__startswith=f'SO{today}'
            ).order_by('-order_number').first()

            if last_order:
                last_num = int(last_order.order_number[10:])
                self.order_number = f'SO{today}{last_num + 1:04d}'
            else:
                self.order_number = f'SO{today}0001'

        # 自动计算总额
        self.total_amount = self.quantity * self.unit_price

        super().save(*args, **kwargs)