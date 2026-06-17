from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


REIMBURSEMENT_COLUMNS = [
    "发票代码",
    "发票号码",
    "开票日期",
    "不含税金额",
    "税额",
    "价税合计",
    "币种",
    "原币种费用",
    "汇率",
    "人民币费用",
    "购买方名称",
    "购买方纳税人识别号",
    "销售方名称",
    "销售方纳税人识别号",
]


@dataclass
class InvoiceRecord:
    invoice_code: str = ""
    invoice_number: str = ""
    invoice_date: str = ""
    amount_without_tax: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    currency: str = "CNY"
    original_currency_amount: Optional[float] = None
    exchange_rate: Optional[float] = 1.0
    rmb_amount: Optional[float] = None
    buyer_name: str = ""
    buyer_tax_id: str = ""
    seller_name: str = ""
    seller_tax_id: str = ""
    check_code: str = ""

    source_file: str = ""
    status: str = "成功"
    errors: list[str] = field(default_factory=list)
    raw_text: str = ""

    def to_reimbursement_row(self) -> dict[str, object]:
        return {
            "发票代码": self.invoice_code,
            "发票号码": self.invoice_number,
            "开票日期": self.invoice_date,
            "不含税金额": self.amount_without_tax,
            "税额": self.tax_amount,
            "价税合计": self.total_amount,
            "币种": self.currency,
            "原币种费用": self.original_currency_amount,
            "汇率": self.exchange_rate,
            "人民币费用": self.rmb_amount,
            "购买方名称": self.buyer_name,
            "购买方纳税人识别号": self.buyer_tax_id,
            "销售方名称": self.seller_name,
            "销售方纳税人识别号": self.seller_tax_id,
        }


@dataclass(frozen=True)
class ProcessResult:
    output_dir: Path
    template_file: Path
    reimbursement_file: Path
    log_file: Path
    total: int
    review_count: int
