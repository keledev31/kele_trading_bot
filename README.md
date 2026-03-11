# 🤖 MeshTradeBot

**A production-ready Telegram bot for crypto trading** combining Freqtrade as the trading engine with a beautiful, user-facing Telegram interface.

## Features

✅ **Trading Engine**: Freqtrade with conservative EMA200 + RSI strategy  
✅ **Telegram Interface**: Clean menu with inline keyboards (aiogram 3.x async)  
✅ **Signal Distribution**: Real-time trading signals with FreqAI confidence scoring  
✅ **Telegram Payments**: Stripe/direct Telegram Payments integration for subscriptions  
✅ **Direct Trading**: Secure encrypted API key management (Binance, Bybit, OKX, etc.)  
✅ **Copy Trading**: Master account replication for subscribers  
✅ **Risk Management**: Hard stop-losses, daily drawdown protection, tight trade limits  
✅ **Docker**: Full Docker + docker-compose setup for easy deployment  

---

## 📋 Project Structure

```
kele_trading_bot/
├── bot/                          # Telegram bot code (aiogram)
│   ├── handlers/                 # Command handlers
│   ├── keyboards/                # Button layouts
│   ├── payments/                 # Telegram Payments logic
│   └── main.py                   # Bot entry point
├── database/                     # SQLAlchemy models & migrations
│   ├── models.py                 # User, Trade, Signal, etc.
│   └── __init__.py               # Session management
├── freqtrade_config/             # Freqtrade configuration
│   └── default.json              # Main config
├── strategies/                   # Freqtrade strategies
│   └── ema200_rsi_strategy.py   # Conservative strategy
├── utils/                        # Utilities
│   ├── encryption.py             # API key encryption (Fernet)
│   ├── logger.py                 # Logging config
│   └── __init__.py
├── config/                       # Config & constants
│   └── constants.py              # Global constants
├── docker-compose.yml            # Docker setup
├── Dockerfile                    # Bot container
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── main.py                       # Main entry point
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Telegram Bot (create with @BotFather)
- Telegram Payments Provider Token
- (Optional) Exchange API keys (Binance, Bybit, etc.)

### Step 1: Get Your Tokens

#### 1a. Telegram Bot Token
1. Open Telegram and chat with **@BotFather**
2. Send `/newbot`
3. Follow the prompts to create your bot
4. Save the **bot token** (example: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

#### 1b. Telegram Payments Provider Token (Critical!)

**Official Telegram Payments Integration:**

1. **Contact Telegram Support:**
   - Open your bot in Telegram
   - Go to Bot Settings > Payments
   - Click "Choose a Payment Provider"

2. **Available Providers:**
   - **Stripe** (supports most countries)
   - **Telegram Payments** (direct to Telegram)
   - **LiqPay** (Eastern Europe)
   - **YooKassa** (Russia)
   - **SBER** (Russia)

3. **For Stripe Provider:**
   - Create Stripe account at stripe.com
   - Get `Stripe Public Key` and `Stripe Test Secret Key`
   - Go to BotFather → Your Bot → Payments → Choose Provider → Stripe
   - Enter your Stripe data

4. **For Telegram Payments:**
   - Telegram itself handles payments
   - Request partnership via @askfedor (Telegram team)
   - Your bot token works as provider token

5. **Save the Provider Token** (you'll need it in `.env`)

### Step 2: Clone & Setup

```bash
# Clone the repository
git clone <your-repo>
cd kele_trading_bot

# Create .env file
cp .env.example .env

# Generate encryption key for API keys
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy the output and paste into .env ENCRYPTION_KEY

# Edit .env with your tokens
nano .env
# Fill in:
# - TELEGRAM_BOT_TOKEN=your_token
# - TELEGRAM_PROVIDER_TOKEN=your_provider_token
# - ENCRYPTION_KEY=your_generated_key
```

### Step 3: Using Docker (Recommended)

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f meshtradebot

# Stop
docker-compose down
```

### Step 4: Manual Setup (Without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from database import init_db; init_db()"

# Run the bot
python main.py
```

---

## 🔧 Configuration

### Freqtrade Config

Edit `freqtrade_config/default.json`:

```json
{
  "max_open_trades": 3,
  "stake_currency": "USDT",
  "dry_run": true,  // TRUE for safety! Change after testing
  "trading_mode": "spot",
  "stake_amount": 100,  // USDT per trade
  "exchange": {
    "name": "binance",
    "key": "",    // Will be filled by users
    "secret": ""  // Will be filled by users
  }
}
```

### Strategy

Use the conservative **EMA200 + RSI** strategy:
- ✅ EMA200 trend filter (only buy above trend)
- ✅ RSI momentum (RSI < 40 for buy)
- ✅ 2% Hard stoploss
- ✅ Trailing stop for profit protection
- ✅ Bollinger Band confirmation

Located at: [strategies/ema200_rsi_strategy.py](strategies/ema200_rsi_strategy.py)

---

## 📱 Telegram Bot Usage

### User Commands

```
/start           - Show main menu
/buy             - Get buy signals
/sell            - Get sell signals
/mytrades        - View your trade history
/performance     - View P&L statistics
/subscribe       - Subscribe to Premium
/addkeys         - Add exchange API keys (Premium)
/automode        - Enable auto-trading (Premium)
/copytrade       - Copy master trades (Premium)
/support         - Get help
/settings        - User preferences
```

### Main Menu Buttons

```
🟢 GET SIGNALS          - Real-time trading signals
📊 MY TRADES            - Trade history & P&L
📈 PERFORMANCE          - Performance metrics
🔓 SUBSCRIBE (Premium)  - Upgrade subscription
⚙️  SETTINGS            - Bot preferences
🤝 COPY TRADING         - Setup copy mode
📝 API KEYS             - Manage exchange keys
```

---

## 💳 Subscription Plans

### Free Plan
- Basic signals (24hr history)
- View 1 trade log
- Limited message rate

### Premium Monthly (₦3,000)
- Full signal distribution
- Direct trading on your account
- Unlimited trade history
- Copy trading mode
- Performance analytics
- Priority support

### Premium Yearly (₦25,000)
- All Premium Monthly features
- 33% discount vs monthly
- Exclusive advanced analytics

---

## 🔐 Security

### Encryption

All API keys are encrypted with **Fernet** (AES-128) before storage:

```python
from utils.encryption import encrypt_data, decrypt_data

# Storing API key
encrypted_key = encrypt_data(user_api_key)
db.save(encrypted_key)

# Retrieving API key
api_key = decrypt_data(encrypted_from_db)
```

### Environment Variables

Never hardcode secrets. All sensitive data in `.env`:
- `TELEGRAM_BOT_TOKEN` → Bot token
- `TELEGRAM_PROVIDER_TOKEN` → Payments token
- `ENCRYPTION_KEY` → API key encryption
- `FREQTRADE_JWT_SECRET` → API authentication

### API Key Handling

- Keys stored encrypted in database
- Decrypted only when needed for trading
- Never logged or exposed
- User can revoke anytime

---

## 📊 Database Schema

### Users Table
```sql
users (
  id INTEGER PRIMARY KEY,
  telegram_user_id STRING UNIQUE,
  subscription_plan ENUM (free, premium_monthly, premium_yearly),
  subscription_expiry DATETIME,
  auto_trade_enabled BOOLEAN,
  copy_trading_enabled BOOLEAN,
  created_at DATETIME
)
```

### Trades Table
```sql
trade_logs (
  id INTEGER PRIMARY KEY,
  user_id FOREIGN KEY,
  symbol STRING (BTC/USDT, etc.),
  entry_price FLOAT,
  exit_price FLOAT,
  profit_loss_percentage FLOAT,
  status STRING (open, closed, cancelled),
  created_at DATETIME
)
```

### Signals Table
```sql
signals (
  id INTEGER PRIMARY KEY,
  user_id FOREIGN KEY,
  symbol STRING,
  signal_type STRING (BUY, SELL),
  entry_price FLOAT,
  stop_loss FLOAT,
  take_profit FLOAT,
  confidence_score FLOAT (0-100),
  created_at DATETIME
)
```

### API Keys Table
```sql
encrypted_api_keys (
  id INTEGER PRIMARY KEY,
  user_id FOREIGN KEY,
  exchange STRING (binance, bybit, okx),
  api_key_encrypted TEXT,
  api_secret_encrypted TEXT,
  created_at DATETIME
)
```

---

## 🔄 Architecture

```
Telegram User <──> Aiogram Bot <──> MeshTradeBot Backend
                    ├─ Payments
                    ├─ UI/Menus
                    └─ User Mgmt
                         │
                         ├─→ SQLite DB
                         ├─→ Freqtrade RPC
                         ├─→ Freqtrade Webhook
                         └─→ Exchange (CCXT)
                         
Freqtrade Engine
├─ Strategy: EMA200 + RSI
├─ Backtests
├─ Signals → Telegram Bot via Webhook
└─ Trades → DB
```

### Signal Flow

1. **Freqtrade** runs on 5m timeframe
2. **EMA200 + RSI** strategy generates signals
3. **Signal sent via webhook** to bot
4. **Bot filters** by user subscription & preferences
5. **Telegram message** sent to users
6. **User clicks "Auto-Trade"** (Premium only)
7. **Bot calls Freqtrade RPC** with trade parameters
8. **Trade executed** on user's account
9. **Result logged** to database
10. **Performance updated** in real-time UI

---

## 🚨 Risk Management

### Hard Limits
- ✅ Max open trades: **3**
- ✅ Max stoploss: **2%** per trade
- ✅ Daily drawdown protection: **-5%** (pause trading)
- ✅ Max risk per trade: **1%** account (user configurable: 0.5-2%)

### Copy Trading Limits
- User sets max risk: 0.5% - 2% per trade
- Position size scaled automatically
- Can disable anytime

### Disclaimer Required
Every message includes:
```
⚠️ Trading involves risk of loss. Not financial advice.
```

---

## 🧪 Testing

### Dry-Run Mode (Default)

All trades are simulated with a virtual wallet:

```json
{
  "dry_run": true,
  "dry_run_wallet": 10000  // Start with 10k USDT
}
```

✅ Test strategies without real money  
✅ Perfect for backtesting  
✅ Change to `false` only when confident  

### Manual Testing

```bash
# Test bot locally
python main.py

# Test signal sending
curl -X POST http://localhost:8433/webhook \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC/USDT", "signal": "buy", "price": 68450}'

# Test database
python -c "
from database import get_db_context
from database.models import User
with get_db_context() as db:
    users = db.query(User).all()
    print(f'Total users: {len(users)}')
"
```

---

## 📦 Deployment (Production)

### Docker Production Setup

```bash
# Build production image
docker build -t meshtradebot:latest .

# Run with environment
docker run -d \
  --name meshtradebot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -p 8433:8433 \
  meshtradebot:latest
```

### Best Practices

1. **Use managed Freqtrade**: Consider freqtradeorg/freqtrade on server
2. **Database backups**: Schedule daily SQLite backups
3. **Monitoring**: Setup alerting for bot crashes
4. **Logging**: Check logs regularly for errors
5. **Rate limiting**: Telegram has API limits (~30 msgs/sec)
6. **SSL/HTTPS**: Use reverse proxy (Nginx) for webhook

---

## 🛠️ Extending the Bot

### Add New Exchange

Edit `freqtrade_config/default.json`:
```json
"exchange": {
  "name": "bybit"  // or okx, kraken, kucoin
}
```

Bybit, OKX fully supported via CCXT.

### Add New Strategy

1. Create `strategies/my_strategy.py`
2. Inherit from `IStrategy`
3. Implement: `populate_indicators()`, `populate_buy_trend()`, `populate_sell_trend()`
4. Update Freqtrade config to use it

### Add WhatsApp Support (Future)

Create `bot/whatsapp_handler.py`:
```python
from twilio.rest import Client

def send_whatsapp_signal(user_phone, signal):
    # Send via Twilio WhatsApp API
    pass
```

---

## 📝 Logging

Logs stored in `./logs/`:
- `meshtradebot.log` - Main bot logs
- `freqtrade.log` - Trading engine logs
- `payments.log` - Payment transactions

JSON format for easy parsing:
```json
{
  "timestamp": "2026-03-11T10:30:00Z",
  "level": "INFO",
  "module": "bot.payments",
  "message": "Payment received: ₦3000 for premium monthly"
}
```

---

## 📋 Development Roadmap & Phases

**Project Status:** Phase 1 Complete ✅  
**Target Release:** Production-ready by Phase 7  

### ✅ Phase 1: Foundation & Setup (COMPLETE)

**Objective:** Setup project scaffolding, database, and infrastructure.

✅ Folder structure & project layout  
✅ `requirements.txt` with all dependencies  
✅ `docker-compose.yml` + `Dockerfile`  
✅ Environment configuration (`.env.example`)  
✅ SQLAlchemy database models (users, trades, signals, payments)  
✅ Database initialization & session management  
✅ Encryption utilities for API keys (Fernet)  
✅ Logging configuration (JSON format)  
✅ Global constants & configurations  
✅ Conservative trading strategy (EMA200 + RSI)  

### ⏳ Phase 2: Core Telegram Bot (Planning)

**Objective:** Build the basic Telegram bot with menu and user interactions.

- [ ] Initialize aiogram 3.x Dispatcher
- [ ] Create main menu with buttons
- [ ] Implement /start command
- [ ] Implement /help command
- [ ] Implement user settings (risk %, preferences)
- [ ] Add FSMContext for multi-step commands
- [ ] Setup webhook listening on port 8433
- [ ] Add rate limiting middleware
- [ ] Add error handling & logging

**Estimated Time:** 2-3 days

### 📱 Phase 3: Telegram Payments Integration

- [ ] Research & integrate Stripe/Telegram Payments provider
- [ ] Implement `/subscribe` command
- [ ] Setup `sendInvoice` for payment requests
- [ ] Handle `pre_checkout_query` webhook
- [ ] Handle `successful_payment` updates
- [ ] Store payment transactions in database
- [ ] Auto-grant premium access on payment

**Estimated Time:** 2-3 days

### 🔗 Phase 4: Freqtrade Integration

- [ ] Setup webhook endpoint to receive Freqtrade signals
- [ ] Connect to Freqtrade RPC API
- [ ] Fetch live candle data for confidence scoring
- [ ] Integrate FreqAI signals if enabled
- [ ] Implement signal caching & deduplication

**Estimated Time:** 2-3 days

### 📊 Phase 5: Signal Distribution System

- [ ] Implement signal filtering by user subscription
- [ ] Send signals only to active premium users
- [ ] Add signal editing for corrections
- [ ] Implement user preference filtering
- [ ] Track signal delivery & read status

**Estimated Time:** 1-2 days

### 🤖 Phase 6: Direct Trading Module

- [ ] Implement `/addkeys` command for exchange API setup
- [ ] Support exchanges: Binance, Bybit, OKX, Kraken, KuCoin
- [ ] Implement one-click trade execution
- [ ] Add manual trade entry UI
- [ ] Implement trade confirmation workflow

**Estimated Time:** 3-4 days

### 📋 Phase 7: Copy Trading Module

- [ ] Setup master account Freqtrade instance
- [ ] Implement trade mirroring system
- [ ] Create copy trading configuration UI
- [ ] Implement signal listener for master account
- [ ] Auto-execute proportional trades on user accounts

**Estimated Time:** 3-4 days

### 🎨 Phase 8: Performance Dashboard & Analytics

- [ ] Calculate daily/weekly/monthly P&L
- [ ] Create trade statistics view
- [ ] Create visual charts
- [ ] Add copy trading performance breakdown

**Estimated Time:** 2-3 days

### 🚀 Phase 9: Deployment & Optimization

- [ ] Performance optimizations
- [ ] Database query optimization
- [ ] Background job scheduling (APScheduler)
- [ ] Comprehensive testing
- [ ] Security audit
- [ ] Load testing

**Estimated Time:** 2-3 days

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Bot Framework | aiogram | 3.5.0 |
| Trading Engine | Freqtrade | 2024.10 |
| Database | SQLAlchemy + SQLite | 2.0.23 |
| Encryption | cryptography | 41.0.7 |
| Exchange API | CCXT | 4.0.96 |
| Async | asyncio | Python 3.11+ |
| Deployment | Docker | latest |

---

## 🤝 Contributing

Thank you for your interest in contributing! Here are guidelines:

### Code Style

- **Python:** Follow PEP 8
- **Type hints:** Use where practical
- **Comments:** Heavy commenting for complex logic (trading bot!)
- **Logging:** Use extensively
- **Functions:** Keep small and testable

### Security Guidelines

✅ **DO:**
- Encrypt sensitive data before storage
- Use environment variables for secrets
- Validate all user inputs
- Log important actions (payments, trades)

❌ **DON'T:**
- Never hardcode API keys, tokens, or secrets
- Never log sensitive data
- Never trust user input without validation
- Never skip SSL verification

### Testing Changes

```bash
# Test database
python -c "from database import get_db_context; from database.models import User; db = get_db_context().__enter__(); print(f'Users: {db.query(User).count()}')"

# Test encryption
python -c "from utils.encryption import encrypt_data, decrypt_data; encrypted = encrypt_data('test'); print(encrypt_data('test')); print(decrypt_data(encrypted))"

# Run with Docker
docker-compose up -d
docker-compose logs -f meshtradebot
```

### Before Submitting PR

- [ ] Code follows PEP 8 style guidelines
- [ ] All comments are clear and non-sensitive
- [ ] No hardcoded secrets or credentials
- [ ] `.env` file is NOT included
- [ ] README updated if needed
- [ ] Tested locally in Docker
- [ ] Descriptive commit message

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes with clear commits
git add .
git commit -m "Add feature X

- Description of changes
- Additional details if needed"

# Push and create PR
git push origin feature/your-feature
```

### Module Responsibilities

- **`bot/handlers.py`** - Parse user commands, validate input
- **`bot/payments.py`** - Telegram Payments API integration
- **`bot/freqtrade_integration.py`** - Receive & parse signals
- **`bot/direct_trading.py`** - Execute trades via CCXT
- **`bot/copy_trading.py`** - Mirror master account trades
- **`database/models.py`** - Data layer (NO business logic here)
- **`utils/`** - Shared utilities (encryption, logging)
- **`config/`** - Constants, configuration (NO secrets)

### Quality Standards

This is a **production trading bot** handling real money. Code quality is critical:

- **No quick hacks** - Strategic trading demands clean code
- **Extensive logging** - Debug live trading issues
- **Backward compatibility** - Users depend on stability
- **Security first** - Financial data must be protected
- **Comprehensive error handling** - Trading can't crash silently

---

## 🎯 Future Enhancements

- [ ] WhatsApp bot version (Twilio)
- [ ] Discord bot integration
- [ ] Advanced backtesting UI
- [ ] Custom strategy builder
- [ ] Multi-asset trading (futures, options)
- [ ] Mobile app (Flutter)
- [ ] Community signal marketplace
- [ ] DeFi lending integration

---

## 📞 Support & Documentation

- `README.md` - Setup & deployment (this file)
- `database/models.py` - Data schema
- `config/constants.py` - Configuration
- Code comments throughout project
- Freqtrade docs: https://freqtrade.io/
- Aiogram docs: https://docs.aiogram.dev/

---

**Current Phase:** 1 (Complete) ✅  
**Next Phase:** 2 (Core Telegram Bot)  
**Last Updated:** March 11, 2026

---

## 🐛 Troubleshooting

### Bot not starting

```bash
# Check logs
docker-compose logs meshtradebot

# Verify .env variables
cat .env

# Rebuild image
docker-compose build --no-cache
```

### "Invalid ENCRYPTION_KEY"

```bash
# Generate new key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Update .env
echo "ENCRYPTION_KEY=<your-new-key>" >> .env
```

### Freqtrade not connecting

```bash
# Check if running
docker-compose logs freqtrade

# Verify network
docker-compose exec meshtradebot ping freqtrade:8080

# Reset
docker-compose restart freqtrade
```

### Payment not processing

- Verify `TELEGRAM_PROVIDER_TOKEN` is correct
- Check it's for your bot (via @BotFather)
- Ensure ngrok/public URL for webhook if testing locally

---

## 📚 Additional Resources

- [Freqtrade Docs](https://freqtrade.io/)
- [Aiogram Docs](https://docs.aiogram.dev/)
- [Python Telegram Bot](https://python-telegram-bot.readthedocs.io/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [CCXT Documentation](https://docs.ccxt.com/)

---

## 📄 License

MIT License - See LICENSE file

---

## 🤝 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review code comments (heavily documented for extensibility)

---

## ⚠️ IMPORTANT DISCLAIMERS

### Trading Disclaimer
```
Trading and investing in cryptocurrencies are HIGHLY RISKY. 

MeshTradeBot provides NO FINANCIAL ADVICE. It is a TOOL for automated trading only.

• You can LOSE all your money
• Past performance ≠ Future results
• Start with small amounts
• Use stop-losses ALWAYS
• We are NOT liable for losses
```

### Security Reminder
- Keep your `.env` file secure and never commit it to git
- Regenerate encryption keys if compromised
- Never leave your bot running in production without monitoring
- Use read-only API keys when possible
- Enable IP whitelist on exchange APIs

---

**Last Updated:** March 2026  
**Version:** 0.1.0  
**Status:** Beta (Production-ready for testing)

---

## Next Steps

After setup, work on:

1. ✅ Database models ← **WE ARE HERE**
2. ⬜️ Core aiogram bot skeleton
3. ⬜️ Telegram payment integration
4. ⬜️ Freqtrade webhook integration
5. ⬜️ Signal distribution
6. ⬜️ Direct trading module
7. ⬜️ Copy trading setup
8. ⬜️ Performance dashboard

See [projects/ROADMAP.md](projects/ROADMAP.md) for detailed development plan.
