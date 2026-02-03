#!/usr/bin/env python3
"""
Basic Discord Bot Template for MultiCord.
A simple, extensible Discord bot with command handling and cog support.
"""

import os
import sys
import logging
from pathlib import Path
import discord
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv

try:
    import tomli
except ImportError:
    import tomllib as tomli

# Load environment variables
load_dotenv()

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Ensure console can handle Unicode on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_dir / 'bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('discord')

# Load configuration
config_path = Path(__file__).parent / "config.toml"
if config_path.exists():
    with open(config_path, 'rb') as f:
        config = tomli.load(f)
else:
    logger.error("config.toml not found!")
    sys.exit(1)

# Get bot token from environment
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    logger.error("DISCORD_TOKEN not found in environment variables!")
    logger.error("Run: multicord bot set-token <bot-name>")
    logger.error("Or add DISCORD_TOKEN to .env file manually")
    sys.exit(1)

# Bot configuration
PREFIX = config["bot"].get("prefix", "!")
DESCRIPTION = config["bot"].get("description", "A basic Discord bot")

# Intents configuration
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Discord sharding detection (for 2500+ guild bots)
SHARD_ID = int(os.getenv('SHARD_ID', 0))
SHARD_COUNT = int(os.getenv('SHARD_COUNT', 1))

# Select appropriate base class based on sharding
if SHARD_COUNT > 1:
    BotBaseClass = commands.AutoShardedBot
    logger.info(f"Sharding enabled: Running as shard {SHARD_ID}/{SHARD_COUNT}")
else:
    BotBaseClass = commands.Bot
    logger.info("Sharding disabled: Running as single instance")


class BasicBot(BotBaseClass):
    """Basic Discord bot with MultiCord integration and automatic shard support."""

    def __init__(self):
        # Build bot initialization kwargs
        kwargs = {
            'command_prefix': PREFIX,
            'description': DESCRIPTION,
            'intents': intents,
            'help_command': commands.DefaultHelpCommand()
        }

        # Add sharding parameters if sharded
        if SHARD_COUNT > 1:
            kwargs['shard_ids'] = [SHARD_ID]
            kwargs['shard_count'] = SHARD_COUNT

        super().__init__(**kwargs)
        self.start_time = datetime.utcnow()
        self.bot_name = os.environ.get('BOT_NAME', 'basic-bot')
        self.bot_port = os.environ.get('BOT_PORT', '8100')
        self.logger = logger
        self.shard_info = f"Shard {SHARD_ID}/{SHARD_COUNT}" if SHARD_COUNT > 1 else "Single instance"

    async def setup_hook(self):
        """Setup hook for bot initialization."""
        self.logger.info(f"Starting bot setup for {self.bot_name}")

        # Load cogs
        await self._load_cogs()

        self.logger.info("Bot setup complete")

    async def _load_cogs(self):
        """
        Automatically discover and load all cogs from the cogs/ directory.

        Looks for valid Python packages (directories with __init__.py).
        """
        cogs_dir = Path(__file__).parent / 'cogs'

        if not cogs_dir.exists():
            self.logger.info("No cogs directory found - running without extensions")
            return

        # Find all valid cog directories
        cog_count = 0
        failed_cogs = []

        for item in cogs_dir.iterdir():
            # Skip non-directories and private directories
            if not item.is_dir() or item.name.startswith('_'):
                continue

            # Check if it has __init__.py (is a valid Python package)
            if not (item / '__init__.py').exists():
                self.logger.warning(f"Skipping {item.name} - not a valid Python package")
                continue

            # Try to load the cog
            cog_name = f'cogs.{item.name}'
            try:
                await self.load_extension(cog_name)
                self.logger.info(f"✓ Loaded cog: {item.name}")
                cog_count += 1
            except Exception as e:
                self.logger.error(f"✗ Failed to load cog {item.name}: {e}")
                failed_cogs.append((item.name, str(e)))

        # Summary
        if cog_count > 0:
            self.logger.info(f"Successfully loaded {cog_count} cog(s)")
        else:
            self.logger.info("No cogs loaded")

        if failed_cogs:
            self.logger.warning(f"Failed to load {len(failed_cogs)} cog(s)")
            for cog_name, error in failed_cogs:
                self.logger.warning(f"  - {cog_name}: {error}")

    async def on_ready(self):
        """Event triggered when bot is ready."""
        self.logger.info(f"Bot is ready! ({self.shard_info})")
        self.logger.info(f"  Logged in as: {self.user.name} (ID: {self.user.id})")
        self.logger.info(f"  Connected to {len(self.guilds)} guild(s)")
        self.logger.info(f"  Loaded {len(self.cogs)} cog(s)")

        # Set status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{len(self.guilds)} servers | {PREFIX}help"
            )
        )

    async def on_guild_join(self, guild):
        """Event triggered when bot joins a guild."""
        self.logger.info(f'Joined guild: {guild.name} (ID: {guild.id})')

    async def on_guild_remove(self, guild):
        """Event triggered when bot leaves a guild."""
        self.logger.info(f'Left guild: {guild.name} (ID: {guild.id})')

    async def on_command_error(self, ctx, error):
        """Global error handler for commands."""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param.name}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument provided: {error}")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Command on cooldown. Try again in {error.retry_after:.1f}s")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I don't have the required permissions to do that.")
        else:
            self.logger.error(f"Unhandled error in command {ctx.command}: {error}", exc_info=error)
            await ctx.send("❌ An error occurred while processing this command.")

    async def close(self):
        """Graceful shutdown handler."""
        self.logger.info("Shutting down bot...")
        await super().close()
        self.logger.info("Bot shutdown complete")


# Create bot instance
bot = BasicBot()


# Basic commands
@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency."""
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Latency: {latency}ms')


@bot.command(name='uptime')
async def uptime(ctx):
    """Check bot uptime."""
    delta = datetime.utcnow() - bot.start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)

    uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
    await ctx.send(f'⏱️ Bot uptime: {uptime_str}')


@bot.command(name='stats')
async def stats(ctx):
    """Display bot statistics."""
    embed = discord.Embed(
        title="📊 Bot Statistics",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="Users", value=len(bot.users), inline=True)
    embed.add_field(name="Commands", value=len(bot.commands), inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)

    delta = datetime.utcnow() - bot.start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)
    embed.add_field(name="Uptime", value=f"{hours}h {minutes}m", inline=True)

    embed.set_footer(text=f"MultiCord Bot: {bot.bot_name}")

    await ctx.send(embed=embed)


@bot.command(name='info')
async def info(ctx):
    """Display bot information."""
    embed = discord.Embed(
        title=bot.user.name,
        description=bot.description,
        color=discord.Color.green()
    )

    embed.add_field(
        name="About",
        value="This is a basic Discord bot template powered by MultiCord.",
        inline=False
    )

    embed.add_field(name="Prefix", value=PREFIX, inline=True)
    embed.add_field(name="Version", value="2.0.0", inline=True)
    embed.add_field(name="Library", value=f"discord.py {discord.__version__}", inline=True)

    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_footer(text="Made with MultiCord")

    await ctx.send(embed=embed)


@bot.command(name='shutdown', hidden=True)
@commands.is_owner()
async def shutdown(ctx):
    """Shutdown the bot (owner only)."""
    await ctx.send("👋 Shutting down...")
    await bot.close()


if __name__ == "__main__":
    # Run the bot
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        logger.error("Invalid bot token! Please check your DISCORD_TOKEN in .env")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)
