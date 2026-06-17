from invoice_reimburse_ocr.parser import parse_invoice_text


def test_parse_invoice_text_extracts_core_fields():
    text = """
    增值税电子普通发票
    发票代码: 031002300111
    发票号码: 12345678
    开票日期: 2026年06月17日
    购买方名称: 上海测试科技有限公司
    购买方纳税人识别号: 91310000MA1K000000
    销售方名称: 北京服务有限公司
    销售方纳税人识别号: 91110000MA1K111111
    合计金额: ￥100.50
    合计税额: ￥6.03
    价税合计(小写): ￥106.53
    校验码: 12345678901234567890
    """

    record = parse_invoice_text(text)

    assert record.invoice_code == "031002300111"
    assert record.invoice_number == "12345678"
    assert record.invoice_date == "2026-06-17"
    assert record.amount_without_tax == 100.50
    assert record.tax_amount == 6.03
    assert record.total_amount == 106.53
    assert record.buyer_name == "上海测试科技有限公司"
    assert record.seller_name == "北京服务有限公司"


def test_parse_invoice_text_detects_foreign_currency():
    text = """
    Commercial Invoice
    Currency: USD
    发票代码: 031002300111
    发票号码: 12345678
    开票日期: 2026-06-17
    价税合计: USD 100.50
    """

    record = parse_invoice_text(text)

    assert record.currency == "USD"
