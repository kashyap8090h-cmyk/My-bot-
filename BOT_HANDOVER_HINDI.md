# Binance Scalping Bot — Handover File

यह file bot के purpose, design, setup, configuration, और safety rules को simple Hindi/Hinglish में explain करती है. आप इस file को email attachment के रूप में भेज सकते हैं.

## 1. Bot kis kaam ke liye design kiya gaya hai?

यह bot Binance पर एक disciplined scalping process test करने के लिए बनाया गया है. इसका goal emotional trading को कम करना और हर trade से पहले risk साफ दिखाना है.

Bot default रूप से live trade नहीं करता. पहले यह paper mode में trade plan log करता है ताकि आप strategy, position size, stop-loss, take-profit और risk/reward ratio समझ सकें.

Important: यह bot profit guarantee नहीं करता. Market risk हमेशा रहता है.

## 2. Default market / symbol

Default symbol:

```text
PAXGUSDT
```

PAXG Binance पर gold-backed asset माना जाता है और USDT quote currency है. इसलिए यह setup gold exposure बनाम USDT test करने के लिए use किया गया है.

## 3. OODA framework

Bot का decision flow OODA loop पर based है:

1. **Observe** — Binance से latest candle data pull करता है.
2. **Orient** — EMA और RSI indicators calculate करता है.
3. **Decide** — strategy conditions match हों तो entry signal बनाता है.
4. **Act** — trade plan बनाता है: quantity, stop-loss, take-profit, risk और reward.

## 4. Strategy logic

Bot long entry consider करता है जब:

- Fast EMA slow EMA से ऊपर हो.
- Current close price fast EMA से ऊपर हो.
- RSI configured max level से नीचे या equal हो.

Default settings:

```text
FAST_EMA=9
SLOW_EMA=21
RSI_PERIOD=14
RSI_BUY_MAX=65
```

## 5. Risk management

Bot position size blindly नहीं लेता. यह calculate करता है:

- Account risk percent
- Stop-loss distance
- Risk/reward ratio
- Maximum position cap
- Daily loss limit

Default risk settings:

```text
ACCOUNT_RISK_PERCENT=0.5
RISK_REWARD_RATIO=1.5
MAX_POSITION_USDT=50
DAILY_LOSS_LIMIT_USDT=10
STOP_LOSS_PERCENT=0.25
```

Example: अगर entry price 2000 USDT है और stop-loss 0.25% है, तो stop distance 5 USDT होगा. Bot quantity इस हिसाब से size करेगा कि risk budget से ज्यादा loss expose न हो.

## 6. Safety defaults

`.env.example` में safe defaults रखे गए हैं:

```text
BINANCE_TESTNET=true
LIVE_TRADING=false
```

इसका मतलब:

- पहले Binance testnet/sandbox use करें.
- Bot real money order नहीं भेजेगा जब तक `LIVE_TRADING=true` manually set न किया जाए.

## 7. Setup commands

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

फिर `.env` file में Binance API key और secret डालें.

## 8. Run command

Paper mode में run करें:

```bash
python bot.py
```

## 9. Live trading se pehle checklist

Live trading enable करने से पहले:

1. Binance testnet पर strategy run करके देखें.
2. Symbol filters, minimum notional, fees और quantity precision confirm करें.
3. बहुत छोटा `MAX_POSITION_USDT` रखें.
4. `DAILY_LOSS_LIMIT_USDT` realistic रखें.
5. Bot को unattended न चलाएँ.
6. Profit guarantee expect न करें.

## 10. Files included

- `bot.py` — main Binance scalping bot code.
- `.env.example` — configuration template.
- `requirements.txt` — Python dependencies.
- `.gitignore` — local secrets/cache ignore rules.
- `README.md` — setup and strategy documentation.
- `BOT_HANDOVER_HINDI.md` — यह handover/details file.

## 11. Email note

Assistant direct email send नहीं कर सकता. इस file को manually attach करके email भेजें:

```text
To: hbatham8353@gmail.com
Subject: Binance Scalping Bot Handover
Attachment: BOT_HANDOVER_HINDI.md
```

## 12. Final warning

Trading में capital loss हो सकता है. यह project educational starter है, financial advice नहीं. Live trading से पहले paper testing, backtesting और manual review जरूरी है.
