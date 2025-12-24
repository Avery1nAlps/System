# diagnose_finance.py
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accounting_proj.settings')
django.setup()

from finance_app.models import Voucher, JournalEntry, Account, BalanceSheet, IncomeStatement
from django.db.models import Sum, Q

print("=" * 80)
print("💰 财务系统数据诊断")
print("=" * 80)


def check_all_data():
    """检查所有数据"""

    # 1. 检查凭证
    print("\n1. 📄 会计凭证检查")
    print("-" * 40)

    total_vouchers = Voucher.objects.count()
    submitted_vouchers = Voucher.objects.filter(status='SUBMITTED').count()

    print(f"总凭证数: {total_vouchers}")
    print(f"已提交凭证: {submitted_vouchers}")

    vouchers = Voucher.objects.filter(status='SUBMITTED')[:5]
    for v in vouchers:
        print(f"\n  凭证: {v.voucher_id}")
        print(f"    日期: {v.voucher_date}")
        print(f"    摘要: {v.description}")
        print(f"    状态: {v.status}")

        # 检查分录
        entries = v.entries.all()
        print(f"    分录数: {entries.count()}")

        for entry in entries:
            print(f"      → {entry.account.account_code} - {entry.account.account_name}")
            print(f"          方向: {entry.direction}, 金额: {entry.amount}")
            print(f"          科目类型: {entry.account.account_type}")

    # 2. 检查科目
    print("\n2. 🔢 会计科目检查")
    print("-" * 40)

    total_accounts = Account.objects.count()
    print(f"总科目数: {total_accounts}")

    # 按类型统计
    for acc_type in ['ASSET', 'LIABILITY', 'EQUITY', 'PROFIT']:
        count = Account.objects.filter(account_type=acc_type).count()
        print(f"  {acc_type}: {count}个")

    # 显示关键科目
    print("\n  关键科目示例:")
    key_accounts = Account.objects.filter(account_code__in=['1002', '1122', '2221', '6001'])
    for acc in key_accounts:
        print(f"    {acc.account_code} - {acc.account_name} ({acc.account_type})")

    # 3. 检查分录总额
    print("\n3. 📝 分录总额检查")
    print("-" * 40)

    total_debit = JournalEntry.objects.filter(direction='DEBIT').aggregate(Sum('amount'))['amount__sum'] or 0
    total_credit = JournalEntry.objects.filter(direction='CREDIT').aggregate(Sum('amount'))['amount__sum'] or 0

    print(f"借方总额: {total_debit}")
    print(f"贷方总额: {total_credit}")
    print(f"平衡检查: {'✅ 平衡' if abs(total_debit - total_credit) < 0.01 else '❌ 不平衡'}")

    # 4. 按期间分析
    print("\n4. 📅 按期间分析")
    print("-" * 40)

    # 获取所有凭证编号中的期间
    periods = set()
    for v in Voucher.objects.all():
        if v.voucher_id.startswith('V') and len(v.voucher_id) >= 7:
            period = v.voucher_id[1:7]
            if period.isdigit():
                periods.add(period)

    print(f"发现的期间: {sorted(periods)}")

    for period in sorted(periods):
        print(f"\n  期间 {period}:")

        # 获取该期间的凭证
        period_vouchers = []
        for v in Voucher.objects.all():
            if v.voucher_id.startswith('V') and v.voucher_id[1:7] == period:
                period_vouchers.append(v)

        print(f"    凭证数: {len(period_vouchers)}")

        # 计算该期间的分录总额
        period_entries = JournalEntry.objects.filter(voucher__in=period_vouchers)
        period_debit = period_entries.filter(direction='DEBIT').aggregate(Sum('amount'))['amount__sum'] or 0
        period_credit = period_entries.filter(direction='CREDIT').aggregate(Sum('amount'))['amount__sum'] or 0

        print(f"    借方总额: {period_debit}")
        print(f"    贷方总额: {period_credit}")

        # 按科目类型统计
        print(f"    按科目类型统计:")
        for acc_type in ['ASSET', 'LIABILITY', 'EQUITY', 'PROFIT']:
            type_entries = period_entries.filter(account__account_type=acc_type)
            type_debit = type_entries.filter(direction='DEBIT').aggregate(Sum('amount'))['amount__sum'] or 0
            type_credit = type_entries.filter(direction='CREDIT').aggregate(Sum('amount'))['amount__sum'] or 0
            print(f"      {acc_type}: 借{type_debit} 贷{type_credit}")

    # 5. 检查科目余额方向
    print("\n5. 🧭 科目余额方向检查")
    print("-" * 40)

    for acc in Account.objects.all()[:10]:  # 显示前10个
        print(f"    {acc.account_code} - {acc.account_name}: {acc.balance_direction}")

    # 6. 验证函数逻辑
    print("\n6. 🔧 验证生成逻辑")
    print("-" * 40)

    # 选择一个期间进行测试
    if periods:
        test_period = sorted(periods)[0]
        print(f"测试期间: {test_period}")

        # 模拟生成逻辑
        test_balance_sheet(test_period)
        test_income_statement(test_period)


def test_balance_sheet(period):
    """测试资产负债表生成逻辑"""
    print(f"\n  资产负债表测试 - 期间: {period}")

    # 获取该期间的凭证
    period_vouchers = []
    for v in Voucher.objects.all():
        if v.voucher_id.startswith('V') and v.voucher_id[1:7] == period:
            period_vouchers.append(v)

    if not period_vouchers:
        print("    ❌ 该期间没有凭证")
        return

    # 初始化
    current_assets = 0

    # 遍历分录
    for v in period_vouchers:
        for entry in v.entries.all():
            account = entry.account

            if account.account_type == 'ASSET':
                # 资产类：借方增加，贷方减少
                net_effect = entry.amount if entry.direction == 'DEBIT' else -entry.amount

                # 只统计流动资产
                if account.account_code in ['1001', '1002', '1121', '1122', '1221']:
                    current_assets += net_effect
                    print(
                        f"    {account.account_code} - {account.account_name}: {entry.direction} {entry.amount} → 流动资产({net_effect})")

    print(f"    流动资产总计: {current_assets}")


def test_income_statement(period):
    """测试利润表生成逻辑"""
    print(f"\n  利润表测试 - 期间: {period}")

    # 获取该期间的凭证
    period_vouchers = []
    for v in Voucher.objects.all():
        if v.voucher_id.startswith('V') and v.voucher_id[1:7] == period:
            period_vouchers.append(v)

    if not period_vouchers:
        print("    ❌ 该期间没有凭证")
        return

    # 初始化
    operating_revenue = 0

    # 遍历分录
    for v in period_vouchers:
        for entry in v.entries.all():
            account = entry.account

            if account.account_type == 'PROFIT':
                # 损益类科目
                if account.balance_direction == 'CREDIT':  # 收入类
                    net_amount = entry.amount if entry.direction == 'CREDIT' else -entry.amount
                else:  # 费用类
                    net_amount = entry.amount if entry.direction == 'DEBIT' else -entry.amount

                if '主营业务收入' in account.account_name or account.account_code == '6001':
                    operating_revenue += net_amount
                    print(
                        f"    {account.account_code} - {account.account_name}: {entry.direction} {entry.amount} → 营业收入({net_amount})")

    print(f"    营业收入总计: {operating_revenue}")


if __name__ == '__main__':
    check_all_data()
    print("\n" + "=" * 80)
    print("诊断完成")
    print("=" * 80)