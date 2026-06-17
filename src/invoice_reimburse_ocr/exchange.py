from __future__ import annotations

from collections.abc import Callable

from .models import InvoiceRecord


RateProvider = Callable[[str], float]


def parse_exchange_rates(value: str | None) -> dict[str, float]:
    if not value:
        return {}

    rates: dict[str, float] = {}
    for item in value.split(","):
        if not item.strip():
            continue
        if "=" not in item:
            raise ValueError(f"汇率格式错误：{item}，应为 USD=7.25")
        currency, rate = item.split("=", 1)
        currency = currency.strip().upper()
        if not currency:
            raise ValueError("币种不能为空")
        parsed_rate = float(rate.strip())
        if parsed_rate <= 0:
            raise ValueError(f"{currency} 汇率必须大于 0")
        rates[currency] = parsed_rate
    return rates


def apply_exchange_rates(records: list[InvoiceRecord], rate_provider: RateProvider) -> None:
    for record in records:
        amount = record.total_amount
        if amount is None:
            continue

        record.original_currency_amount = amount
        if record.currency == "CNY":
            record.exchange_rate = 1.0
        else:
            record.exchange_rate = rate_provider(record.currency)
        record.rmb_amount = round(amount * record.exchange_rate, 2)


def build_rate_provider(initial_rates: dict[str, float], interactive: bool = True) -> RateProvider:
    rates = {currency.upper(): rate for currency, rate in initial_rates.items()}

    def provide(currency: str) -> float:
        normalized_currency = currency.upper()
        if normalized_currency in rates:
            return rates[normalized_currency]
        if not interactive:
            raise ValueError(f"缺少 {normalized_currency} 转人民币汇率")

        while True:
            raw_value = input(f"检测到 {normalized_currency} 外币发票，请输入转换到人民币的汇率：").strip()
            try:
                rate = float(raw_value)
            except ValueError:
                print("汇率必须是数字，请重新输入。")
                continue
            if rate <= 0:
                print("汇率必须大于 0，请重新输入。")
                continue
            rates[normalized_currency] = rate
            return rate

    return provide
