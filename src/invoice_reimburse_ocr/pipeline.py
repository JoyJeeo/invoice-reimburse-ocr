from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .dedup import deduplicate_records
from .exporter import create_run_output_dir, export_processing_log, export_reimbursement, export_template
from .exchange import RateProvider, apply_exchange_rates
from .file_scanner import discover_input_files
from .models import InvoiceRecord, ProcessResult
from .ocr import OCREngine
from .parser import parse_invoice_text
from .validator import validate_records


def process_folder(
    input_dir: Path,
    output_base_dir: Path,
    ocr_engine: OCREngine,
    rate_provider: RateProvider | None = None,
) -> ProcessResult:
    timestamp = datetime.now()
    output_dir = create_run_output_dir(output_base_dir, timestamp)
    files = discover_input_files(input_dir)
    if not files:
        raise ValueError(f"输入目录中未发现支持的图片或PDF文件：{input_dir}")

    records: list[InvoiceRecord] = []
    total_files = len(files)
    for index, file_path in enumerate(files, start=1):
        print(f"[{index}/{total_files}] 正在处理：{file_path.name}")
        try:
            text = ocr_engine.extract_text(file_path)
            record = parse_invoice_text(text)
        except Exception as exc:
            record = InvoiceRecord(status="待人工复核", errors=[str(exc)])
        record.source_file = str(file_path)
        records.append(record)

    if rate_provider is None:
        rate_provider = lambda currency: 1.0
    apply_exchange_rates(records, rate_provider)
    reimbursement_records = deduplicate_records(records)
    validate_records(records)
    template_file = export_template(output_dir)
    reimbursement_file = export_reimbursement(reimbursement_records, output_dir, timestamp)
    log_file = export_processing_log(records, output_dir)
    return ProcessResult(
        output_dir=output_dir,
        template_file=template_file,
        reimbursement_file=reimbursement_file,
        log_file=log_file,
        total=len(records),
        review_count=sum(1 for record in records if record.status == "待人工复核"),
    )
