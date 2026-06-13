# My-bot-

A Binance scalping-bot starter project focused on strict risk management. It is configured for **paper trading by default** and can be pointed at Binance testnet before any live trading.

> ⚠️ Trading is risky. This bot cannot guarantee profit. Use small position sizes, test thoroughly, and enable live trading only if you accept the risk of financial loss.

## What it trades

The default symbol is `PAXGUSDT`, because PAX Gold (`PAXG`) is commonly used on Binance as a gold-backed asset quoted against USDT. You can change `SYMBOL` in `.env` for another Binance spot symbol.

## Strategy

The bot uses a simple scalping signal:

- Fast EMA above slow EMA
- Price above fast EMA
- RSI below the configured overbought ceiling

When a signal appears, it calculates position size from your configured risk, stop-loss percentage, risk/reward ratio, and maximum position cap. It then simulates or places a market buy, a stop-loss, and a take-profit target.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your Binance API credentials.

## Run safely in paper mode

```bash
python bot.py
```

Paper mode is enabled when `LIVE_TRADING=false`.

## Live trading checklist

Before setting `LIVE_TRADING=true`:

1. Use Binance testnet first (`BINANCE_TESTNET=true`).
2. Confirm the symbol, order sizing, fees, and minimum notional rules.
3. Start with very small `MAX_POSITION_USDT`.
4. Set a realistic `DAILY_LOSS_LIMIT_USDT`.
5. Monitor the bot manually; do not run unattended.

## Environment variables

See `.env.example` for all available settings.
