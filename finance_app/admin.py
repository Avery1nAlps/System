# 导入Django后台管理模块和我们创建的三个模型
from django.contrib import admin
from .models import PurchaseOrder, SalesOrder
from .models import Account, Customer, Supplier, Voucher, JournalEntry, GeneralLedger, BalanceSheet, IncomeStatement, ReportPeriod

# -------------------------- 注册会计科目模型 --------------------------
@admin.register(Account)  # 装饰器方式注册模型
class AccountAdmin(admin.ModelAdmin):
    # 后台列表页面显示的字段（对应模型的属性）
    list_display = ('account_code', 'account_name', 'account_type', 'parent_account', 'balance_direction', 'status', 'create_time')
    # 可搜索的字段（输入关键词能搜索对应字段内容）
    search_fields = ('account_code', 'account_name')  # 按科目代码、科目名称搜索
    # 可筛选的字段（右侧出现筛选栏）
    list_filter = ('account_type', 'balance_direction', 'status')
    # 排序方式（默认按科目代码升序排列）
    ordering = ('account_code',)

# -------------------------- 注册客户模型 --------------------------
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'customer_name', 'credit_limit', 'current_receivable', 'status', 'create_time')
    search_fields = ('customer_id', 'customer_name')  # 按客户ID、客户名称搜索
    list_filter = ('status',)  # 按状态筛选
    ordering = ('customer_id',)

# -------------------------- 注册供应商模型 --------------------------
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_id', 'supplier_name', 'current_payable', 'payment_terms', 'status', 'create_time')
    search_fields = ('supplier_id', 'supplier_name')  # 按供应商ID、供应商名称搜索
    list_filter = ('status',)  # 按状态筛选
    ordering = ('supplier_id',)

# -------------------------- 注册会计凭证模型 --------------------------
@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('voucher_id', 'voucher_date', 'description', 'total_debit', 'total_credit', 'status', 'created_by', 'audited_by', 'create_time')
    search_fields = ('voucher_id', 'description')  # 按凭证编号、摘要搜索
    list_filter = ('status', 'voucher_date', 'created_by')  # 按状态、日期、制单人筛选
    ordering = ('-voucher_date', '-voucher_id')  # 按日期倒序，凭证编号倒序
    # 添加一个内联显示，方便查看分录明细
    inlines = []

# -------------------------- 注册分录明细模型 --------------------------
class JournalEntryInline(admin.TabularInline):
    """内联显示分录明细"""
    model = JournalEntry
    extra = 1  # 默认显示1个空行
    fields = ('account', 'direction', 'amount', 'description', 'customer', 'supplier')
    # 限制每行显示字段数量，使界面更紧凑

@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('voucher', 'account', 'direction', 'amount', 'description', 'customer', 'supplier', 'create_time')
    search_fields = ('account__account_name', 'description', 'voucher__voucher_id')  # 按科目名称、摘要、凭证编号搜索
    list_filter = ('direction', 'account__account_type')  # 按借贷方向、科目类型筛选
    ordering = ('-create_time',)  # 按创建时间倒序

# 将内联添加到VoucherAdmin
VoucherAdmin.inlines = [JournalEntryInline]

# -------------------------- 注册总分类账模型 --------------------------
@admin.register(GeneralLedger)
class GeneralLedgerAdmin(admin.ModelAdmin):
    list_display = ('period', 'account', 'opening_balance', 'opening_direction',
                    'debit_total', 'credit_total', 'ending_balance', 'ending_direction', 'update_time')
    search_fields = ('period', 'account__account_code', 'account__account_name')  # 按期间、科目代码、科目名称搜索
    list_filter = ('period', 'account__account_type', 'ending_direction')  # 按期间、科目类型、期末方向筛选
    ordering = ('-period', 'account__account_code')  # 按期间倒序，科目代码正序
    # 添加只读字段
    readonly_fields = ('ending_balance', 'ending_direction', 'update_time')

# -------------------------- 注册资产负债表模型 --------------------------
@admin.register(BalanceSheet)
class BalanceSheetAdmin(admin.ModelAdmin):
    list_display = ('period', 'current_assets', 'fixed_assets', 'intangible_assets', 'other_assets',
                    'current_liabilities', 'long_term_liabilities', 'paid_in_capital',
                    'retained_earnings', 'current_profit', 'total_assets', 'total_liabilities',
                    'total_equity', 'is_balanced', 'balance_diff', 'is_final', 'report_date')
    search_fields = ('period',)  # 按期间搜索
    list_filter = ('period', 'is_final', 'is_balanced')  # 按期间、是否定稿、是否平衡筛选
    ordering = ('-period',)  # 按期间倒序
    # 添加只读字段
    readonly_fields = ('total_assets', 'total_liabilities', 'total_equity', 'is_balanced', 'balance_diff', 'report_date')

# -------------------------- 注册利润表模型 --------------------------
@admin.register(IncomeStatement)
class IncomeStatementAdmin(admin.ModelAdmin):
    list_display = ('period', 'operating_revenue', 'other_revenue', 'operating_cost',
                    'selling_expenses', 'admin_expenses', 'financial_expenses',
                    'other_income', 'other_expenses', 'tax_expense',
                    'total_revenue', 'total_cost_expense', 'gross_profit',
                    'operating_profit', 'profit_before_tax', 'net_profit',
                    'is_final', 'report_date')
    search_fields = ('period',)  # 按期间搜索
    list_filter = ('period', 'is_final')  # 按期间、是否定稿筛选
    ordering = ('-period',)  # 按期间倒序
    # 添加只读字段
    readonly_fields = ('total_revenue', 'total_cost_expense', 'gross_profit',
                      'operating_profit', 'profit_before_tax', 'net_profit', 'report_date')

# -------------------------- 注册报表期间模型 --------------------------
@admin.register(ReportPeriod)
class ReportPeriodAdmin(admin.ModelAdmin):
    list_display = ('period_code', 'period_name', 'start_date', 'end_date',
                    'is_closed', 'closed_by', 'closed_date')
    search_fields = ('period_code', 'period_name')  # 按期间代码、期间名称搜索
    list_filter = ('is_closed',)  # 按是否结账筛选
    ordering = ('-period_code',)  # 按期间代码倒序



@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'supplier', 'product_name', 'quantity',
                    'unit_price', 'total_amount', 'status', 'order_date']
    list_filter = ['status', 'order_date', 'supplier']
    search_fields = ['order_number', 'supplier__name', 'product_name']
    readonly_fields = ['created_time', 'updated_time', 'order_number']
    fieldsets = (
        ('基本信息', {
            'fields': ('order_number', 'supplier', 'order_date', 'expected_date', 'status')
        }),
        ('商品信息', {
            'fields': ('product_name', 'quantity', 'unit_price', 'total_amount')
        }),
        ('财务信息', {
            'fields': ('tax_amount', 'paid_amount')
        }),
        ('其他信息', {
            'fields': ('notes', 'created_by', 'created_time', 'updated_time')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'product_name', 'quantity',
                    'unit_price', 'total_amount', 'status', 'order_date']
    list_filter = ['status', 'order_date', 'customer']
    search_fields = ['order_number', 'customer__name', 'product_name']
    readonly_fields = ['created_time', 'updated_time', 'order_number']
    fieldsets = (
        ('基本信息', {
            'fields': ('order_number', 'customer', 'order_date', 'delivery_date', 'status')
        }),
        ('商品信息', {
            'fields': ('product_name', 'quantity', 'unit_price', 'total_amount')
        }),
        ('运输信息', {
            'fields': ('shipping_address', 'shipping_method')
        }),
        ('财务信息', {
            'fields': ('tax_amount', 'received_amount')
        }),
        ('其他信息', {
            'fields': ('notes', 'created_by', 'created_time', 'updated_time')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)