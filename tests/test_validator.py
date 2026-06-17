from invoice_reimburse_ocr.dedup import deduplicate_records
from invoice_reimburse_ocr.models import InvoiceRecord
from invoice_reimburse_ocr.validator import validate_records


def _valid_record(number: str) -> InvoiceRecord:
    return InvoiceRecord(
        invoice_code="031002300111",
        invoice_number=number,
        invoice_date="2026-06-17",
        amount_without_tax=100.0,
        tax_amount=6.0,
        total_amount=106.0,
    )


def test_deduplicate_records_excludes_duplicate_invoice_number():
    records = [_valid_record("12345678"), _valid_record("12345678")]

    kept = deduplicate_records(records)
    validate_records(records)

    assert records[0].status == "成功"
    assert records[1].status == "重复已去重"
    assert records[1].excluded_from_reimbursement is True
    assert kept == [records[0]]


def test_validate_records_marks_missing_required_fields_for_review():
    record = InvoiceRecord()

    validate_records([record])

    assert record.status == "待人工复核"
    assert "缺少发票代码" in record.errors
    assert "缺少发票号码" in record.errors
    assert "缺少价税合计" in record.errors


def test_validate_payment_record_does_not_require_invoice_fields():
    record = InvoiceRecord(
        document_type="付款记录",
        payment_date="2026-06-17",
        transaction_id="PAY202606170001",
        total_amount=88.66,
    )

    validate_records([record])

    assert record.status == "成功"
