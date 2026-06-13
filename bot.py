"""Binance scalping bot with paper-trading defaults and risk controls.

This is an educational starter bot, not financial advice. It does not guarantee
profit and can lose money if live trading is enabled.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from typing import Literal

import numpy as np
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv

Side = Literal["BUY", "SELL"]


@dataclass(frozen=True)
class Settings:
    api_key: str
    api_secret: str
    testnet: bool
    live_trading: bool
    symbol: str
    interval: str
    account_risk_percent: Decimal
    risk_reward_ratio: Decimal
    max_position_usdt: Decimal
    daily_loss_limit_usdt: Decimal
    stop_loss_percent: Decimal
    fast_ema: int
    slow_ema: int
    rsi_period: int
    rsi_buy_max: Decimal
    rsi_sell_min: Decimal
    poll_seconds: int

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            api_key=os.getenv("BINANCE_API_KEY", ""),
            api_secret=os.getenv("BINANCE_API_SECRET", ""),
            testnet=_env_bool("BINANCE_TESTNET", default=True),
            live_trading=_env_bool("LIVE_TRADING", default=False),
            symbol=os.getenv("SYMBOL", "PAXGUSDT").upper(),
            interval=os.getenv("INTERVAL", Client.KLINE_INTERVAL_1MINUTE),
            account_risk_percent=Decimal(os.getenv("ACCOUNT_RISK_PERCENT", "0.5")),
            risk_reward_ratio=Decimal(os.getenv("RISK_REWARD_RATIO", "1.5")),
            max_position_usdt=Decimal(os.getenv("MAX_POSITION_USDT", "50")),
            daily_loss_limit_usdt=Decimal(os.getenv("DAILY_LOSS_LIMIT_USDT", "10")),
            stop_loss_percent=Decimal(os.getenv("STOP_LOSS_PERCENT", "0.25")),
            fast_ema=int(os.getenv("FAST_EMA", "9")),
            slow_ema=int(os.getenv("SLOW_EMA", "21")),
            rsi_period=int(os.getenv("RSI_PERIOD", "14")),
            rsi_buy_max=Decimal(os.getenv("RSI_BUY_MAX", "65")),
            rsi_sell_min=Decimal(os.getenv("RSI_SELL_MIN", "35")),
            poll_seconds=int(os.getenv("POLL_SECONDS", "15")),
        )


@dataclass(frozen=True)
class TradePlan:
    side: Side
    entry: Decimal
    stop_loss: Decimal
    take_profit: Decimal
    quantity: Decimal
    risk_usdt: Decimal
    reward_usdt: Decimal


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def build_client(settings: Settings) -> Client:
    if not settings.api_key or not settings.api_secret:
        raise ValueError("BINANCE_API_KEY and BINANCE_API_SECRET must be set in .env")
    client = Client(settings.api_key, settings.api_secret, testnet=settings.testnet)
    return client


def fetch_klines(client: Client, symbol: str, interval: str, limit: int = 150) -> pd.DataFrame:
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    frame = pd.DataFrame(
        klines,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_volume",
            "taker_buy_quote_volume",
            "ignore",
        ],
    )
    for column in ["open", "high", "low", "close", "volume"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.dropna().reset_index(drop=True)


def add_indicators(frame: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    enriched = frame.copy()
    enriched["fast_ema"] = enriched["close"].ewm(span=settings.fast_ema, adjust=False).mean()
    enriched["slow_ema"] = enriched["close"].ewm(span=settings.slow_ema, adjust=False).mean()
    enriched["rsi"] = calculate_rsi(enriched["close"], settings.rsi_period)
    return enriched


def calculate_rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    relative_strength = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + relative_strength))


def should_enter_long(latest: pd.Series, settings: Settings) -> bool:
    return (
        latest["fast_ema"] > latest["slow_ema"]
        and latest["close"] > latest["fast_ema"]
        and Decimal(str(latest["rsi"])) <= settings.rsi_buy_max
    )


def build_trade_plan(settings: Settings, account_equity_usdt: Decimal, entry: Decimal) -> TradePlan:
    risk_budget = account_equity_usdt * settings.account_risk_percent / Decimal("100")
    risk_budget = min(risk_budget, settings.daily_loss_limit_usdt)

    stop_distance = entry * settings.stop_loss_percent / Decimal("100")
    stop_loss = entry - stop_distance
    take_profit = entry + (stop_distance * settings.risk_reward_ratio)

    raw_quantity = risk_budget / stop_distance
    max_quantity = settings.max_position_usdt / entry
    quantity = min(raw_quantity, max_quantity).quantize(Decimal("0.000001"), rounding=ROUND_DOWN)

    actual_risk = (entry - stop_loss) * quantity
    actual_reward = (take_profit - entry) * quantity
    return TradePlan(
        side="BUY",
        entry=entry,
        stop_loss=stop_loss,
        take_profit=take_profit,
        quantity=quantity,
        risk_usdt=actual_risk,
        reward_usdt=actual_reward,
    )


def get_usdt_balance(client: Client) -> Decimal:
    account = client.get_account()
    for balance in account["balances"]:
        if balance["asset"] == "USDT":
            return Decimal(balance["free"])
    return Decimal("0")


def execute_trade(client: Client, settings: Settings, plan: TradePlan) -> None:
    logging.info(
        "Trade plan: %s %s qty=%s entry=%s stop=%s target=%s risk=%s reward=%s",
        plan.side,
        settings.symbol,
        plan.quantity,
        plan.entry,
        plan.stop_loss,
        plan.take_profit,
        plan.risk_usdt,
        plan.reward_usdt,
    )

    if not settings.live_trading:
        logging.info("Paper mode: order was not sent to Binance.")
        return

    client.create_order(
        symbol=settings.symbol,
        side=Client.SIDE_BUY,
        type=Client.ORDER_TYPE_MARKET,
        quantity=str(plan.quantity),
    )
    logging.warning(
        "Live market order sent. Place protective stop/target orders according to your account permissions and symbol filters."
    )


def run() -> None:
    configure_logging()
    settings = Settings.from_env()
    client = build_client(settings)
    logging.info("Starting bot for %s | live_trading=%s | testnet=%s", settings.symbol, settings.live_trading, settings.testnet)

    while True:
        try:
            frame = add_indicators(fetch_klines(client, settings.symbol, settings.interval), settings)
            latest = frame.iloc[-1]
            logging.info(
                "close=%.6f fast_ema=%.6f slow_ema=%.6f rsi=%.2f",
                latest["close"],
                latest["fast_ema"],
                latest["slow_ema"],
                latest["rsi"],
            )

            if should_enter_long(latest, settings):
                equity = get_usdt_balance(client)
                plan = build_trade_plan(settings, equity, Decimal(str(latest["close"])))
                if plan.quantity > 0:
                    execute_trade(client, settings, plan)
                else:
                    logging.info("Signal found, but calculated quantity is zero. Check risk settings.")
            else:
                logging.info("No long setup yet.")
        except (BinanceAPIException, ValueError, KeyError, IndexError) as exc:
            logging.error("Bot cycle failed: %s", exc)

        time.sleep(settings.poll_seconds)


if __name__ == "__main__":
    run()
