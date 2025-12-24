# finance_app/urls.py
from django.urls import path
from . import views


app_name = 'finance_app'

urlpatterns = [
    # 添加finance根路径，重定向到凭证列表
    path('', views.voucher_list, name='finance_home'),

    # 原有路径保持不变
    path('vouchers/', views.voucher_list, name='voucher_list'),
    path('vouchers/create/', views.voucher_create, name='voucher_create'),
    path('vouchers/<str:voucher_id>/', views.voucher_detail, name='voucher_detail'),
    path('vouchers/<str:voucher_id>/edit/', views.voucher_edit, name='voucher_edit'),
    path('vouchers/<str:voucher_id>/submit/', views.voucher_submit, name='voucher_submit'),

    # 供应商管理
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<str:supplier_id>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<str:supplier_id>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<str:supplier_id>/toggle/', views.supplier_toggle_status, name='supplier_toggle_status'),

    # 客户管理
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<str:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/<str:customer_id>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<str:customer_id>/toggle/', views.customer_toggle_status, name='customer_toggle_status'),
    # AJAX接口保持不变
    path('api/account/<str:account_code>/', views.get_account_info, name='get_account_info'),
    path('api/check-balance/', views.check_voucher_balance, name='check_balance'),

    path('reports/', views.report_home, name='report_home'),
    path('reports/balance-sheet/', views.balance_sheet_list, name='balance_sheet_list'),
    path('reports/balance-sheet/generate/', views.balance_sheet_generate, name='balance_sheet_generate'),
    path('reports/balance-sheet/<str:period>/', views.balance_sheet_detail, name='balance_sheet_detail'),
    path('reports/balance-sheet/<str:period>/edit/', views.balance_sheet_edit, name='balance_sheet_edit'),
    path('reports/balance-sheet/<str:period>/export/', views.export_balance_sheet, name='export_balance_sheet'),

    path('reports/income-statement/', views.income_statement_list, name='income_statement_list'),
    path('reports/income-statement/generate/', views.income_statement_generate, name='income_statement_generate'),
    path('reports/income-statement/<str:period>/', views.income_statement_detail, name='income_statement_detail'),
    path('reports/income-statement/<str:period>/export/', views.export_income_statement,
         name='export_income_statement'),

    # API接口
    path('api/balance-sheet/<str:period>/chart/', views.api_balance_sheet_chart, name='api_balance_sheet_chart'),
    path('api/income-statement/<str:period>/chart/', views.api_income_statement_chart,
         name='api_income_statement_chart'),

    path('reports/generate-direct/', views.generate_report_direct, name='generate_report_direct'),

    # 采购订单
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/create/', views.purchase_order_create, name='purchase_order_create'),
    path('purchase-orders/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('purchase-orders/<int:order_id>/update-status/', views.purchase_order_update_status,
         name='purchase_order_update_status'),

    # 销售订单
    path('sales-orders/', views.sales_order_list, name='sales_order_list'),
    path('sales-orders/create/', views.sales_order_create, name='sales_order_create'),
    path('sales-orders/<int:order_id>/', views.sales_order_detail, name='sales_order_detail'),
]