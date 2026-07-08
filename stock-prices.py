from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import math
import pandas as pd
import yfinance as yf

TSX_TICKERS: List[str] = ['BMO.TO']

NYSE_TICKERS: List[str] = ['LLY', 'FIX', 'VOO', 'VTI', 'LIN', 'ANET', 'SPMO']

NASDAQ_TICKERS: List[str] = ['MU', 'AMD', 'GOOGL', 'CDNS', 'KLAC', 'LRCX', 'QQQM', 'RKLB']

@dataclass
class StockSnapshot:
    ticker: str
    exchange: str
    currency: str
    close: Optional[float]
    daily_change_pct: Optional[float]
    weekly_change_pct: Optional[float]
    monthly_change_pct: Optional[float]
    six_month_change_pct: Optional[float]
    ytd_pct: Optional[float]


def pct_change(current: float, previous: float) -> Optional[float]:
    if previous is None or current is None or previous == 0 or math.isnan(previous) or math.isnan(current):
        return None
    return round(((current - previous) / previous) * 100, 2)


def latest_valid_close(series: pd.Series, on_or_before: pd.Timestamp) -> Optional[float]:
    eligible = series[series.index <= on_or_before].dropna()
    if eligible.empty:
        return None
    return float(eligible.iloc[-1])


def compute_period_changes(history: pd.DataFrame) -> Dict[str, Optional[float]]:
    closes = history['Close'].dropna()
    if closes.empty:
        return {
            'close': None,
            'daily_change_pct': None,
            'weekly_change_pct': None,
            'monthly_change_pct': None,
            'six_month_change_pct': None,
            'ytd_pct': None,
        }

    current_date = closes.index[-1]
    current_close = float(closes.iloc[-1])

    previous_day_close = float(closes.iloc[-2]) if len(closes) >= 2 else None
    one_week_close = latest_valid_close(closes, current_date - pd.Timedelta(days=7))
    one_month_close = latest_valid_close(closes, current_date - pd.DateOffset(months=1))
    six_month_close = latest_valid_close(closes, current_date - pd.DateOffset(months=6))
    ytd_close = latest_valid_close(closes, current_date - pd.DateOffset(years=1))

    return {
        'close': round(current_close, 2),
        'daily_change_pct': pct_change(current_close, previous_day_close),
        'weekly_change_pct': pct_change(current_close, one_week_close),
        'monthly_change_pct': pct_change(current_close, one_month_close),
        'six_month_change_pct': pct_change(current_close, six_month_close),
        'ytd_pct': pct_change(current_close, ytd_close),
    }


def fetch_stock_snapshot(ticker: str, exchange: str) -> StockSnapshot:
    stock = yf.Ticker(ticker)

    history = stock.history(period='1y', interval='1d', auto_adjust=False)
    info = stock.fast_info if hasattr(stock, 'fast_info') else {}
    currency = info.get('currency') or 'N/A'

    metrics = compute_period_changes(history)

    return StockSnapshot(
        ticker=ticker,
        exchange=exchange,
        currency=currency,
        close=metrics['close'],
        daily_change_pct=metrics['daily_change_pct'],
        weekly_change_pct=metrics['weekly_change_pct'],
        monthly_change_pct=metrics['monthly_change_pct'],
        six_month_change_pct=metrics['six_month_change_pct'],
        ytd_pct=metrics['ytd_pct'],
    )


def fetch_exchange_data(exchange: str, tickers: List[str]) -> List[StockSnapshot]:
    results: List[StockSnapshot] = []

    for ticker in tickers:
        try:
            results.append(fetch_stock_snapshot(ticker, exchange))
        except Exception as exc:
            results.append(
                StockSnapshot(
                    ticker=ticker,
                    exchange=exchange,
                    currency='N/A',
                    close=None,
                    daily_change_pct=None,
                    weekly_change_pct=None,
                    monthly_change_pct=None,
                    six_month_change_pct=None,
                    ytd_pct=None,
                )
            )
            print(f'Failed to fetch {ticker}: {exc}')

    return results


def main() -> None:
    all_results = []
    all_results.extend(fetch_exchange_data('TSX', TSX_TICKERS))
    all_results.extend(fetch_exchange_data('NYSE', NYSE_TICKERS))
    all_results.extend(fetch_exchange_data('NASDAQ', NASDAQ_TICKERS))

    df = pd.DataFrame([asdict(row) for row in all_results])

    output_file = 'stock-prices.csv'
    df.to_csv(output_file, index=False)

    print(df.to_string(index=False))
    print(f'\nSaved output to {output_file}')


if __name__ == '__main__':
    main()
