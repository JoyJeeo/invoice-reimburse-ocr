from __future__ import annotations

import re
from datetime import datetime

from .models import InvoiceRecord


def parse_invoice_text(text: str) -> InvoiceRecord:
    normalized = _normalize_text(text)
    record = InvoiceRecord(raw_text=text)
    record.invoice_code = _first_match(normalized, [
        r"发票代码[:：]?\s*(\d{10,12})",
        r"\b(\d{10,12})\b(?=.*发票代码)",
    ])
    record.invoice_number = _first_match(normalized, [
        r"发票号码[:：]?\s*(\d{8,20})",
        r"号码[:：]?\s*(\d{8,20})",
    ])
    record.invoice_date = _normalize_date(_first_match(normalized, [
        r"开票日期[:：]?\s*(\d{4}[年./-]\d{1,2}[月./-]\d{1,2}日?)",
        r"日期[:：]?\s*(\d{4}[年./-]\d{1,2}[月./-]\d{1,2}日?)",
    ]))
    record.amount_without_tax = _parse_amount(_first_match(normalized, [
        r"合计金额[:：]?\s*[￥¥]?\s*([0-9,]+(?:\.\d{1,2})?)",
        r"不含税金额[:：]?\s*[￥¥]?\s*([0-9,]+(?:\.\d{1,2})?)",
        r"金额[:：]?\s*[￥¥]?\s*([0-9,]+(?:\.\d{1,2})?)",
    ]))
    record.tax_amount = _parse_amount(_first_match(normalized, [
        r"合计税额[:：]?\s*[￥¥]?\s*([0-9,]+(?:\.\d{1,2})?)",
        r"税额[:：]?\s*[￥¥]?\s*([0-9,]+(?:\.\d{1,2})?)",
    ]))
    record.total_amount = _parse_amount(_first_match(normalized, [
        r"价税合计(?:\(小写\))?[:：]?\s*[￥¥]?\s*([0-9,]+(?:\.\d{1,2})?)",
        r"含税金额[:：]?\s*[￥¥]?\s*([0-9,]+(?:\.\d{1,2})?)",
    ]))
    record.buyer_name = _first_match(normalized, [
        r"购买方名称[:：]?\s*([^\n]+)",
        r"购买方[\s\S]{0,20}?名称[:：]?\s*([^\n]+)",
    ])
    record.buyer_tax_id = _clean_tax_id(_first_match(normalized, [
        r"购买方纳税人识别号[:：]?\s*([A-Z0-9]{15,25})",
        r"购买方[\s\S]{0,40}?纳税人识别号[:：]?\s*([A-Z0-9]{15,25})",
    ]))
    record.seller_name = _first_match(normalized, [
        r"销售方名称[:：]?\s*([^\n]+)",
        r"销售方[\s\S]{0,20}?名称[:：]?\s*([^\n]+)",
    ])
    record.seller_tax_id = _clean_tax_id(_first_match(normalized, [
        r"销售方纳税人识别号[:：]?\s*([A-Z0-9]{15,25})",
        r"销售方[\s\S]{0,40}?纳税人识别号[:：]?\s*([A-Z0-9]{15,25})",
    ]))
    record.check_code = _first_match(normalized, [r"校验码[:：]?\s*(\d{6,20})"])
    return record


def _normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _first_match(text: str, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip(" ：:;，,")
    return ""


def _normalize_date(value: str) -> str:
    if not value:
        return ""
    cleaned = value.strip().replace("年", "-").replace("月", "-").replace("日", "")
    cleaned = cleaned.replace("/", "-").replace(".", "-")
    try:
        return datetime.strptime(cleaned, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return ""


def _parse_amount(value: str) -> float | None:
    if not value:
        return None
    try:
        return round(float(value.replace(",", "")), 2)
    except ValueError:
        return None


def _clean_tax_id(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", value.upper())
