# Music Player Cog

Music playback bot with queue management, YouTube support, and voice controls for Discord servers.

## Features

### Voice Connection
- **`!join`** (aliases: `connect`) - Join your voice channel
- **`!leave`** (aliases: `disconnect`, `dc`) - Leave voice channel and clear queue

### Playback Controls
- **`!play <song>`** (aliases: `p`) - Play a song or add to queue
- **`!pause`** - Pause current playback
- **`!resume`** - Resume paused playback
- **`!stop`** - Stop playback and clear queue
- **`!skip`** (aliases: `s`) - Skip current song

### Queue Management
- **`!queue`** (aliases: `q`) - Display current queue (up to 10 songs)
- **`!nowplaying`** (aliases: `np`) - Show currently playing song

### Audio Controls
- **`!volume <0-100>`** (aliases: `vol`) - Adjust playback volume

## Installation

### System Requirements

**FFmpeg** (Required for audio processing):
- **Windows**: Download from https://ffmpeg.org/download.html
- **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)
- **macOS**: `brew install ffmpeg`

### Via MultiCord CLI (Recommended)
```bash
# Install cog (automatically installs Python dependencies)
multicord cog add <bot-name> music-player

# Verify FFmpeg is installed
ffmpeg -version
```

### Manual Installation
1. Install FFmpeg (see system requirements above)
2. Copy the `music-player` directory to your bot's `cogs/` folder
3. Install Python dependencies:
   ```bash
   cd bots/<bot-name>
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r cogs/music-player/requirements.txt
   ```
4. Restart your bot (cogs are auto-loaded)

## Configuration

Configure music settings in your bot's `config.toml`:

```toml
[music]
# Default volume (0-100)
default_volume = 50

# Maximum queue size
max_queue_size = 100

# Maximum song duration in seconds (prevents abuse)
max_song_duration_seconds = 600  # 10 minutes
```

## Required Permissions

The bot needs these Discord permissions:
- **Send Messages** - Send playback status messages
- **Embed Links** - Send rich embeds for queue/nowplaying
- **Connect** - Join voice channels
- **Speak** - Play audio in voice channels

Optional permissions:
- **Manage Messages** - Clean up command messages

## Usage Examples

### Basic Playback
```
!join
!play Never Gonna Give You Up
!pause
!resume
!skip
!stop
!leave
```

### Queue Management
```
!play Song 1
!play Song 2
!play Song 3
!queue
# Shows:
# 1. Song 1
# 2. Song 2
# 3. Song 3

!skip  # Moves to Song 2
!nowplaying  # Shows Song 2
```

### Volume Control
```
!volume 75  # Set to 75%
!volume 100 # Maximum volume
!volume 25  # Quiet
```

## Implementation Notes

### Simplified Version
This cog provides a **simplified music player interface**. For full YouTube support with actual audio playback, you need to implement:

1. **yt-dlp Integration**: Search and extract audio from YouTube
2. **Audio Streaming**: Stream audio to Discord voice channel
3. **Queue Processing**: Auto-play next song when current ends

### Example Full Implementation

```python
import yt_dlp

# YouTube search and download
ytdl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

async def play_full(self, ctx, query):
    with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
        info = ytdl.extract_info(f"ytsearch:{query}", download=False)
        url = info['entries'][0]['url']

        # Play audio
        audio_source = discord.FFmpegPCMAudio(url)
        ctx.voice_client.play(audio_source, after=lambda e: self.play_next(ctx))
```

### Queue Auto-Play
```python
def play_next(self, ctx):
    """Play next song in queue when current ends."""
    if ctx.guild.id in self.music_queues and self.music_queues[ctx.guild.id]:
        next_song = self.music_queues[ctx.guild.id].pop(0)
        # Play next_song...
```

## Troubleshooting

### "FFmpeg not found" Error
- **Cause**: FFmpeg is not installed or not in system PATH
- **Fix**: Install FFmpeg and restart terminal/bot
- **Verify**: Run `ffmpeg -version` in terminal

### "Nothing is playing!" but bot is in voice
- **Cause**: This is a simplified version without actual audio implementation
- **Fix**: Implement full yt-dlp integration (see Implementation Notes)

### Bot joins but doesn't play audio
- **Cause**: Missing PyNaCl dependency
- **Fix**: `pip install PyNaCl>=1.5.0`
- **Cause**: No audio source configured
- **Fix**: Implement audio streaming with yt-dlp

### "You need to be in a voice channel!"
- **Cause**: User is not in a voice channel
- **Fix**: Join a voice channel before using music commands

### Queue not clearing after !stop
- **Cause**: Bug in queue management
- **Fix**: Use `!leave` to force clear, or restart bot

## Advanced Features (Future)

### Planned Enhancements
- **Spotify Integration**: Play from Spotify playlists
- **Playlist Support**: Load entire YouTube playlists
- **Search Command**: Search YouTube before playing
- **Loop Mode**: Repeat current song or queue
- **Shuffle**: Randomize queue order
- **Bass Boost**: Audio effects and filters
- **Lyrics**: Display lyrics for current song
- **Vote Skip**: Democratic skip with vote threshold
- **DJ Role**: Restrict commands to DJ role
- **Auto-Disconnect**: Leave after inactivity

### Database Persistence
For production, store playlists and favorites in database:

```python
# Example: PostgreSQL playlist storage
async def save_playlist(self, user_id, playlist_name, songs):
    async with self.db.acquire() as conn:
        await conn.execute(
            "INSERT INTO playlists (user_id, name, songs) VALUES ($1, $2, $3)",
            user_id, playlist_name, songs
        )
```

## Resources

- **FFmpeg**: https://ffmpeg.org/download.html
- **yt-dlp**: https://github.com/yt-dlp/yt-dlp
- **discord.py Voice**: https://discordpy.readthedocs.io/en/stable/api.html#voice-related
- **Example Full Bot**: https://github.com/Rapptz/discord.py/tree/master/examples

## Version History

### v1.0.0 (2025-11-19)
- Initial release
- 10 music commands (join, leave, play, pause, resume, stop, skip, queue, nowplaying, volume)
- Queue management system
- Simplified audio interface (requires yt-dlp implementation for full functionality)
- Configuration support (volume, queue size, duration limits)

## Contributing

To report issues or suggest features:
1. Visit the MultiCord Templates repository
2. Open an issue with the `cog:music-player` label
3. Describe your use case or problem

## License

This cog is part of the MultiCord Templates collection and is licensed under the MIT License.
