# Music Discord Bot Template

**A feature-rich music bot template for MultiCord using modular cog architecture (v2.1.0).**

## 🎯 What's Included

This template provides **minimal bot scaffolding** (~160 lines) that automatically installs and loads the **music-player cog** with all music playback features.

### Template Architecture (v2.1.0)

```
music/bot.py (~160 lines)
├── Logging (file + console)
├── Configuration loading (.env + TOML)
├── Cog auto-discovery and loading
└── Graceful shutdown handling

Auto-installed: music-player cog
├── 10 music commands
├── Queue management
└── YouTube integration ready
```

**Why this matters**: Clean separation between scaffolding (template) and features (cogs) makes the bot easier to maintain, customize, and extend with additional audio sources.

---

## 🎵 Features

All music features are provided by the **music-player cog** (auto-installed):

### Voice & Playback Commands (10 total)
- **join** - Join your voice channel
- **leave** - Leave voice channel
- **play** - Play song from URL or search
- **pause** - Pause current song
- **resume** - Resume playback
- **stop** - Stop and clear queue
- **skip** - Skip to next song
- **queue** - View current queue
- **nowplaying** - Show current song info
- **volume** - Adjust playback volume (0-100)

### Queue Management
- Add songs to queue
- View queue with song list
- Skip songs
- Clear entire queue
- Automatic queue progression

### YouTube Integration
- Ready for yt-dlp implementation
- URL and search query support
- Metadata extraction
- High-quality audio streaming

---

## 📋 Prerequisites

### System Requirements
- **Python 3.9+**
- **MultiCord CLI** installed (`pip install multicord`)
- **FFmpeg** installed and in system PATH
- **Discord bot token** with voice permissions

### Installing FFmpeg

**Windows**:
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to system PATH
4. Verify: `ffmpeg -version`

**Linux**:
```bash
sudo apt update
sudo apt install ffmpeg
ffmpeg -version
```

**macOS**:
```bash
brew install ffmpeg
ffmpeg -version
```

---

## ⚡ Quick Start

### 1. Create Bot from Template

```bash
multicord bot create my-music-bot --template music
```

**What happens automatically**:
- ✓ Template scaffolding installed (~160 lines)
- ✓ music-player cog auto-installed
- ✓ Virtual environment created
- ✓ Dependencies installed (discord.py, yt-dlp, PyNaCl)
- ✓ .env file created from template

### 2. Configure Bot Token

```bash
cd ~/.multicord/bots/my-music-bot
nano .env  # Add your DISCORD_TOKEN
```

**Add your Discord bot token**:
```env
# Discord Bot Configuration
DISCORD_TOKEN=your_bot_token_here
```

**Important**: The .env file is auto-created by the CLI. Never commit it to Git (already in .gitignore).

### 3. Start the Bot

```bash
multicord bot start my-music-bot
```

**That's it!** Your music bot is now ready to play audio.

---

## ⚙️ Configuration

### Bot Configuration (config.toml)

The template includes sensible defaults. Customize as needed:

```toml
[bot]
prefix = "!"
description = "A music bot powered by MultiCord"

[bot.status]
type = "listening"
message = "to music"

[intents]
members = false
presences = false
message_content = true

[music]
# Music-player cog configuration
default_volume = 50             # Default volume (0-100)
max_queue_size = 100            # Maximum songs in queue
auto_disconnect = true          # Auto-leave when queue empty
```

### Token Security (v2.0.0+)

**DO**: Store token in `.env` file (auto-created, gitignored)
**DON'T**: Put token in config.toml or commit .env to Git

```env
# .env file (gitignored, auto-created)
DISCORD_TOKEN=your_token_here
```

---

## 🎮 Using Music Commands

All commands are provided by the **music-player cog**. See the [music-player README](../cogs/music-player/README.md) for complete documentation.

### Quick Command Reference

#### Voice Connection
```bash
!join                           # Bot joins your voice channel
!leave                          # Bot leaves voice channel
```

#### Playback
```bash
!play <URL or search query>     # Play or queue a song
!pause                          # Pause current song
!resume                         # Resume playback
!stop                           # Stop and clear queue
!skip                           # Skip to next song
!volume 75                      # Set volume to 75%
```

#### Queue Management
```bash
!queue                          # View current queue
!nowplaying                     # Show current song info
```

### Example Usage

```
User: !join
Bot: ✅ Joined voice channel

User: !play Never Gonna Give You Up
Bot: 🎵 Now Playing: Rick Astley - Never Gonna Give You Up

User: !play https://www.youtube.com/watch?v=dQw4w9WgXcQ
Bot: ✅ Added to queue: Position 1

User: !queue
Bot: 📃 Current Queue (2 songs):
     1. Song Name 1 (3:42)
     2. Song Name 2 (4:15)

User: !volume 80
Bot: 🔊 Volume set to 80%

User: !skip
Bot: ⏭️ Skipped to next song
```

---

## 🔐 Required Discord Permissions

### Essential Permissions
- **Send Messages** - To respond to commands
- **Embed Links** - To send rich embeds
- **Connect** - To join voice channels
- **Speak** - To play audio

### Optional Permissions
- **Move Members** - To move users between channels (future features)
- **Priority Speaker** - For priority audio (future features)

### Permission Setup
1. Go to Discord Developer Portal
2. Select your bot application
3. OAuth2 → URL Generator
4. Select required permissions
5. Use generated URL to invite bot

---

## 🧩 Working with Cogs

### Viewing Installed Cogs

```bash
multicord cog list my-music-bot
```

### Installing Additional Cogs

```bash
# Example: Add moderation features
multicord cog add my-music-bot moderation-tools
multicord bot restart my-music-bot
```

### Removing Cogs

```bash
multicord cog remove my-music-bot music-player
```

**Note**: Removing music-player will remove all music commands.

---

## 🛠️ Customization

### Modifying Configuration

Edit `config.toml` to change cog behavior:

```toml
[music]
default_volume = 75             # Start at 75% volume
max_queue_size = 200            # Allow 200 songs in queue
auto_disconnect = false         # Stay in channel after queue ends
```

### Extending the Bot

**Option 1**: Install additional cogs
```bash
multicord cog add my-music-bot permissions
multicord cog add my-music-bot custom-cog
```

**Option 2**: Create custom cogs
1. Create `cogs/my_custom_cog/` directory
2. Add `__init__.py` with Discord.py cog class
3. Restart bot - cogs auto-load from `cogs/` directory

See [CONTRIBUTING.md](../CONTRIBUTING.md) for cog creation guide.

### Modifying the Scaffolding

The template is intentionally minimal (~160 lines). To customize:

1. **Logging**: Edit logging configuration in `bot.py`
2. **Intents**: Modify Discord.py intents setup
3. **Status**: Change bot status in `on_ready` event
4. **Error Handling**: Add global error handlers

**Don't edit the cog**: Music features are in `cogs/music-player/`, not `bot.py`.

---

## 📚 Documentation

### Template Documentation
- **This README** - Template overview and setup
- [Contributing Guide](../CONTRIBUTING.md) - Creating templates and cogs
- [Repository README](../README.md) - Template collection overview

### Cog Documentation
- [music-player README](../cogs/music-player/README.md) - Complete command reference
- [music-player source](../cogs/music-player/__init__.py) - Implementation details

---

## 🐛 Troubleshooting

### FFmpeg Not Found

**Error**: `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`

**Solution**:
1. Install FFmpeg (see Prerequisites section)
2. Verify installation: `ffmpeg -version`
3. Ensure FFmpeg is in system PATH
4. Restart terminal/bot after PATH changes

### Bot Won't Start

**Error**: `Missing DISCORD_TOKEN environment variable`

**Solution**:
1. Check `.env` file exists in bot directory
2. Verify `DISCORD_TOKEN=...` is set correctly
3. No spaces around `=` sign
4. Restart bot after editing `.env`

### Commands Not Working

**Error**: Commands don't respond

**Solution**:
1. Verify bot has `message_content` intent enabled (Developer Portal)
2. Check bot has permissions in the channel
3. Ensure command prefix matches config (default: `!`)
4. Check logs: `multicord bot logs my-music-bot`

### Music Commands Missing

**Error**: `Command "play" is not found`

**Solution**:
1. Verify music-player cog is installed: `multicord cog list my-music-bot`
2. Check cog loaded successfully in logs
3. Reinstall cog if needed: `multicord cog add my-music-bot music-player`

### No Audio Playback

**Error**: Bot joins but no sound plays

**Solution**:
1. Check bot has "Speak" permission in voice channel
2. Verify volume is not 0: `!volume 50`
3. Ensure FFmpeg is correctly installed
4. Check bot role isn't muted in voice channel settings
5. Try different song/video

### YouTube Download Fails

**Error**: `ERROR: Unable to extract video data`

**Solution**:
1. Update yt-dlp: `pip install --upgrade yt-dlp` (in bot's venv)
2. Check if video is region-locked or age-restricted
3. Try a different video
4. Check internet connection

### Permission Errors

**Error**: `Missing Permissions` when trying to join

**Solution**:
- Verify bot has "Connect" and "Speak" permissions
- Check voice channel user limit (bot needs access)
- Ensure bot isn't banned from the channel
- Check channel-specific permission overrides

### Bot Stuck in Voice Channel

**Error**: Bot doesn't leave after queue ends

**Solution**:
- Use `!leave` to force disconnect
- Check `auto_disconnect = true` in config.toml
- Restart bot: `multicord bot restart my-music-bot`

---

## 🔄 Template Version History

### v2.1.0 (Current)
- **Architecture**: Refactored to cog-based system
- **Template**: Now minimal scaffolding (~160 lines, 56% reduction)
- **Cogs**: Features extracted to music-player cog (auto-installed)
- **Auto-Installation**: Cogs automatically installed during bot creation
- **Benefits**: Modular, reusable, easier to maintain

### v2.0.0
- **Security**: Token storage moved to `.env` files
- **Enhancement**: Auto-load cogs from `cogs/` directory
- **Enhancement**: Structured logging with file and console output
- **Enhancement**: Graceful shutdown handling

### v1.0.0
- Initial release with all features in single bot.py file

---

## ⚠️ Known Limitations

- **YouTube Implementation**: Requires yt-dlp integration (template provides structure)
- **Search Functionality**: Basic search implementation (can be enhanced)
- **Playlist Support**: Limited playlist handling
- **Live Streams**: Basic live stream support

**These limitations can be addressed by enhancing the music-player cog.**

---

## 🚀 Performance Notes

- **Caching**: Song metadata can be cached to improve performance
- **Concurrent Bots**: Each bot runs in isolated venv with independent dependencies
- **Memory Usage**: Queue size affects memory (configure `max_queue_size`)
- **Network**: YouTube downloads require stable internet connection

---

## 🤝 Contributing

Want to improve this template or create your own?

1. Fork the [MultiCord-Templates](https://github.com/HollowTheSilver/MultiCord-Templates) repository
2. Read the [Contributing Guide](../CONTRIBUTING.md)
3. Follow v2.1.0 template standards (minimal scaffolding, cog-based)
4. Submit a pull request

**Ideas for Music Cog Enhancements**:
- Spotify integration
- SoundCloud support
- Playlist management
- Audio filters/effects
- Lyrics fetching
- Vote skip system

---

## 📜 License

MIT License - see [repository LICENSE](https://github.com/HollowTheSilver/MultiCord-Templates/blob/main/LICENSE) file

---

## 🔗 Links

- **MultiCord CLI**: https://github.com/HollowTheSilver/MultiCord
- **Templates Repository**: https://github.com/HollowTheSilver/MultiCord-Templates
- **Report Issues**: https://github.com/HollowTheSilver/MultiCord-Templates/issues
- **Discord.py Documentation**: https://discordpy.readthedocs.io/
- **yt-dlp Documentation**: https://github.com/yt-dlp/yt-dlp

---

**Built with ❤️ using [MultiCord](https://github.com/HollowTheSilver/MultiCord) | v2.1.0 - Modular Architecture**
