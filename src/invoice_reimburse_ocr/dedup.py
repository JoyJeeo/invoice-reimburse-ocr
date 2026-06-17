from __future__ import annotations

from .models import InvoiceRecord


def deduplicate_records(records: list[InvoiceRecord]) -> list[InvoiceRecord]:
    seen_keys: set[tuple[object, ...]] = set()
    kept_records: list[InvoiceRecord] = []

    for record in records:
        key = _dedup_key(record)
        if key and key in seen_keys:
            record.excluded_from_reimbursement = True
            record.status = "重复已去重"
            record.errors.append("重复记录，已从正式报销明细中剔除")
            continue
        if key:
            seen_keys.add(key)
        kept_records.append(record)
    return kept_records


def _dedup_key(record: InvoiceRecord) -> tuple[object, ...] | None:
    if record.document_type == "发票":
        if record.invoice_code and record.invoice_number:
            return ("invoice", record.invoice_code, record.invoice_number)
        if record.invoice_number:
            return ("invoice", record.invoice_number)
        return None

    if record.document_type == "付款记录":
        if record.transaction_id:
            return ("payment", record.transaction_id)
        if record.payment_date and record.total_amount is not None:
            return (
                "payment",
                record.payment_date,
                record.currency,
                record.total_amount,
                record.payer_name,
                record.payee_name,
            )
    return None
