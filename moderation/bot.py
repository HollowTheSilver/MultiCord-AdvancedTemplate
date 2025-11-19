#!/usr/bin/env python3
"""
Moderation Discord Bot Template for MultiCord.
A bot focused on server moderation and management.
"""

import os
import sys
import logging
from pathlib import Path
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from dotenv import load_dotenv
import asyncio
from typing import Optional, List

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

# Moderation settings
AUTO_MOD = config["moderation"].get("auto_mod", True)
MAX_WARNINGS = config["moderation"].get("max_warnings", 3)
MUTE_DURATION = config["moderation"].get("mute_duration_minutes", 10)

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

        # Moderation data (in production, use a database)
        self.warnings = {}  # {guild_id: {user_id: [warnings]}}
        self.muted_users = {}  # {guild_id: {user_id: unmute_time}}

    async def setup_hook(self):
        """Setup hook for bot initialization."""
        self.logger.info(f"Starting bot setup for {self.bot_name}")

        # Load cogs
        await self._load_cogs()

        # Start background tasks
        self.check_mutes.start()

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
    
    @tasks.loop(seconds=30)
    async def check_mutes(self):
        """Check and remove expired mutes."""
        current_time = datetime.utcnow()
        for guild_id in list(self.muted_users.keys()):
            for user_id in list(self.muted_users[guild_id].keys()):
                if self.muted_users[guild_id][user_id] <= current_time:
                    # Unmute user
                    guild = self.get_guild(guild_id)
                    if guild:
                        member = guild.get_member(user_id)
                        if member:
                            muted_role = discord.utils.get(guild.roles, name="Muted")
                            if muted_role and muted_role in member.roles:
                                await member.remove_roles(muted_role)
                                logger.info(f"Auto-unmuted {member} in {guild.name}")
                    
                    del self.muted_users[guild_id][user_id]
    
    async def on_message(self, message):
        """Auto-moderation for messages."""
        if message.author.bot:
            return
        
        if AUTO_MOD and message.guild:
            # Check for spam (simple example)
            if len(message.content) > 1000:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention}, your message was too long and has been deleted.",
                    delete_after=5
                )
                return
            
            # Check for mass mentions
            if len(message.mentions) > 5:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention}, please don't mass mention users.",
                    delete_after=5
                )
                return
        
        await self.process_commands(message)

# Create bot instance
bot = ModerationBot()

# Moderation commands
@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: Optional[str] = "No reason provided"):
    """Kick a member from the server."""
    if member.top_role >= ctx.author.top_role:
        await ctx.send("You cannot kick someone with an equal or higher role.")
        return
    
    await member.kick(reason=f"{reason} - by {ctx.author}")
    
    embed = discord.Embed(
        title="Member Kicked",
        color=discord.Color.orange(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Member", value=f"{member.mention} ({member})", inline=False)
    embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    
    await ctx.send(embed=embed)
    logger.info(f"{ctx.author} kicked {member} from {ctx.guild.name}")

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: Optional[str] = "No reason provided"):
    """Ban a member from the server."""
    if member.top_role >= ctx.author.top_role:
        await ctx.send("You cannot ban someone with an equal or higher role.")
        return
    
    await member.ban(reason=f"{reason} - by {ctx.author}", delete_message_days=1)
    
    embed = discord.Embed(
        title="Member Banned",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Member", value=f"{member.mention} ({member})", inline=False)
    embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    
    await ctx.send(embed=embed)
    logger.info(f"{ctx.author} banned {member} from {ctx.guild.name}")

@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    """Unban a user by their ID."""
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"Unbanned {user.mention}")
        logger.info(f"{ctx.author} unbanned {user} in {ctx.guild.name}")
    except discord.NotFound:
        await ctx.send("User not found or not banned.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to unban users.")

@bot.command(name='mute')
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: Optional[int] = None, *, reason: Optional[str] = "No reason provided"):
    """Mute a member (duration in minutes)."""
    if member.top_role >= ctx.author.top_role:
        await ctx.send("You cannot mute someone with an equal or higher role.")
        return
    
    # Get or create muted role
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(
            name="Muted",
            color=discord.Color.dark_gray(),
            reason="Muted role for moderation"
        )
        
        # Set permissions for all channels
        for channel in ctx.guild.channels:
            await channel.set_permissions(
                muted_role,
                send_messages=False,
                add_reactions=False,
                speak=False
            )
    
    await member.add_roles(muted_role, reason=reason)
    
    # Set unmute time if duration specified
    if duration:
        unmute_time = datetime.utcnow() + timedelta(minutes=duration)
        if ctx.guild.id not in bot.muted_users:
            bot.muted_users[ctx.guild.id] = {}
        bot.muted_users[ctx.guild.id][member.id] = unmute_time
        duration_text = f"{duration} minutes"
    else:
        duration_text = "indefinitely"
    
    embed = discord.Embed(
        title="Member Muted",
        color=discord.Color.dark_gray(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="Duration", value=duration_text, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    
    await ctx.send(embed=embed)
    logger.info(f"{ctx.author} muted {member} in {ctx.guild.name}")

@bot.command(name='unmute')
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    """Unmute a member."""
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role or muted_role not in member.roles:
        await ctx.send(f"{member.mention} is not muted.")
        return
    
    await member.remove_roles(muted_role)
    
    # Remove from muted users dict
    if ctx.guild.id in bot.muted_users and member.id in bot.muted_users[ctx.guild.id]:
        del bot.muted_users[ctx.guild.id][member.id]
    
    await ctx.send(f"Unmuted {member.mention}")
    logger.info(f"{ctx.author} unmuted {member} in {ctx.guild.name}")

@bot.command(name='warn')
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason: str):
    """Warn a member."""
    if ctx.guild.id not in bot.warnings:
        bot.warnings[ctx.guild.id] = {}
    if member.id not in bot.warnings[ctx.guild.id]:
        bot.warnings[ctx.guild.id][member.id] = []
    
    bot.warnings[ctx.guild.id][member.id].append({
        'reason': reason,
        'moderator': str(ctx.author),
        'timestamp': datetime.utcnow().isoformat()
    })
    
    warning_count = len(bot.warnings[ctx.guild.id][member.id])
    
    embed = discord.Embed(
        title="Warning Issued",
        color=discord.Color.yellow(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="Warning #", value=warning_count, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    
    await ctx.send(embed=embed)
    
    # Auto-action after max warnings
    if warning_count >= MAX_WARNINGS:
        await ctx.send(f"{member.mention} has reached {MAX_WARNINGS} warnings and will be kicked.")
        await member.kick(reason=f"Reached {MAX_WARNINGS} warnings")
        bot.warnings[ctx.guild.id][member.id] = []
    
    logger.info(f"{ctx.author} warned {member} in {ctx.guild.name}")

@bot.command(name='warnings')
@commands.has_permissions(manage_messages=True)
async def warnings(ctx, member: discord.Member):
    """Check warnings for a member."""
    if ctx.guild.id not in bot.warnings or member.id not in bot.warnings[ctx.guild.id]:
        await ctx.send(f"{member.mention} has no warnings.")
        return
    
    member_warnings = bot.warnings[ctx.guild.id][member.id]
    
    embed = discord.Embed(
        title=f"Warnings for {member}",
        color=discord.Color.yellow()
    )
    
    for i, warning in enumerate(member_warnings, 1):
        embed.add_field(
            name=f"Warning {i}",
            value=f"**Reason:** {warning['reason']}\n**By:** {warning['moderator']}",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """Clear messages from the channel."""
    if amount < 1 or amount > 100:
        await ctx.send("Please specify a number between 1 and 100.")
        return
    
    deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include command message
    await ctx.send(f"Cleared {len(deleted) - 1} messages.", delete_after=5)
    logger.info(f"{ctx.author} cleared {len(deleted) - 1} messages in {ctx.guild.name}")

@bot.command(name='slowmode')
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    """Set channel slowmode (0 to disable)."""
    if seconds < 0 or seconds > 21600:
        await ctx.send("Slowmode must be between 0 and 21600 seconds (6 hours).")
        return
    
    await ctx.channel.edit(slowmode_delay=seconds)
    
    if seconds == 0:
        await ctx.send("Slowmode disabled.")
    else:
        await ctx.send(f"Slowmode set to {seconds} seconds.")
    
    logger.info(f"{ctx.author} set slowmode to {seconds}s in {ctx.channel.name}")

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