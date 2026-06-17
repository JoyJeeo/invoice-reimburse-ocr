from pathlib import Path

from openpyxl import load_workbook

from invoice_reimburse_ocr.models import REIMBURSEMENT_COLUMNS
from invoice_reimburse_ocr.ocr import SidecarTextOCREngine
from invoice_reimburse_ocr.pipeline import process_folder


def test_process_folder_exports_clean_reimbursement_file(tmp_path: Path):
    input_dir = tmp_path / "inputs"
    input_dir.mkdir()
    image_file = input_dir / "invoice.jpg"
    image_file.write_bytes(b"fake image bytes")
    image_file.with_suffix(".txt").write_text(
        """
        发票代码: 031002300111
        发票号码: 12345678
        开票日期: 2026-06-17
        合计金额: 100.50
        合计税额: 6.03
        价税合计: 106.53
        购买方名称: 上海测试科技有限公司
        购买方纳税人识别号: 91310000MA1K000000
        销售方名称: 北京服务有限公司
        销售方纳税人识别号: 91110000MA1K111111
        """,
        encoding="utf-8",
    )

    result = process_folder(input_dir, tmp_path, SidecarTextOCREngine())

    assert result.total == 1
    assert result.review_count == 0
    assert result.template_file.exists()
    assert result.reimbursement_file.exists()
    assert result.log_file.exists()

    wb = load_workbook(result.reimbursement_file)
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    assert headers == REIMBURSEMENT_COLUMNS
    assert "原始文件名" not in headers
    assert "识别状态" not in headers
    assert ws.cell(row=2, column=6).value == 106.53
