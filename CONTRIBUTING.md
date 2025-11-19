# Contributing to MultiCord Templates

Thank you for your interest in contributing to the MultiCord Templates repository! This document provides guidelines for creating and submitting Discord bot **templates** and **cogs**.

## 📋 Table of Contents

- [Architecture Overview (v2.1.0)](#architecture-overview-v210)
- [Contributing Templates](#contributing-templates)
- [Contributing Cogs](#contributing-cogs)
- [Testing](#testing)
- [Submission Process](#submission-process)
- [Code Standards](#code-standards)
- [Review Process](#review-process)

---

## 🏗️ Architecture Overview (v2.1.0)

MultiCord uses a **modular architecture**:

- **Templates**: Minimal bot scaffolding (~150-200 lines) with logging, configuration, and cog auto-loading
- **Cogs**: Reusable feature modules (commands, event handlers, background tasks)
- **Auto-Installation**: Templates can specify cogs to install automatically

**Example**: The moderation template is ~160 lines of scaffolding that auto-installs the moderation-tools cog with all commands.

---

## 🎨 Contributing Templates

### Template Philosophy (v2.1.0)

Templates should be **minimal scaffolding** that:
- Set up logging, configuration, and error handling
- Auto-discover and load cogs from `cogs/` directory
- Expose configuration to cogs via `self.config`
- **Do NOT include feature logic** - that belongs in cogs!

### Prerequisites

Before contributing, ensure you have:
- Python 3.9+ installed
- Discord.py 2.0+ knowledge
- MultiCord CLI installed (`pip install multicord`)
- A Discord bot application (for testing)
- Git installed and configured

### Fork and Clone

1. Fork this repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/MultiCord-Templates.git
   cd MultiCord-Templates
   ```
3. Create a new branch:
   ```bash
   git checkout -b template/your-template-name
   ```

---

### Template Requirements (v2.1.0)

#### Mandatory Requirements

All templates **MUST** include:

1. **bot.py** - Minimal bot scaffolding (~150-200 lines)
   - Structured logging (file + console)
   - Configuration loading from `.env` + `config.toml`
   - Cog auto-discovery and loading
   - Graceful shutdown handling
   - **NO feature logic** (use cogs!)

2. **.env.example** - Environment variable template
   ```env
   # Discord Bot Configuration
   DISCORD_TOKEN=your_token_here
   ```

3. **config.toml** - Non-secret configuration
   - Bot metadata (prefix, description)
   - Feature flags
   - **NO tokens or secrets!**

4. **requirements.txt** - Base dependencies
   ```txt
   discord.py>=2.3.0
   python-dotenv>=1.0.0
   tomli>=2.0.0;python_version<"3.11"
   ```

5. **.gitignore** - Security
   ```gitignore
   .env
   __pycache__/
   logs/
   *.pyc
   ```

6. **README.md** - Documentation
   - Template description
   - Features list (from auto-installed cogs)
   - Setup instructions
   - Required Discord permissions

7. **cogs/.gitkeep** - Cogs directory placeholder

#### Optional but Recommended

- Example cogs in `cogs/` directory
- Comprehensive README with troubleshooting
- Screenshots of bot in action

---

### Creating a Template

#### Step 1: Choose a Template Name

- Use lowercase with hyphens: `my-template-name`
- Be descriptive but concise
- Check existing templates to avoid duplicates

#### Step 2: Create Directory Structure

```bash
mkdir your-template-name
cd your-template-name
```

#### Step 3: Create Required Files

**bot.py Template (v2.1.0):**

```python
#!/usr/bin/env python3
"""
[Template Name] - Brief description
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
DESCRIPTION = config["bot"].get("description", "A Discord bot")

# Intents configuration
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

class MyBot(commands.Bot):
    """Your bot class with MultiCord integration."""

    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            description=DESCRIPTION,
            intents=intents,
            help_command=commands.DefaultHelpCommand()
        )
        self.start_time = datetime.utcnow()
        self.bot_name = os.environ.get('BOT_NAME', 'my-bot')
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
        """Auto-discover and load all cogs from cogs/ directory."""
        cogs_dir = Path(__file__).parent / 'cogs'

        if not cogs_dir.exists():
            self.logger.info("No cogs directory found - running without extensions")
            return

        cog_count = 0
        failed_cogs = []

        for item in cogs_dir.iterdir():
            if not item.is_dir() or item.name.startswith('_'):
                continue

            if not (item / '__init__.py').exists():
                self.logger.warning(f"Skipping {item.name} - not a valid Python package")
                continue

            cog_name = f'cogs.{item.name}'
            try:
                await self.load_extension(cog_name)
                self.logger.info(f"✓ Loaded cog: {item.name}")
                cog_count += 1
            except Exception as e:
                self.logger.error(f"✗ Failed to load cog {item.name}: {e}")
                failed_cogs.append((item.name, str(e)))

        if cog_count > 0:
            self.logger.info(f"Successfully loaded {cog_count} cog(s)")
        else:
            self.logger.info("No cogs loaded")

        if failed_cogs:
            self.logger.warning(f"Failed to load {len(failed_cogs)} cog(s)")

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
                name=f"{PREFIX}help"
            )
        )

    async def close(self):
        """Graceful shutdown handler."""
        self.logger.info("Shutting down bot...")
        await super().close()
        self.logger.info("Bot shutdown complete")

# Create bot instance
bot = MyBot()

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
```

**config.toml Template:**

```toml
# [Template Name] Configuration
# Bot token is now stored in .env file for security

[bot]
prefix = "!"
description = "A Discord bot created with MultiCord"

[bot.status]
type = "watching"  # playing, watching, listening
message = "for !help"

[intents]
members = false
presences = false
message_content = true

[features]
# Template-specific features
auto_restart = true
debug_mode = false

[logging]
level = "INFO"  # DEBUG, INFO, WARNING, ERROR
```

**.env.example:**

```env
# Discord Bot Configuration
DISCORD_TOKEN=your_token_here

# Optional: Additional configuration
# DATABASE_URL=sqlite:///bot.db
```

---

### Step 4: Update manifest.json

Add your template to `manifest.json`:

```json
{
  "templates": {
    "your-template": {
      "name": "Your Template Name",
      "description": "Brief description",
      "version": "1.0.0",
      "author": "Your Name",
      "category": "general",
      "tags": ["tag1", "tag2"],
      "discord_py_version": ">=2.3.0",
      "python_version": ">=3.9",
      "files": ["bot.py", "config.toml", ".env.example", ".gitignore", "requirements.txt", "README.md", "cogs/.gitkeep"],
      "featured": false,
      "auto_install_cogs": [
        {
          "id": "cog-name",
          "version": ">=1.0.0",
          "required": true,
          "reason": "Provides core functionality"
        }
      ],
      "changelog": {
        "1.0.0": ["Initial release"]
      }
    }
  }
}
```

---

## 🧩 Contributing Cogs

### Cog Philosophy

Cogs should be **self-contained, reusable feature modules** that:
- Work with any template
- Include all dependencies in `requirements.txt`
- Have comprehensive documentation
- Follow Discord.py cog architecture

### Cog Requirements

All cogs **MUST** include:

1. **__init__.py** - Main cog file
   - Discord.py cog class
   - `async def setup(bot)` function
   - All commands and event handlers
   - Comprehensive docstrings

2. **manifest.json** - Cog metadata
   ```json
   {
     "name": "Cog Name",
     "id": "cog-name",
     "version": "1.0.0",
     "author": "Your Name",
     "description": "Brief description",
     "category": "moderation",
     "tags": ["tag1", "tag2"],
     "discord_py_version": ">=2.0.0",
     "python_version": ">=3.9",
     "database_required": false,
     "files": ["__init__.py", "requirements.txt", "manifest.json", "README.md"],
     "features": {
       "feature1": true
     },
     "permissions": {
       "required": ["send_messages"],
       "optional": []
     },
     "commands": {
       "group": ["command1", "command2"]
     }
   }
   ```

3. **requirements.txt** - Dependencies (even if empty)
   ```txt
   # Additional dependencies beyond discord.py
   # Leave empty if no additional dependencies
   ```

4. **README.md** - Comprehensive documentation
   - Features list
   - Installation instructions
   - Command usage examples
   - Configuration options
   - Troubleshooting guide

---

### Creating a Cog

#### Step 1: Create Cog Directory

```bash
mkdir cogs/your-cog-name
cd cogs/your-cog-name
```

#### Step 2: Create Cog Files

**__init__.py Template:**

```python
"""
Your Cog Name for MultiCord.
Brief description of what this cog does.
"""

import discord
from discord.ext import commands
import logging

logger = logging.getLogger('discord.your-cog')


class YourCog(commands.Cog, name="Your Cog"):
    """
    Brief description of your cog.

    Features:
    - Feature 1
    - Feature 2
    """

    def __init__(self, bot):
        self.bot = bot
        self.logger = logger

        # Load configuration if available
        config = getattr(bot, 'config', {})
        your_config = config.get('your_cog', {})
        self.enabled = your_config.get('enabled', True)

        self.logger.info("Your Cog loaded")

    def cog_unload(self):
        """Cleanup when cog is unloaded."""
        self.logger.info("Your Cog unloaded")

    @commands.command(name='yourcommand')
    async def your_command(self, ctx):
        """
        Brief command description.

        Usage: !yourcommand
        """
        await ctx.send("Hello from your cog!")
        self.logger.info(f"{ctx.author} used yourcommand")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Example event listener."""
        if message.author.bot:
            return
        # Your event handling logic

    @your_command.error
    async def command_error(self, ctx, error):
        """Error handler for your command."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        else:
            self.logger.error(f"Error in command: {error}")


async def setup(bot):
    """Discord.py cog setup function."""
    await bot.add_cog(YourCog(bot))
```

#### Step 3: Update Repository manifest.json

Add your cog to the `cogs` section of `manifest.json`:

```json
{
  "cogs": {
    "your-cog-name": {
      "name": "Your Cog Name",
      "description": "Brief description",
      "version": "1.0.0",
      "author": "Your Name",
      "category": "utility",
      "tags": ["tag1", "tag2"],
      "discord_py_version": ">=2.0.0",
      "python_version": ">=3.9",
      "database_required": false,
      "files": ["__init__.py", "requirements.txt", "manifest.json", "README.md"],
      "featured": false,
      "changelog": {
        "1.0.0": "Initial release"
      }
    }
  }
}
```

---

## 🧪 Testing

### Testing Templates

1. **Create test bot**:
   ```bash
   multicord bot create test-bot --template your-template
   ```

2. **Configure**:
   ```bash
   cd ~/.multicord/bots/test-bot
   nano .env  # Add DISCORD_TOKEN
   ```

3. **Start bot**:
   ```bash
   multicord bot start test-bot
   ```

4. **Verify**:
   - Bot connects successfully
   - Cogs load correctly
   - Commands work as expected
   - No errors in logs

### Testing Cogs

1. **Install cog**:
   ```bash
   multicord cog add test-bot your-cog-name
   ```

2. **Restart bot**:
   ```bash
   multicord bot restart test-bot
   ```

3. **Verify**:
   - Cog loads without errors
   - Commands are registered
   - Functionality works correctly
   - Works with multiple templates

### Validation Checklist

- [ ] No hardcoded tokens or secrets
- [ ] All commands work as documented
- [ ] Error handling is comprehensive
- [ ] Code follows PEP 8 guidelines
- [ ] Documentation is complete
- [ ] Works with MultiCord CLI
- [ ] No unnecessary dependencies
- [ ] Logging is appropriate

---

## 📤 Submission Process

### 1. Commit Changes

```bash
git add your-contribution/
git add manifest.json
git commit -m "Add [name] template/cog"
```

### 2. Push to Fork

```bash
git push origin template/your-branch-name
```

### 3. Create Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Fill in PR description:
   - What you're contributing (template/cog)
   - Features and purpose
   - Testing performed
   - Screenshots (if applicable)

---

## 💻 Code Standards

### Python Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to all functions
- Use type hints where appropriate
- Keep functions focused and small

### Discord.py Best Practices
- Use intents appropriately
- Handle errors gracefully
- Implement proper permission checks
- Use embeds for rich content
- Avoid rate limiting issues

### Security
- **NEVER** commit tokens or secrets
- **ALWAYS** use `.env` files for secrets
- Validate all user input
- Implement proper permission checks
- Include `.env` in `.gitignore`

---

## 👀 Review Process

After submission, maintainers will:

1. **Review code** for quality, security, and standards compliance
2. **Test functionality** with MultiCord CLI
3. **Provide feedback** via PR comments
4. **Request changes** if needed
5. **Merge** once approved

### Review Timeline
- Initial review: Within 3-7 days
- Follow-up: Within 2-3 days
- Merge: Once feedback addressed

---

## ❓ Questions?

- **Issues**: [GitHub Issues](https://github.com/HollowTheSilver/MultiCord-Templates/issues)
- **Discussions**: [GitHub Discussions](https://github.com/HollowTheSilver/MultiCord-Templates/discussions)
- **Discord**: Join our community server (coming soon)

---

Thank you for contributing to MultiCord Templates! Your work helps the entire Discord bot community. 🎉
