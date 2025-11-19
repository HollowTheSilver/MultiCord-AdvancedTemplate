"""
Music Player Cog for MultiCord.
Music playback bot with queue management, YouTube support, and voice controls.
"""

import discord
from discord.ext import commands
from typing import Optional
import logging

logger = logging.getLogger('discord.music')


class MusicPlayerCog(commands.Cog, name="Music Player"):
    """
    Music playback bot with queue management and voice controls.

    Features:
    - Join/leave voice channels
    - Play music from YouTube (requires yt-dlp)
    - Queue management (add, view, skip)
    - Playback controls (pause, resume, stop)
    - Volume control
    - Now playing information

    Requirements:
    - FFmpeg installed on system
    - yt-dlp Python package
    - PyNaCl for voice support
    """

    def __init__(self, bot):
        self.bot = bot
        self.logger = logger

        # Music queue per guild
        self.music_queues = {}  # {guild_id: [songs]}

        # Configuration from bot config (with defaults)
        config = getattr(bot, 'config', {})
        music_config = config.get('music', {})

        self.default_volume = music_config.get('default_volume', 50)
        self.max_queue_size = music_config.get('max_queue_size', 100)
        self.max_song_duration = music_config.get('max_song_duration_seconds', 600)

        self.logger.info("Music Player cog loaded")

    def cog_unload(self):
        """Cleanup when cog is unloaded."""
        self.logger.info("Music Player cog unloaded")

    @commands.command(name='join', aliases=['connect'])
    async def join(self, ctx):
        """
        Join the voice channel of the message author.

        Usage: !join
        Aliases: connect
        """
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command!")
            return

        channel = ctx.author.voice.channel

        if ctx.voice_client:
            if ctx.voice_client.channel == channel:
                await ctx.send(f"I'm already in {channel.mention}!")
                return
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()

        await ctx.send(f"Connected to {channel.mention}")
        self.logger.info(f"Joined voice channel: {channel.name} in {ctx.guild.name}")

    @commands.command(name='leave', aliases=['disconnect', 'dc'])
    async def leave(self, ctx):
        """
        Leave the voice channel.

        Usage: !leave
        Aliases: disconnect, dc
        """
        if not ctx.voice_client:
            await ctx.send("I'm not in a voice channel!")
            return

        await ctx.voice_client.disconnect()

        # Clear queue for this guild
        if ctx.guild.id in self.music_queues:
            self.music_queues[ctx.guild.id].clear()

        await ctx.send("Disconnected from voice channel")
        self.logger.info(f"Left voice channel in {ctx.guild.name}")

    @commands.command(name='play', aliases=['p'])
    async def play(self, ctx, *, query: str):
        """
        Play a song (simplified - requires additional implementation).

        Usage: !play <song name or URL>
        Aliases: p

        Note: This is a simplified version. For full YouTube support,
        implement yt-dlp integration with audio extraction.
        """
        # Ensure bot is in voice channel
        if not ctx.voice_client:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You need to be in a voice channel!")
                return

        # Check queue size limit
        if ctx.guild.id in self.music_queues:
            if len(self.music_queues[ctx.guild.id]) >= self.max_queue_size:
                await ctx.send(f"Queue is full! Maximum {self.max_queue_size} songs.")
                return

        # This is a simplified version - in production you'd use yt-dlp
        # to search and download the audio
        embed = discord.Embed(
            title="Added to Queue",
            description=f"🎵 {query}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Requested by {ctx.author}")

        await ctx.send(embed=embed)

        # Add to queue
        if ctx.guild.id not in self.music_queues:
            self.music_queues[ctx.guild.id] = []
        self.music_queues[ctx.guild.id].append({
            'title': query,
            'requester': str(ctx.author)
        })

        self.logger.info(f"Added '{query}' to queue in {ctx.guild.name}")

    @commands.command(name='pause')
    async def pause(self, ctx):
        """
        Pause the current playback.

        Usage: !pause
        """
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("Nothing is playing!")
            return

        ctx.voice_client.pause()
        await ctx.send("⏸️ Paused playback")
        self.logger.info(f"Paused playback in {ctx.guild.name}")

    @commands.command(name='resume')
    async def resume(self, ctx):
        """
        Resume the paused playback.

        Usage: !resume
        """
        if not ctx.voice_client or not ctx.voice_client.is_paused():
            await ctx.send("Nothing is paused!")
            return

        ctx.voice_client.resume()
        await ctx.send("▶️ Resumed playback")
        self.logger.info(f"Resumed playback in {ctx.guild.name}")

    @commands.command(name='stop')
    async def stop(self, ctx):
        """
        Stop playback and clear the queue.

        Usage: !stop
        """
        if not ctx.voice_client:
            await ctx.send("I'm not in a voice channel!")
            return

        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            ctx.voice_client.stop()

        # Clear queue
        if ctx.guild.id in self.music_queues:
            self.music_queues[ctx.guild.id].clear()

        await ctx.send("⏹️ Stopped playback and cleared queue")
        self.logger.info(f"Stopped playback in {ctx.guild.name}")

    @commands.command(name='skip', aliases=['s'])
    async def skip(self, ctx):
        """
        Skip the current song.

        Usage: !skip
        Aliases: s
        """
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("Nothing is playing!")
            return

        ctx.voice_client.stop()
        await ctx.send("⏭️ Skipped current song")
        self.logger.info(f"Skipped song in {ctx.guild.name}")

    @commands.command(name='queue', aliases=['q'])
    async def queue(self, ctx):
        """
        Display the music queue.

        Usage: !queue
        Aliases: q
        """
        if ctx.guild.id not in self.music_queues or not self.music_queues[ctx.guild.id]:
            await ctx.send("The queue is empty!")
            return

        queue_list = self.music_queues[ctx.guild.id]

        embed = discord.Embed(
            title="Music Queue",
            color=discord.Color.blue()
        )

        for i, song in enumerate(queue_list[:10], 1):  # Show first 10
            embed.add_field(
                name=f"{i}. {song['title']}",
                value=f"Requested by {song['requester']}",
                inline=False
            )

        if len(queue_list) > 10:
            embed.set_footer(text=f"And {len(queue_list) - 10} more...")

        await ctx.send(embed=embed)

    @commands.command(name='nowplaying', aliases=['np'])
    async def nowplaying(self, ctx):
        """
        Show the currently playing song.

        Usage: !nowplaying
        Aliases: np
        """
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("Nothing is playing!")
            return

        # This would show actual playing info in a real implementation
        embed = discord.Embed(
            title="Now Playing",
            description="🎵 Current song information would appear here",
            color=discord.Color.purple()
        )

        await ctx.send(embed=embed)

    @commands.command(name='volume', aliases=['vol'])
    async def volume(self, ctx, volume: int):
        """
        Adjust the volume (0-100).

        Usage: !volume <0-100>
        Aliases: vol
        """
        if not ctx.voice_client:
            await ctx.send("I'm not in a voice channel!")
            return

        if not 0 <= volume <= 100:
            await ctx.send("Volume must be between 0 and 100!")
            return

        # In a real implementation, you'd adjust the actual volume here
        # ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"🔊 Volume set to {volume}%")
        self.logger.info(f"Volume set to {volume}% in {ctx.guild.name}")

    @join.error
    @leave.error
    @play.error
    @pause.error
    @resume.error
    @stop.error
    @skip.error
    @queue.error
    @nowplaying.error
    @volume.error
    async def music_error(self, ctx, error):
        """Global error handler for music commands."""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument: {error.param.name}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Invalid argument. Please check command usage with `!help <command>`.")
        else:
            self.logger.error(f"Error in music command: {error}")
            await ctx.send("An error occurred while executing this command.")


async def setup(bot):
    """Discord.py cog setup function."""
    await bot.add_cog(MusicPlayerCog(bot))
