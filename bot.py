"""
Advanced Discord Bot Template
=============================

A production-ready Discord bot template with enterprise features.

Features:
- Automatic cog loading from cogs/ directory
- TOML-based configuration
- Structured logging with file and console output
- Environment variable support
- Graceful shutdown handling
- Professional error handling
- Discord sharding support (for 2500+ guild bots)
- Docker ready

Usage:
    1. Add your bot token to .env (DISCORD_TOKEN=your_token)
    2. Install cogs: multicord bot cog add <cog-name> <bot-name>
    3. Run: python bot.py

For sharding (2500+ guilds):
    Set SHARD_ID and SHARD_COUNT environment variables
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands

try:
    import tomli
except ImportError:
    import tomllib as tomli


# Discord sharding detection (for 2500+ guild bots)
SHARD_ID = int(os.getenv('SHARD_ID', 0))
SHARD_COUNT = int(os.getenv('SHARD_COUNT', 1))


def get_bot_base_class():
    """Select appropriate bot base class based on sharding configuration."""
    if SHARD_COUNT > 1:
        return commands.AutoShardedBot
    return commands.Bot


class AdvancedBot(get_bot_base_class()):
    """
    Advanced Discord bot with enterprise features.

    Automatically loads all cogs from the cogs/ directory and provides
    structured logging, configuration, error handling, and sharding support.
    """

    def __init__(self, config: dict):
        """
        Initialize the bot.

        Args:
            config: Configuration dictionary from config.toml
        """
        # Bot configuration
        self.bot_config = config.get('bot', {})
        self.features_config = config.get('features', {})

        # Store full config for cog access
        self.config = config

        # Set up intents
        intents = discord.Intents.default()
        if self.bot_config.get('privileged_intents', {}).get('message_content', False):
            intents.message_content = True
        if self.bot_config.get('privileged_intents', {}).get('members', False):
            intents.members = True
        if self.bot_config.get('privileged_intents', {}).get('presences', False):
            intents.presences = True

        # Build initialization kwargs
        kwargs = {
            'command_prefix': self.bot_config.get('prefix', '!'),
            'intents': intents,
            'help_command': commands.DefaultHelpCommand() if self.bot_config.get('enable_help', True) else None,
            'description': self.bot_config.get('description', 'Advanced Discord Bot')
        }

        # Add sharding parameters if sharded
        if SHARD_COUNT > 1:
            kwargs['shard_ids'] = [SHARD_ID]
            kwargs['shard_count'] = SHARD_COUNT

        # Initialize bot
        super().__init__(**kwargs)

        # Track startup time
        self.start_time = datetime.now(timezone.utc)

        # Bot identification (from environment)
        self.bot_name = os.environ.get('BOT_NAME', 'advanced-bot')
        self.bot_port = os.environ.get('BOT_PORT', '8100')

        # Shard info for logging
        self.shard_info = f"Shard {SHARD_ID}/{SHARD_COUNT}" if SHARD_COUNT > 1 else "Single instance"

        # Set up logging
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """
        Set up structured logging with both file and console output.

        Returns:
            Configured logger instance
        """
        # Create logs directory
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        # Configure logger
        logger = logging.getLogger('discord')
        logger.setLevel(logging.INFO)

        # Ensure console can handle Unicode on Windows
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)

        # File handler for persistent logs
        file_handler = logging.FileHandler(
            log_dir / 'bot.log',
            encoding='utf-8',
            mode='a'
        )
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)

        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

    async def setup_hook(self):
        """
        Called when the bot is starting up.
        Loads all cogs from the cogs/ directory.
        """
        self.logger.info(f"Starting bot setup for {self.bot_name} ({self.shard_info})")

        # Load cogs automatically
        await self._load_cogs()

        self.logger.info("Bot setup complete")

    async def _load_cogs(self):
        """
        Automatically discover and load all cogs from the cogs/ directory.

        This method:
        - Scans the cogs/ directory for valid Python packages
        - Loads each cog using Discord.py's extension system
        - Reports success/failure for each cog
        - Continues loading even if individual cogs fail
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
        """Called when the bot is fully connected and ready."""
        self.logger.info(f"Bot is ready! ({self.shard_info})")
        self.logger.info(f"  Logged in as: {self.user.name} (ID: {self.user.id})")
        self.logger.info(f"  Connected to {len(self.guilds)} guild(s)")
        self.logger.info(f"  Loaded {len(self.cogs)} cog(s)")

        # Set bot status if configured
        status = self.bot_config.get('status')
        if status:
            activity = discord.Game(name=status)
            await self.change_presence(activity=activity)
            self.logger.info(f"  Status set to: {status}")

    async def on_guild_join(self, guild):
        """Event triggered when bot joins a guild."""
        self.logger.info(f'Joined guild: {guild.name} (ID: {guild.id})')

    async def on_guild_remove(self, guild):
        """Event triggered when bot leaves a guild."""
        self.logger.info(f'Left guild: {guild.name} (ID: {guild.id})')

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """
        Global error handler for command errors.

        Args:
            ctx: Command context
            error: The error that occurred
        """
        # Ignore command not found errors
        if isinstance(error, commands.CommandNotFound):
            return

        # Handle missing permissions
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"❌ You don't have permission to use this command.")
            return

        # Handle bot missing permissions
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"❌ I don't have the required permissions to do that.")
            return

        # Handle missing arguments
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
            return

        # Handle bad arguments
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument: {error}")
            return

        # Handle cooldown errors
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ This command is on cooldown. Try again in {error.retry_after:.1f}s")
            return

        # Log unexpected errors
        self.logger.error(f"Unhandled command error in {ctx.command}: {error}", exc_info=error)
        await ctx.send("❌ An error occurred while processing your command.")

    async def close(self):
        """Graceful shutdown handler."""
        self.logger.info("Shutting down bot...")
        await super().close()
        self.logger.info("Bot shutdown complete")


def load_config() -> dict:
    """
    Load configuration from config.toml.

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config.toml doesn't exist
        ValueError: If config.toml is invalid
    """
    config_path = Path('config.toml')

    if not config_path.exists():
        raise FileNotFoundError(
            "config.toml not found. Please create it from config.toml.example"
        )

    try:
        with open(config_path, 'rb') as f:
            config = tomli.load(f)
        return config
    except Exception as e:
        raise ValueError(f"Failed to parse config.toml: {e}")


def get_bot_token() -> str:
    """
    Get the bot token from environment or config.

    Returns:
        Bot token string

    Raises:
        ValueError: If no token is found
    """
    # Try environment variable first (recommended for production)
    token = os.getenv('DISCORD_TOKEN')

    if not token:
        # Try loading from .env file
        env_path = Path('.env')
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('DISCORD_TOKEN='):
                        token = line.split('=', 1)[1].strip()
                        break

    if not token:
        raise ValueError(
            "No Discord token found. Run: multicord bot set-token <bot-name>  "
            "Or set DISCORD_TOKEN environment variable or create .env file"
        )

    return token


async def main():
    """Main entry point for the bot."""
    # Log sharding configuration
    if SHARD_COUNT > 1:
        print(f"🔀 Sharding enabled: Shard {SHARD_ID} of {SHARD_COUNT}")

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)

    # Get bot token
    try:
        token = get_bot_token()
    except ValueError as e:
        print(f"❌ Token error: {e}")
        sys.exit(1)

    # Create and run bot
    async with AdvancedBot(config) as bot:
        try:
            await bot.start(token)
        except KeyboardInterrupt:
            print("\n⚠️  Received shutdown signal")
        except Exception as e:
            print(f"❌ Bot error: {e}")
            sys.exit(1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
