# Telegram Signal Forwarder

Listens to a source Telegram channel (via user account) and forwards messages to a target channel (via bot account).

## Features

- **Dual Client Architecture**: User client listens, Bot client broadcasts
- **Koyeb Ready**: StringSession support for ephemeral storage environments
- **Graceful Shutdown**: Handles SIGTERM for clean restarts
- **Keepalive**: 5-minute heartbeat prevents idle timeout

## Quick Start

### 1. Setup Credentials

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
- `API_ID` - From [my.telegram.org](https://my.telegram.org)
- `API_HASH` - From [my.telegram.org](https://my.telegram.org)
- `BOT_TOKEN` - From [@BotFather](https://t.me/BotFather)
- `SOURCE_CHANNEL_ID` - Channel to listen to (negative integer)
- `TARGET_CHANNEL_ID` - Channel to forward to (negative integer)
- `phone_number` - Your phone number for initial auth

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Locally

```bash
python main.py
```

## Deploy to Koyeb

### 1. Generate Session Strings

```bash
python generate_session.py
```

Copy the output strings.

### 2. Deploy

1. Connect this repo to [Koyeb](https://app.koyeb.com)
2. Set service type: **Worker**
3. Add environment variables (including `USER_SESSION_STRING` and `BOT_SESSION_STRING`)
4. Deploy

## Files

| File | Purpose |
|------|--------|
| `main.py` | Main application with event handlers |
| `config.py` | Environment variable loading |
| `parser.py` | Signal parsing utilities (optional) |
| `generate_session.py` | Export sessions for Koyeb |
| `Procfile` | Koyeb worker declaration |

## License

MIT
