"""
Moderation Tools Cog for MultiCord.
Comprehensive moderation toolkit with kick, ban, mute, warn, and auto-moderation features.
"""

import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger('discord.moderation')


class ModerationToolsCog(commands.Cog, name="Moderation Tools"):
    """
    Comprehensive moderation toolkit for Discord servers.

    Features:
    - Kick/ban/unban members
    - Temporary and permanent mutes
    - Warning system with auto-kick
    - Message clearing (bulk delete)
    - Channel slowmode control
    - Auto-moderation (message length, mass mentions)
    """

    def __init__(self, bot):
        self.bot = bot
        self.logger = logger

        # Moderation data (in production, use a database)
        self.warnings = {}  # {guild_id: {user_id: [warnings]}}
        self.muted_users = {}  # {guild_id: {user_id: unmute_time}}

        # Configuration from bot config (with defaults)
        config = getattr(bot, 'config', {})
        mod_config = config.get('moderation', {})

        self.auto_mod_enabled = mod_config.get('auto_mod', True)
        self.max_warnings = mod_config.get('max_warnings', 3)
        self.mute_duration = mod_config.get('mute_duration_minutes', 10)

        # Start background tasks
        self.check_mutes.start()

        self.logger.info("Moderation Tools cog loaded")

    def cog_unload(self):
        """Cleanup when cog is unloaded."""
        self.check_mutes.cancel()
        self.logger.info("Moderation Tools cog unloaded")

    @tasks.loop(seconds=30)
    async def check_mutes(self):
        """Check and remove expired mutes."""
        current_time = datetime.utcnow()
        for guild_id in list(self.muted_users.keys()):
            for user_id in list(self.muted_users[guild_id].keys()):
                if self.muted_users[guild_id][user_id] <= current_time:
                    # Unmute user
                    guild = self.bot.get_guild(guild_id)
                    if guild:
                        member = guild.get_member(user_id)
                        if member:
                            muted_role = discord.utils.get(guild.roles, name="Muted")
                            if muted_role and muted_role in member.roles:
                                await member.remove_roles(muted_role)
                                self.logger.info(f"Auto-unmuted {member} in {guild.name}")

                    del self.muted_users[guild_id][user_id]

    @check_mutes.before_loop
    async def before_check_mutes(self):
        """Wait for bot to be ready before starting mute checks."""
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message):
        """Auto-moderation for messages."""
        if message.author.bot or not message.guild:
            return

        if not self.auto_mod_enabled:
            return

        # Check for spam (message too long)
        if len(message.content) > 1000:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, your message was too long and has been deleted.",
                delete_after=5
            )
            self.logger.info(f"Auto-deleted long message from {message.author} in {message.guild.name}")
            return

        # Check for mass mentions
        if len(message.mentions) > 5:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, please don't mass mention users.",
                delete_after=5
            )
            self.logger.info(f"Auto-deleted mass mention from {message.author} in {message.guild.name}")
            return

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: Optional[str] = "No reason provided"):
        """
        Kick a member from the server.

        Usage: !kick @member [reason]
        Requires: Kick Members permission
        """
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
        self.logger.info(f"{ctx.author} kicked {member} from {ctx.guild.name}")

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: Optional[str] = "No reason provided"):
        """
        Ban a member from the server.

        Usage: !ban @member [reason]
        Requires: Ban Members permission
        """
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
        self.logger.info(f"{ctx.author} banned {member} from {ctx.guild.name}")

    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        """
        Unban a user by their ID.

        Usage: !unban <user_id>
        Requires: Ban Members permission
        """
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"Unbanned {user.mention}")
            self.logger.info(f"{ctx.author} unbanned {user} in {ctx.guild.name}")
        except discord.NotFound:
            await ctx.send("User not found or not banned.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to unban users.")

    @commands.command(name='mute')
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: Optional[int] = None, *, reason: Optional[str] = "No reason provided"):
        """
        Mute a member (duration in minutes).

        Usage: !mute @member [duration] [reason]
        Example: !mute @user 10 Spamming
        Requires: Manage Roles permission
        """
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
            if ctx.guild.id not in self.muted_users:
                self.muted_users[ctx.guild.id] = {}
            self.muted_users[ctx.guild.id][member.id] = unmute_time
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
        self.logger.info(f"{ctx.author} muted {member} in {ctx.guild.name}")

    @commands.command(name='unmute')
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        """
        Unmute a member.

        Usage: !unmute @member
        Requires: Manage Roles permission
        """
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role or muted_role not in member.roles:
            await ctx.send(f"{member.mention} is not muted.")
            return

        await member.remove_roles(muted_role)

        # Remove from muted users dict
        if ctx.guild.id in self.muted_users and member.id in self.muted_users[ctx.guild.id]:
            del self.muted_users[ctx.guild.id][member.id]

        await ctx.send(f"Unmuted {member.mention}")
        self.logger.info(f"{ctx.author} unmuted {member} in {ctx.guild.name}")

    @commands.command(name='warn')
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        """
        Warn a member.

        Usage: !warn @member <reason>
        Requires: Manage Messages permission
        Note: Auto-kicks after reaching max warnings (default: 3)
        """
        if ctx.guild.id not in self.warnings:
            self.warnings[ctx.guild.id] = {}
        if member.id not in self.warnings[ctx.guild.id]:
            self.warnings[ctx.guild.id][member.id] = []

        self.warnings[ctx.guild.id][member.id].append({
            'reason': reason,
            'moderator': str(ctx.author),
            'timestamp': datetime.utcnow().isoformat()
        })

        warning_count = len(self.warnings[ctx.guild.id][member.id])

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
        if warning_count >= self.max_warnings:
            await ctx.send(f"{member.mention} has reached {self.max_warnings} warnings and will be kicked.")
            await member.kick(reason=f"Reached {self.max_warnings} warnings")
            self.warnings[ctx.guild.id][member.id] = []

        self.logger.info(f"{ctx.author} warned {member} in {ctx.guild.name}")

    @commands.command(name='warnings')
    @commands.has_permissions(manage_messages=True)
    async def warnings_command(self, ctx, member: discord.Member):
        """
        Check warnings for a member.

        Usage: !warnings @member
        Requires: Manage Messages permission
        """
        if ctx.guild.id not in self.warnings or member.id not in self.warnings[ctx.guild.id]:
            await ctx.send(f"{member.mention} has no warnings.")
            return

        member_warnings = self.warnings[ctx.guild.id][member.id]

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

    @commands.command(name='clear')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        """
        Clear messages from the channel.

        Usage: !clear <amount>
        Requires: Manage Messages permission
        Note: Amount must be between 1 and 100
        """
        if amount < 1 or amount > 100:
            await ctx.send("Please specify a number between 1 and 100.")
            return

        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include command message
        await ctx.send(f"Cleared {len(deleted) - 1} messages.", delete_after=5)
        self.logger.info(f"{ctx.author} cleared {len(deleted) - 1} messages in {ctx.guild.name}")

    @commands.command(name='slowmode')
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        """
        Set channel slowmode (0 to disable).

        Usage: !slowmode <seconds>
        Requires: Manage Channels permission
        Note: Slowmode must be between 0 and 21600 seconds (6 hours)
        """
        if seconds < 0 or seconds > 21600:
            await ctx.send("Slowmode must be between 0 and 21600 seconds (6 hours).")
            return

        await ctx.channel.edit(slowmode_delay=seconds)

        if seconds == 0:
            await ctx.send("Slowmode disabled.")
        else:
            await ctx.send(f"Slowmode set to {seconds} seconds.")

        self.logger.info(f"{ctx.author} set slowmode to {seconds}s in {ctx.channel.name}")

    @kick.error
    @ban.error
    @unban.error
    @mute.error
    @unmute.error
    @warn.error
    @warnings_command.error
    @clear.error
    @slowmode.error
    async def moderation_error(self, ctx, error):
        """Global error handler for moderation commands."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Invalid argument. Please check command usage with `!help <command>`.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Member not found.")
        else:
            self.logger.error(f"Error in moderation command: {error}")
            await ctx.send("An error occurred while executing this command.")


async def setup(bot):
    """Discord.py cog setup function."""
    await bot.add_cog(ModerationToolsCog(bot))
