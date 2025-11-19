# Basic Discord Bot

A simple, extensible Discord bot template for MultiCord. Perfect for beginners and quick bot deployments.

## Features

- **Command handling** with customizable prefix
- **Event processing** (guild join/leave, errors)
- **Built-in commands**: ping, uptime, stats, info, shutdown
- **Auto-loading cog system** for modular extensions
- **Environment-based configuration** with .env support
- **Structured logging** to file and console
- **Clean error handling** with user-friendly messages
- **Production-ready** with graceful shutdown
- **MultiCord integration** ready

## Quick Start

### Prerequisites

- Python 3.9 or higher
- A Discord bot token ([Get one here](https://discord.com/developers/applications))
- MultiCord CLI installed

### Installation

1. Create a new bot using this template:
   ```bash
   multicord bot create my-bot --template basic
   ```

2. Configure your bot token:
   ```bash
   cd bots/my-bot
   # Edit .env and add your Discord bot token
   # DISCORD_TOKEN=your_token_here
   ```

3. Start the bot:
   ```bash
   multicord bot start my-bot
   ```

The CLI automatically creates a `.env` file from `.env.example` during bot creation.

## Configuration

### Environment Variables (.env)

Store sensitive information in the `.env` file (never commit this to Git):

```bash
# Discord Bot Token (REQUIRED)
DISCORD_TOKEN=your_token_here

# Optional: Bot identification
# BOT_NAME=my-bot
# BOT_PORT=8100
```

### Bot Configuration (config.toml)

Customize non-sensitive bot settings in `config.toml`:

```toml
[bot]
prefix = "!"
description = "A basic Discord bot powered by MultiCord"

[logging]
level = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
max_file_size_mb = 10
backup_count = 5

[features]
welcome_messages = true
auto_roles = false
moderation = false
```

**Security Note**: The bot token is stored in `.env` for security. This file is automatically excluded from Git via `.gitignore`.

## Available Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `!ping` | Check bot latency | `!ping` |
| `!uptime` | Show how long the bot has been running | `!uptime` |
| `!stats` | Display bot statistics (servers, users, etc.) | `!stats` |
| `!info` | Show bot information | `!info` |
| `!shutdown` | Shutdown the bot (owner only) | `!shutdown` |

## Required Discord Permissions

- **Send Messages** - To respond to commands
- **Embed Links** - To send rich embeds
- **Read Message History** - To process messages

## Extending the Bot

### Adding Simple Commands

Add new commands directly to `bot.py`:

```python
@bot.command(name="hello")
async def hello(ctx):
    """Say hello to the user."""
    await ctx.send(f"Hello {ctx.author.mention}!")
```

### Creating Cogs

For better organization, create cogs as **Python packages** in the `cogs/` directory. The bot automatically discovers and loads all cogs at startup.

**Directory structure**:
```
cogs/
└── greetings/              # Cog package directory
    ├── __init__.py         # Required: defines the cog
    └── requirements.txt    # Optional: cog-specific dependencies
```

**Example cog** (`cogs/greetings/__init__.py`):
```python
from discord.ext import commands

class Greetings(commands.Cog):
    """Friendly greeting commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        """Say hello to the user."""
        await ctx.send(f"Hello {ctx.author.mention}!")

    @commands.command()
    async def goodbye(self, ctx):
        """Say goodbye to the user."""
        await ctx.send(f"Goodbye {ctx.author.mention}!")

async def setup(bot):
    """Required setup function for Discord.py cogs."""
    await bot.add_cog(Greetings(bot))
```

**Using the MultiCord CLI**:
```bash
# Install community cogs (coming soon)
multicord cog add my-bot permissions

# The bot automatically loads all cogs on next start
multicord bot restart my-bot
```

## Troubleshooting

### Bot doesn't start

**Error: "Missing DISCORD_TOKEN environment variable"**
- Ensure `.env` file exists in the bot directory
- Check that `DISCORD_TOKEN=your_token_here` is set in `.env`
- Verify the token is valid (from [Discord Developer Portal](https://discord.com/developers/applications))
- Make sure there are no spaces around the `=` sign

**Other startup issues:**
- Check logs in `logs/bot.log` for detailed error messages
- Ensure all dependencies are installed in the bot's virtual environment
- Verify Python version is 3.9 or higher

### Commands don't work

- Verify the bot has **Message Content Intent** enabled in Discord Developer Portal
- Check that the bot has "Send Messages" and "Embed Links" permissions in your server
- Ensure you're using the correct command prefix (default: `!`)
- Check logs for command errors

### Cogs don't load

- Verify cog directory structure: `cogs/cogname/__init__.py`
- Check that `__init__.py` contains the `async def setup(bot)` function
- Review logs for specific cog loading errors
- Ensure cog dependencies are installed: `pip install -r cogs/cogname/requirements.txt`

## License

MIT License - see root repository LICENSE file

---

**Made with [MultiCord](https://github.com/HollowTheSilver/MultiCord)** | [Report Issues](https://github.com/HollowTheSilver/MultiCord-Templates/issues)
