# My-bot-

A Binance scalping-bot starter project focused on strict risk management. It is configured for **paper trading by default** and can be pointed at Binance testnet before any live trading.

> ⚠️ Trading is risky. This bot cannot guarantee profit. Use small position sizes, test thoroughly, and enable live trading only if you accept the risk of financial loss.


## Founder note: why this exists

This bot is designed for one job: help you test a disciplined, repeatable scalping process without gambling from emotion. It observes Binance candle data, orients with simple trend/momentum indicators, decides only when the setup is clear, and acts through a pre-sized trade plan with a defined stop-loss and take-profit.

In plain language: it is not built to predict the future or promise profit. It is built to make risk visible before an order happens. The default pair is `PAXGUSDT` so you can test gold-backed exposure against USDT, and the default mode is paper trading so the first lesson is process, not loss.

### OODA breakdown

1. **Observe** — pull recent Binance candles for the configured symbol.
2. **Orient** — calculate EMA trend and RSI momentum.
3. **Decide** — enter only when the strategy conditions line up.
4. **Act** — create a trade plan with position size, stop-loss, take-profit, and risk/reward before execution.

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
