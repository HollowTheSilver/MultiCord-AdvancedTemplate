# MultiCord Advanced Template

A production-ready Discord bot template with enterprise features for [MultiCord](https://github.com/HollowTheSilver/MultiCord).

## Features

- Automatic cog loading from `cogs/` directory
- TOML-based configuration
- Structured logging (file + console)
- Environment variable support for secrets
- Graceful shutdown handling
- Professional error handling
- Docker and sharding ready

## Quick Start

```bash
# Create a bot from this template
multicord bot create my-bot --from advanced

# Add your Discord token
cd ~/.multicord/bots/my-bot
# Edit .env and add DISCORD_TOKEN=your_token_here

# Start the bot
multicord bot run my-bot
```

## Adding Cogs

Install cogs to add features:

```bash
multicord bot cog add permissions my-bot
multicord bot cog add moderation my-bot
```

Cogs are automatically discovered and loaded from the `cogs/` directory.

## Configuration

Edit `config.toml` for bot settings:

```toml
[bot]
prefix = "!"
description = "My Discord Bot"

[bot.privileged_intents]
message_content = true
members = true
```

## Project Structure

```
my-bot/
├── bot.py           # Main bot file
├── config.toml      # Bot configuration
├── .env             # Secret token (never commit!)
├── requirements.txt # Dependencies
├── cogs/            # Cog modules (auto-loaded)
└── logs/            # Log files
```

## License

MIT License - see [LICENSE](LICENSE)
