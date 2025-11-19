# Moderation Discord Bot Template

**A professional moderation bot template for MultiCord using modular cog architecture (v2.1.0).**

## 🎯 What's Included

This template provides **minimal bot scaffolding** (~160 lines) that automatically installs and loads the **moderation-tools cog** with all moderation features.

### Template Architecture (v2.1.0)

```
moderation/bot.py (~160 lines)
├── Logging (file + console)
├── Configuration loading (.env + TOML)
├── Cog auto-discovery and loading
└── Graceful shutdown handling

Auto-installed: moderation-tools cog
├── 9 moderation commands
├── Auto-moderation features
└── Background mute tracking
```

**Why this matters**: Clean separation between scaffolding (template) and features (cogs) makes the bot easier to maintain, customize, and extend.

---

## 🚀 Features

All moderation features are provided by the **moderation-tools cog** (auto-installed):

### Moderation Commands (9 total)
- **kick** - Remove member from server
- **ban** - Permanently ban member
- **unban** - Unban user by ID
- **mute** - Temporarily mute member
- **unmute** - Remove member mute
- **warn** - Issue warning to member
- **warnings** - View member's warning history
- **clear** - Bulk delete messages
- **slowmode** - Set channel slowmode

### Auto-Moderation
- **Message length limits** - Prevents spam walls
- **Mass mention prevention** - Blocks mention spam
- **Automatic unmute** - Background task checks expired mutes

### Warning System
- Track warnings per user
- Automatic timeout after 3 warnings
- Configurable thresholds

---

## 📋 Prerequisites

- **Python 3.9+**
- **MultiCord CLI** installed (`pip install multicord`)
- **Discord bot token** with moderation permissions

---

## ⚡ Quick Start

### 1. Create Bot from Template

```bash
multicord bot create my-moderator --template moderation
```

**What happens automatically**:
- ✓ Template scaffolding installed (~160 lines)
- ✓ moderation-tools cog auto-installed
- ✓ Virtual environment created
- ✓ Dependencies installed (discord.py 2.3+)
- ✓ .env file created from template

### 2. Configure Bot Token

```bash
cd ~/.multicord/bots/my-moderator
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
multicord bot start my-moderator
```

**That's it!** Your moderation bot is now running with all features.

---

## ⚙️ Configuration

### Bot Configuration (config.toml)

The template includes sensible defaults. Customize as needed:

```toml
[bot]
prefix = "!"
description = "A moderation bot powered by MultiCord"

[bot.status]
type = "watching"
message = "for !help"

[intents]
members = false
presences = false
message_content = true

[moderation]
# Moderation-tools cog configuration
auto_mod = true
max_message_length = 2000
max_mentions = 5
```

### Token Security (v2.0.0+)

**DO**: Store token in `.env` file (auto-created, gitignored)
**DON'T**: Put token in config.toml or commit .env to Git

```env
# .env file (gitignored, auto-created)
DISCORD_TOKEN=your_token_here
```

---

## 🎮 Using Moderation Commands

All commands are provided by the **moderation-tools cog**. See the [moderation-tools README](../cogs/moderation-tools/README.md) for complete documentation.

### Quick Command Reference

#### Basic Moderation
```bash
!kick @user Spamming                    # Kick member
!ban @user Rule violation               # Ban member
!unban 123456789                        # Unban by ID
!mute @user 10m Spam                    # Mute for 10 minutes
!unmute @user                           # Remove mute
!warn @user Breaking rules              # Issue warning
!warnings @user                         # View warnings
!clear 50                               # Delete 50 messages
!slowmode 5                             # 5 second slowmode
```

#### Auto-Moderation
The cog automatically:
- Deletes messages exceeding `max_message_length`
- Deletes messages with more than `max_mentions` mentions
- Automatically unmutes users when mute duration expires

---

## 🔐 Required Discord Permissions

### Essential Permissions
- **Kick Members** - For kick command
- **Ban Members** - For ban/unban commands
- **Moderate Members** - For mute/timeout commands
- **Manage Messages** - For clear command
- **Manage Channels** - For slowmode command

### Permission Setup
1. Go to Discord Developer Portal
2. Select your bot application
3. OAuth2 → URL Generator
4. Select required permissions
5. Use generated URL to invite bot

**Important**: The bot's role must be **above** the roles it needs to moderate.

---

## 🧩 Working with Cogs

### Viewing Installed Cogs

```bash
multicord cog list my-moderator
```

### Installing Additional Cogs

```bash
# Example: Add permissions cog
multicord cog add my-moderator permissions
multicord bot restart my-moderator
```

### Removing Cogs

```bash
multicord cog remove my-moderator moderation-tools
```

**Note**: Removing moderation-tools will remove all moderation commands.

---

## 🛠️ Customization

### Modifying Configuration

Edit `config.toml` to change cog behavior:

```toml
[moderation]
auto_mod = true                  # Enable/disable auto-moderation
max_message_length = 2000        # Max message characters
max_mentions = 5                 # Max mentions per message
```

### Extending the Bot

**Option 1**: Install additional cogs
```bash
multicord cog add my-moderator permissions
multicord cog add my-moderator custom-cog
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

**Don't edit the cog**: Moderation features are in `cogs/moderation-tools/`, not `bot.py`.

---

## 📚 Documentation

### Template Documentation
- **This README** - Template overview and setup
- [Contributing Guide](../CONTRIBUTING.md) - Creating templates and cogs
- [Repository README](../README.md) - Template collection overview

### Cog Documentation
- [moderation-tools README](../cogs/moderation-tools/README.md) - Complete command reference
- [moderation-tools source](../cogs/moderation-tools/__init__.py) - Implementation details

---

## 🐛 Troubleshooting

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
4. Check logs: `multicord bot logs my-moderator`

### Moderation Commands Missing

**Error**: `Command "kick" is not found`

**Solution**:
1. Verify moderation-tools cog is installed: `multicord cog list my-moderator`
2. Check cog loaded successfully in logs
3. Reinstall cog if needed: `multicord cog add my-moderator moderation-tools`

### Permission Errors

**Error**: `Missing Permissions` when using commands

**Solution**:
- Bot role must be **above** roles it's moderating
- Verify bot has required permissions (see Required Permissions section)
- Check channel-specific permission overrides

### Auto-Moderation Not Working

**Error**: Spam messages not being deleted

**Solution**:
1. Check `auto_mod = true` in config.toml
2. Verify bot has "Manage Messages" permission
3. Check `max_message_length` and `max_mentions` thresholds
4. Restart bot after config changes

---

## 🔄 Template Version History

### v2.1.0 (Current)
- **Architecture**: Refactored to cog-based system
- **Template**: Now minimal scaffolding (~160 lines, 64% reduction)
- **Cogs**: Features extracted to moderation-tools cog (auto-installed)
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

## 🤝 Contributing

Want to improve this template or create your own?

1. Fork the [MultiCord-Templates](https://github.com/HollowTheSilver/MultiCord-Templates) repository
2. Read the [Contributing Guide](../CONTRIBUTING.md)
3. Follow v2.1.0 template standards (minimal scaffolding, cog-based)
4. Submit a pull request

---

## 📜 License

MIT License - see [repository LICENSE](https://github.com/HollowTheSilver/MultiCord-Templates/blob/main/LICENSE) file

---

## 🔗 Links

- **MultiCord CLI**: https://github.com/HollowTheSilver/MultiCord
- **Templates Repository**: https://github.com/HollowTheSilver/MultiCord-Templates
- **Report Issues**: https://github.com/HollowTheSilver/MultiCord-Templates/issues
- **Discord.py Documentation**: https://discordpy.readthedocs.io/

---

**Built with ❤️ using [MultiCord](https://github.com/HollowTheSilver/MultiCord) | v2.1.0 - Modular Architecture**
