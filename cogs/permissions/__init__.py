"""
Custom Permissions System Cog
==============================

Enterprise-grade hierarchical permission system for Discord bots.

Features:
- 9-level permission hierarchy (BANNED → BOT_OWNER)
- Intelligent role auto-detection with classification
- Unicode text normalization for fancy Discord names
- Guild-specific permission overrides
- Audit logging for compliance
- Optional database persistence

Usage:
    # In your bot's main file:
    await bot.load_extension('cogs.permissions')

    # Or manually:
    from cogs.permissions import PermissionsCog
    await bot.add_cog(PermissionsCog(bot))

Author: HollowTheSilver
Version: 1.0.0
"""

from discord.ext import commands
from .permissions import PermissionManager

__version__ = "1.0.0"
__author__ = "HollowTheSilver"


class PermissionsCog(commands.Cog, name="PermissionsBackend"):
    """
    Advanced permission management system for Discord bots.

    Provides hierarchical permission control with intelligent role detection,
    guild-specific overrides, and comprehensive audit logging.
    """

    def __init__(self, bot: commands.Bot, use_database: bool = False, db_path: str = None):
        """
        Initialize the Permissions cog.

        Args:
            bot: The Discord bot instance
            use_database: Whether to use database persistence (default: False, uses in-memory)
            db_path: Path to SQLite database file (optional)
        """
        self.bot = bot
        self.use_database = use_database
        self.db_path = db_path

        # Initialize permission manager
        self.permissions = PermissionManager(bot=bot)

    async def cog_load(self):
        """Called when the cog is loaded."""
        # No initialization needed - PermissionManager is ready after __init__
        self.bot.logger.info("Permissions system loaded")

    async def cog_unload(self):
        """Called when the cog is unloaded."""
        await self.permissions.shutdown()
        self.bot.logger.info("Permissions system shut down")


async def setup(bot: commands.Bot):
    """
    Standard Discord.py cog setup function.

    This function is called when you use bot.load_extension('cogs.permissions').

    Configuration can be passed via bot.config if available:
        bot.config['permissions'] = {
            'use_database': True,
            'db_path': 'data/permissions.db'
        }
    """
    # Check if bot has configuration
    use_database = False
    db_path = None

    if hasattr(bot, 'config') and 'permissions' in bot.config:
        perm_config = bot.config['permissions']
        use_database = perm_config.get('use_database', False)
        db_path = perm_config.get('db_path', None)

    # Create and add the backend cog
    backend_cog = PermissionsCog(bot, use_database=use_database, db_path=db_path)
    await bot.add_cog(backend_cog)

    # Make permission_manager accessible to command cog
    bot.permission_manager = backend_cog.permissions

    # Import and add the command interface cog
    from .commands import Permissions as PermissionsCommands
    commands_cog = PermissionsCommands(bot)
    await bot.add_cog(commands_cog)
