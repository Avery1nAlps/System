# generate_ledger.py - 生成总分类账数据
import os
import sys
import django

# 设置Django环境
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accounting_proj.settings')

try:
    django.setup()
    print("✅ Django 环境设置成功")
except Exception as e:
    print(f"❌ 设置失败: {e}")
    sys.exit(1)

from finance_app.models import Voucher, JournalEntry, Account, GeneralLedger
from django.db.models import Sum, Q
from collections import defaultdict


def generate_general_ledger_for_all_periods():
    """为所有期间生成总分类账"""
    print("🔄 开始生成总分类账...")

    # 1. 获取所有已审核的凭证
    approved_vouchers = Voucher.objects.filter(status__in=['AUDITED', 'POSTED'])

    if not approved_vouchers.exists():
        print("❌ 没有找到已审核的凭证！请先审核一些凭证。")
        return

    print(f"找到 {approved_vouchers.count()} 张已审核凭证")

    # 2. 按期间分组凭证
    period_vouchers = defaultdict(list)

    for voucher in approved_vouchers:
        # 从凭证编号提取期间 (V2025010001 -> 202501)
        if voucher.voucher_id.startswith('V') and len(voucher.voucher_id) >= 7:
            period = voucher.voucher_id[1:7]
            if period.isdigit():
                period_vouchers[period].append(voucher)

    if not period_vouchers:
        print("❌ 无法从凭证编号中提取期间信息")
        return

    print(f"发现 {len(period_vouchers)} 个期间: {list(period_vouchers.keys())}")

    total_created = 0

    # 3. 为每个期间生成总分类账
    for period, voucher_list in period_vouchers.items():
        print(f"\n📅 处理期间: {period} ({len(voucher_list)}张凭证)")

        # 获取该期间所有分录
        entries = JournalEntry.objects.filter(voucher__in=voucher_list)

        if not entries.exists():
            print(f"  ⚠️ 期间 {period} 没有分录")
            continue

        # 按科目统计借贷发生额
        account_stats = entries.values('account').annotate(
            debit_sum=Sum('amount', filter=Q(direction='DEBIT')),
            credit_sum=Sum('amount', filter=Q(direction='CREDIT'))
        )

        period_created = 0

        for stat in account_stats:
            account = Account.objects.get(id=stat['account'])

            # 获取或创建总分类账记录
            ledger, created = GeneralLedger.objects.get_or_create(
                period=period,
                account=account,
                defaults={
                    'opening_balance': 0,  # 假设期初为0
                    'opening_direction': account.balance_direction,
                    'debit_total': stat['debit_sum'] or 0,
                    'credit_total': stat['credit_sum'] or 0,
                }
            )

            if not created:
                # 更新已有记录（累加）
                ledger.debit_total += stat['debit_sum'] or 0
                ledger.credit_total += stat['credit_sum'] or 0

            # 计算期末余额
            ledger.calculate_ending_balance()
            ledger.save()

            if created:
                period_created += 1
                if period_created <= 5:  # 只显示前5个
                    print(f"  ✅ 创建: {account.account_code} - {account.account_name}")

        total_created += period_created
        print(f"  本期创建/更新了 {period_created} 个科目")

    # 4. 显示结果
    print(f"\n{'=' * 50}")
    print(f"🎉 总分类账生成完成！")
    print(f"总计创建/更新了 {total_created} 条记录")
    print(f"总分类账总记录数: {GeneralLedger.objects.count()}")

    # 5. 显示一些示例
    if GeneralLedger.objects.exists():
        print(f"\n📋 总分类账示例（前5条）:")
        samples = GeneralLedger.objects.select_related('account')[:5]
        for ledger in samples:
            print(f"  {ledger.period} - {ledger.account.account_name}: {ledger.ending_balance}")


def check_current_data():
    """检查当前数据状态"""
    print("\n🔍 当前数据状态检查")
    print("=" * 50)

    # 1. 凭证数据
    print("\n📄 会计凭证:")
    total_vouchers = Voucher.objects.count()
    approved_vouchers = Voucher.objects.filter(status__in=['AUDITED', 'POSTED']).count()
    print(f"  总数: {total_vouchers}")
    print(f"  已审核: {approved_vouchers}")

    if approved_vouchers > 0:
        # 显示最近的凭证
        recent = Voucher.objects.filter(status__in=['AUDITED', 'POSTED']).order_by('-voucher_date')[:3]
        for v in recent:
            print(f"    {v.voucher_id} - {v.voucher_date} - {v.description[:30]}")

    # 2. 分录数据
    print(f"\n📝 分录明细:")
    entry_count = JournalEntry.objects.count()
    print(f"  总数: {entry_count}")

    if entry_count > 0:
        # 显示一些分录
        entries = JournalEntry.objects.select_related('voucher', 'account')[:3]
        for e in entries:
            print(f"    {e.voucher.voucher_id} - {e.account.account_name} - {e.direction} {e.amount}")

    # 3. 总分类账
    print(f"\n📊 总分类账:")
    ledger_count = GeneralLedger.objects.count()
    print(f"  总数: {ledger_count}")

    if ledger_count == 0:
        print("  ⚠️ 总分类账为空！需要生成数据")

    return approved_vouchers > 0


if __name__ == '__main__':
    print("=" * 60)
    print("财务系统 - 总分类账生成工具")
    print("=" * 60)

    # 先检查数据
    has_approved_vouchers = check_current_data()

    if has_approved_vouchers:
        # 询问是否生成
        print(f"\n❓ 是否要生成总分类账数据？")
        response = input("   输入 'yes' 确认生成，其他键取消: ")

        if response.lower() == 'yes':
            generate_general_ledger_for_all_periods()
        else:
            print("操作已取消")
    else:
        print("\n❌ 没有已审核的凭证，无法生成总分类账")
        print("请先：")
        print("1. 在 Django Admin 中审核一些凭证")
        print("2. 确保凭证状态为 'AUDITED' 或 'POSTED'")
        print("3. 重新运行此脚本")