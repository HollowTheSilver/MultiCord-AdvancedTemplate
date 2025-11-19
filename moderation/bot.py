#!/usr/bin/env python3
"""
Moderation Discord Bot Template for MultiCord.
A minimal scaffolding bot that loads moderation features from cogs.
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
    logger.error("Please create a .env file with your Discord bot token.")
    sys.exit(1)

# Bot configuration
PREFIX = config["bot"].get("prefix", "!")
DESCRIPTION = config["bot"].get("description", "A moderation Discord bot")

# Intents configuration
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.bans = True
intents.moderation = True

class ModerationBot(commands.Bot):
    """Moderation Discord bot with MultiCord integration."""

    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            description=DESCRIPTION,
            intents=intents,
            help_command=commands.DefaultHelpCommand()
        )
        self.start_time = datetime.utcnow()
        self.bot_name = os.environ.get('BOT_NAME', 'moderation-bot')
        self.bot_port = os.environ.get('BOT_PORT', '8100')
        self.logger = logger
        self.config = config  # Expose config to cogs

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
        self.logger.info(f"Bot is ready!")
        self.logger.info(f"  Logged in as: {self.user.name} (ID: {self.user.id})")
        self.logger.info(f"  Connected to {len(self.guilds)} guild(s)")
        self.logger.info(f"  Loaded {len(self.cogs)} cog(s)")

        # Set status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"for rule breakers | {PREFIX}help"
            )
        )

    async def close(self):
        """Graceful shutdown handler."""
        self.logger.info("Shutting down bot...")
        await super().close()
        self.logger.info("Bot shutdown complete")

# Create bot instance
bot = ModerationBot()

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