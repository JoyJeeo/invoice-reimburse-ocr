from invoice_reimburse_ocr.exchange import apply_exchange_rates, build_rate_provider, parse_exchange_rates
from invoice_reimburse_ocr.models import InvoiceRecord


def test_parse_exchange_rates_supports_multiple_items():
    rates = parse_exchange_rates("USD=7.25,EUR=7.80")

    assert rates == {"USD": 7.25, "EUR": 7.8}


def test_apply_exchange_rates_sets_rmb_amount():
    record = InvoiceRecord(currency="USD", total_amount=100.0)
    provider = build_rate_provider({"USD": 7.25}, interactive=False)

    apply_exchange_rates([record], provider)

    assert record.exchange_rate == 7.25
    assert record.rmb_amount == 725.0
