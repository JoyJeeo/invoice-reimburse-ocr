from __future__ import annotations

from datetime import datetime

from .models import InvoiceRecord


def validate_records(records: list[InvoiceRecord]) -> None:
    seen_numbers: set[str] = set()
    for record in records:
        if record.excluded_from_reimbursement:
            continue

        errors: list[str] = []
        if record.document_type == "发票":
            if not record.invoice_code:
                errors.append("缺少发票代码")
            if not record.invoice_number:
                errors.append("缺少发票号码")
            elif record.invoice_number in seen_numbers:
                errors.append("发票号码重复")
            else:
                seen_numbers.add(record.invoice_number)

        date_value = record.invoice_date if record.document_type == "发票" else record.payment_date
        date_label = "开票日期" if record.document_type == "发票" else "付款日期"
        if not date_value:
            errors.append(f"缺少或无法解析{date_label}")
        else:
            try:
                datetime.strptime(date_value, "%Y-%m-%d")
            except ValueError:
                errors.append(f"{date_label}格式非法")

        amount_fields = [("价税合计", record.total_amount)]
        if record.document_type == "发票":
            amount_fields = [
                ("不含税金额", record.amount_without_tax),
                ("税额", record.tax_amount),
                ("价税合计", record.total_amount),
            ]
        for field_name, value in amount_fields:
            if value is None:
                errors.append(f"缺少{field_name}")
            elif value < 0:
                errors.append(f"{field_name}不能为负数")

        for field_name, tax_id in [
            ("购买方纳税人识别号", record.buyer_tax_id),
            ("销售方纳税人识别号", record.seller_tax_id),
        ]:
            if tax_id and len(tax_id) not in {18, 20}:
                errors.append(f"{field_name}长度异常")

        if record.currency != "CNY":
            if record.exchange_rate is None:
                errors.append("缺少外币汇率")
            elif record.exchange_rate <= 0:
                errors.append("外币汇率必须大于0")
        if record.currency != "CNY" and record.rmb_amount is None and record.total_amount is not None:
            errors.append("缺少人民币费用")

        record.errors.extend(errors)
        record.status = "待人工复核" if record.errors else "成功"
