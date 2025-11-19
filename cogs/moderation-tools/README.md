# Moderation Tools Cog

Comprehensive moderation toolkit for Discord servers with kick, ban, mute, warning system, and auto-moderation features.

## Features

### Moderation Commands
- **`!kick @member [reason]`** - Kick a member from the server
- **`!ban @member [reason]`** - Ban a member from the server
- **`!unban <user_id>`** - Unban a user by their ID

### Mute System
- **`!mute @member [duration] [reason]`** - Mute a member temporarily or permanently
- **`!unmute @member`** - Remove mute from a member
- Automatic mute role creation with proper permissions
- Background task to automatically remove expired mutes

### Warning System
- **`!warn @member <reason>`** - Issue a warning to a member
- **`!warnings @member`** - Check warnings for a member
- Auto-kick after reaching max warnings (configurable, default: 3)

### Channel Management
- **`!clear <amount>`** - Delete multiple messages (1-100)
- **`!slowmode <seconds>`** - Set channel slowmode (0 to disable)

### Auto-Moderation
- Automatically deletes messages over 1000 characters
- Automatically deletes messages with mass mentions (>5 users)
- Configurable via bot's `config.toml`

## Installation

### Via MultiCord CLI (Recommended)
```bash
multicord cog add <bot-name> moderation-tools
```

### Manual Installation
1. Copy the `moderation-tools` directory to your bot's `cogs/` folder
2. Restart your bot (cogs are auto-loaded if your template supports it)

## Configuration

Configure moderation settings in your bot's `config.toml`:

```toml
[moderation]
# Enable/disable auto-moderation
auto_mod = true

# Maximum warnings before auto-kick
max_warnings = 3

# Default mute duration in minutes (if not specified in command)
mute_duration_minutes = 10
```

## Required Permissions

The bot needs these Discord permissions:
- **Send Messages** - Send confirmation messages
- **Embed Links** - Send rich embeds
- **Kick Members** - Use kick command
- **Ban Members** - Use ban/unban commands
- **Manage Roles** - Use mute/unmute commands
- **Manage Messages** - Use clear command and auto-mod
- **Manage Channels** - Use slowmode command

Users need these permissions to use commands:
- **Kick Members** - `!kick` command
- **Ban Members** - `!ban`, `!unban` commands
- **Manage Roles** - `!mute`, `!unmute` commands
- **Manage Messages** - `!warn`, `!warnings`, `!clear` commands
- **Manage Channels** - `!slowmode` command

## Usage Examples

### Kick a member
```
!kick @spammer Spamming in general chat
```

### Ban a member
```
!ban @rulebreaker Repeated violations of server rules
```

### Mute for 10 minutes
```
!mute @troublemaker 10 Posting NSFW content
```

### Permanent mute
```
!mute @bot-user Confirmed bot account
```

### Issue warning
```
!warn @user Please read the rules before posting
```

### Check warnings
```
!warnings @user
```

### Clear 50 messages
```
!clear 50
```

### Set 10-second slowmode
```
!slowmode 10
```

## Architecture

### Data Persistence
Currently stores warnings and mute data in memory (resets on bot restart). For production use, consider implementing database persistence:

```python
# Example: Add PostgreSQL persistence
async def get_warnings(self, guild_id: int, user_id: int) -> list:
    async with self.db.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM warnings WHERE guild_id = $1 AND user_id = $2",
            guild_id, user_id
        )
```

### Background Tasks
- **Mute Check Task**: Runs every 30 seconds to check for expired mutes
- Automatically removes muted role when timer expires
- Handles bot restarts gracefully

### Auto-Moderation
- Message length limit: 1000 characters
- Mass mention limit: 5 users
- Can be disabled via config: `auto_mod = false`

## Troubleshooting

### "You don't have permission to use this command"
- Check that you have the required Discord permissions
- Check that the bot has the required permissions
- Ensure you're not trying to moderate someone with a higher role

### "I don't have permission to unban users"
- Ensure the bot has Ban Members permission
- Check that the bot's role is higher than the banned user's role

### Mute role permissions not working
- The cog automatically sets permissions when creating the Mute role
- If channels are added later, manually set Mute role permissions:
  - Send Messages: ❌
  - Add Reactions: ❌
  - Speak: ❌

### Warnings persist after kick
- This is intentional - warnings are only cleared after auto-kick
- To manually clear, the bot owner can modify the data structure

## Version History

### v1.0.0 (2025-11-19)
- Initial release
- 9 moderation commands
- Auto-moderation system
- Warning system with auto-kick
- Temporary mute system with background task

## Contributing

To report issues or suggest features:
1. Visit the MultiCord Templates repository
2. Open an issue with the `cog:moderation-tools` label
3. Describe your use case or problem

## License

This cog is part of the MultiCord Templates collection and is licensed under the MIT License.
