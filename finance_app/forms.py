# finance_app/forms.py
from django import forms
from .models import Voucher, JournalEntry, Account,Customer, Supplier


class JournalEntryForm(forms.ModelForm):
    """单个分录表单"""
    # 将外键字段改为CharField，用于文本输入
    customer = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '客户名称'
        }),
        label='客户'
    )

    supplier = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '供应商名称'
        }),
        label='供应商'
    )

    class Meta:
        model = JournalEntry
        fields = ['account', 'direction', 'amount', 'description', 'customer', 'supplier']
        widgets = {
            'account': forms.Select(attrs={'class': 'form-control'}),
            'direction': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '摘要'}),
        }


class VoucherForm(forms.ModelForm):
    """凭证主表表单"""

    class Meta:
        model = Voucher
        fields = ['voucher_date', 'description']
        widgets = {
            'voucher_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '请输入凭证摘要'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置默认日期为今天
        from datetime import date
        if not self.instance.pk:
            self.initial['voucher_date'] = date.today()


class SupplierForm(forms.ModelForm):
    """供应商表单"""

    class Meta:
        model = Supplier
        fields = ['supplier_id', 'supplier_name', 'payment_terms', 'bank_account']
        widgets = {
            'supplier_id': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier_name': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_terms': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_supplier_id(self):
        supplier_id = self.cleaned_data.get('supplier_id')
        # 检查ID是否已存在（除了当前编辑的实例）
        if self.instance and self.instance.supplier_id == supplier_id:
            return supplier_id
        if Supplier.objects.filter(supplier_id=supplier_id).exists():
            raise forms.ValidationError('该供应商ID已存在')
        return supplier_id


class CustomerForm(forms.ModelForm):
    """客户表单"""

    class Meta:
        model = Customer
        fields = ['customer_id', 'customer_name', 'credit_limit', 'current_receivable', 'contact_info']
        widgets = {
            'customer_id': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'credit_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'value': '0.00'
            }),
            'current_receivable': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'value': '0.00'
            }),
            'contact_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入联系电话、地址等联系信息'
            }),
        }
        labels = {
            'current_receivable': '当前应收账款',
            'credit_limit': '信用额度',
            'contact_info': '联系信息',
        }
        help_texts = {
            'current_receivable': '客户当前的应收账款余额',
            'credit_limit': '为客户设置的信用额度上限',
            'contact_info': '可输入电话、地址、联系人等信息',
        }

    def clean_customer_id(self):
        customer_id = self.cleaned_data.get('customer_id')
        # 检查ID是否已存在（除了当前编辑的实例）
        if self.instance and self.instance.customer_id == customer_id:
            return customer_id
        if Customer.objects.filter(customer_id=customer_id).exists():
            raise forms.ValidationError('该客户ID已存在')
        return customer_id

    def clean_credit_limit(self):
        """验证信用额度不能为负数"""
        credit_limit = self.cleaned_data.get('credit_limit')
        if credit_limit and credit_limit < 0:
            raise forms.ValidationError('信用额度不能为负数')
        return credit_limit

    def clean_current_receivable(self):
        """验证应收账款不能为负数"""
        current_receivable = self.cleaned_data.get('current_receivable')
        if current_receivable and current_receivable < 0:
            raise forms.ValidationError('应收账款不能为负数')
        return current_receivable

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置默认值
        if not self.instance.pk:  # 如果是新建
            self.initial['current_receivable'] = 0.00
            self.initial['credit_limit'] = 0.00