# MultiCord Discord Bot Templates

**Official template repository for [MultiCord](https://github.com/HollowTheSilver/MultiCord) - Professional Discord bot management made easy.**

This repository contains production-ready Discord bot templates that work seamlessly with the MultiCord CLI. Templates provide clean bot scaffolding, while **cogs** deliver the actual features through automatic installation.

## 🎯 Architecture (v2.1.0)

### Templates = Scaffolding, Cogs = Features

MultiCord uses a **modular architecture** where:

- **Templates** (~160 lines): Minimal bot scaffolding with logging, configuration, and cog auto-loading
- **Cogs** (reusable modules): Feature-rich command sets that are automatically installed and loaded
- **Automatic Integration**: When you create a bot from a template, required cogs are installed automatically

**Example**: Creating a moderation bot installs the minimal template PLUS the moderation-tools cog with all commands.

## 🚀 Available Templates

### Basic Bot Template
**Perfect for**: Learning Discord.py, simple utility bots, custom bot foundations

A minimal yet complete Discord bot with:
- Structured logging (file + console)
- Configuration management (`.env` + TOML)
- Automatic cog discovery and loading
- Error handling and graceful shutdown
- Production-ready defaults

**Use case**: Start here for any custom bot project. Install additional cogs as needed.

```bash
multicord bot create my-bot --template basic
# Creates a clean bot scaffold - add cogs for features!
```

---

### Moderation Bot Template
**Perfect for**: Community management, server moderation, anti-spam

**Template (~160 lines)** + **moderation-tools cog (auto-installed)** with:
- **Moderation Commands**: kick, ban, unban, mute, unmute
- **Warning System**: warn, warnings (tracks violations)
- **Channel Management**: clear (bulk delete), slowmode
- **Auto-Moderation**: Message length limits, mass mention prevention
- **Mute Tracking**: Automatic unmute with background task

**Use case**: Complete server moderation solution, ready to deploy.

```bash
multicord bot create mod-bot --template moderation
# Automatically installs moderation-tools cog
```

---

### Music Bot Template
**Perfect for**: Playing music, voice channel utilities, entertainment

**Template (~160 lines)** + **music-player cog (auto-installed)** with:
- **Voice Connection**: join, leave (automatic channel detection)
- **Playback Controls**: play, pause, resume, stop, skip
- **Queue Management**: queue (view), nowplaying (current song)
- **Volume Control**: volume adjustment (0-100)
- **YouTube Integration**: Ready for yt-dlp implementation

**Use case**: Add music functionality to your server.

```bash
multicord bot create music-bot --template music
# Automatically installs music-player cog
# Requires FFmpeg (see setup instructions)
```

---

### Business Bot Template (Advanced)
**Perfect for**: Commissioned projects, enterprise deployments, custom solutions

A professional foundation with:
- Automatic cog discovery and loading
- Structured logging with rotation
- TOML configuration + environment variables
- Production-ready architecture
- No pre-installed cogs (add what you need)

**Use case**: Professional bot projects where you choose the exact features needed.

```bash
multicord bot create client-bot --template business
# Then: multicord cog add client-bot <cog-name>
```

---

## 🧩 Available Cogs

### Core Cogs

#### **moderation-tools** (Auto-installed with moderation template)
Comprehensive moderation toolkit with 9 commands, auto-moderation, and mute tracking.

#### **music-player** (Auto-installed with music template)
Complete music playback system with queue management and voice controls.

#### **permissions** (Optional - Install manually)
Enterprise-grade 9-level permission hierarchy with intelligent role detection.

```bash
# Install optional cogs (with automatic dependency resolution)
multicord cog add my-bot permissions
```

### Cog Dependencies ⭐ NEW in v1.2

Cogs can declare dependencies on other cogs. When you install a cog, the CLI automatically:
1. Checks for required dependencies
2. Prompts you to install missing dependencies
3. Installs dependencies in the correct order
4. Detects and prevents circular dependencies

```bash
# Example: Installing a cog with dependencies
$ multicord cog add my-bot advanced-moderation

Checking dependencies for 'advanced-moderation'...
  ⚠ Missing: permissions (>=1.0.0)

Install dependencies automatically? [Y/n]: y
  → Installing permissions... ✓
  → Installing advanced-moderation... ✓

✓ Cogs installed successfully
```

---

## 📦 Installation & Usage

### Quick Start

```bash
# Install MultiCord CLI
pip install multicord

# Create a bot (templates + cogs auto-downloaded)
multicord bot create my-bot --template moderation

# Configure bot token
cd ~/.multicord/bots/my-bot
nano .env  # Add: DISCORD_TOKEN=your_token_here

# Start bot
multicord bot start my-bot
```

That's it! The bot runs with all moderation features ready to use.

---

## 🛠️ Creating a Bot (Detailed)

### Step 1: Create from Template

```bash
# Create a new bot from the basic template
multicord bot create my-awesome-bot --template basic

# What happens automatically:
# ✓ Template installed from repository
# ✓ .env file created from .env.example
# ✓ Virtual environment created for bot
# ✓ Template requirements installed
# ✓ Required cogs auto-installed (if any)
# ✓ Logs and data directories created
```

### Step 2: Configure Token

```bash
# Navigate to bot directory
cd ~/.multicord/bots/my-awesome-bot

# Edit .env file and add your Discord token
nano .env
```

Add this line:
```env
DISCORD_TOKEN=your_discord_bot_token_here
```

### Step 3: Start Bot

```bash
multicord bot start my-awesome-bot
```

---

## 📝 Template Structure (v2.1.0)

```
template-name/
├── bot.py              # Minimal bot scaffolding (~160 lines)
├── config.toml         # Non-secret configuration
├── .env.example        # Environment variable template
├── .gitignore          # Security (excludes .env, logs, etc.)
├── requirements.txt    # Base Python dependencies
├── cogs/               # Cogs directory (auto-loaded)
│   └── .gitkeep
└── README.md          # Template documentation
```

### Configuration Security (v2.0.0+)

**Token Storage**: All templates now use `.env` files for secrets (never committed to Git).

- **`.env`** - Contains `DISCORD_TOKEN=...` (gitignored, auto-created)
- **`config.toml`** - Contains non-secret config (prefix, features, etc.)

---

## 🎨 Template Workflow

### Before v2.1.0 (Monolithic):
```
moderation/bot.py (450 lines)
└── All commands hardcoded in template
    ❌ Not reusable across templates
    ❌ Hard to maintain
    ❌ Mixed concerns
```

### v2.1.0+ (Modular):
```
moderation/bot.py (160 lines)  # Scaffolding
└── Loads: moderation-tools cog (400 lines)  # Features
    ✓ Reusable in any template
    ✓ Easy to maintain
    ✓ Clean separation
```

**Result**: Templates are now **~64% smaller** and features are **fully modular**.

---

## 📋 V3.0 MANIFEST SYSTEM (✅ DEPLOYED January 2026)

### Overview

**Status**: ✅ Complete and Merged (January 11, 2026)

Templates v3.0 introduces a 3-layer manifest system with JSON Schema validation, providing professional dependency management and explicit version compatibility.

### The Three Layers

#### **Layer 1: Repository Collection** (`multicord.json`)
Located at repository root, describes the entire collection:

```json
{
  "$schema": "https://multicord.io/schemas/multicord.schema.json",
  "type": "collection",
  "name": "MultiCord Official Templates",
  "version": "3.0.0",
  "items": ["basic/", "moderation/", "cogs/moderation-tools/"]
}
```

**Purpose**: Registry of all templates and cogs in this repository.

#### **Layer 2: Individual Items** (`template.json` / `cog.json`)
Located in each template/cog directory:

```json
{
  "$schema": "https://multicord.io/schemas/template.schema.json",
  "type": "template",
  "id": "moderation",
  "name": "Moderation Bot",
  "version": "2.1.0",
  "requires_cogs": ["moderation-tools@^1.0.0"],
  "compatibility": {
    "multicord_version": ">=3.0.0"
  }
}
```

**Purpose**: Package metadata with dependencies and version constraints.

#### **Layer 3: Runtime Config** (`config.toml` / `.env`)
Located in bot instance (unchanged from v2.1.0):

```toml
[bot]
prefix = "!"
name = "MyBot"
```

**Purpose**: Bot-specific runtime configuration and secrets.

### Key Features

- **JSON Schema Validation**: Manifests validated against official schemas
- **npm-Style Versions**: `^1.0.0` (compatible), `~1.2.0` (patch), `>=1.0.0` (minimum)
- **Explicit Dependencies**: `requires_cogs` declares cog requirements with version constraints
- **Version Gating**: `compatibility.multicord_version` ensures template compatibility
- **Type Safety**: `type` field distinguishes "template", "cog", "collection"

### For Contributors

When creating templates or cogs for v3.0:

1. **Include `$schema` URL** for validation
2. **Set `type` field** ("template" or "cog")
3. **Specify `compatibility.multicord_version: ">=3.0.0"`**
4. **Use `requires_cogs`** (not `auto_install_cogs`) for dependencies
5. **Reference schemas**: See [CLAUDE.md](./Templates/CLAUDE.md) for detailed manifest examples

**Migration from v2.1.0**: Templates v3.0 replaces single `manifest.json` with per-item `template.json`/`cog.json` files + repository-level `multicord.json`.

---

## 🤝 Contributing

We welcome community contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details on:
- Creating new templates (v3.0 manifest requirements)
- Creating new cogs (v3.0 schema validation)
- Template and cog naming conventions
- Testing requirements with v3.0 manifests
- Pull request process

### Quick Start for Contributors

#### Contributing a New Template
1. Fork this repository
2. Create template directory with minimal scaffolding
3. Follow v2.1.0 architecture (scaffolding only)
4. Add entry to `manifest.json` with `auto_install_cogs` if needed
5. Test with MultiCord CLI
6. Submit pull request

#### Contributing a New Cog
1. Fork this repository
2. Create cog directory in `cogs/`
3. Include: `__init__.py`, `manifest.json`, `requirements.txt`, `README.md`
4. Add cog metadata to repository `manifest.json`
5. Test with multiple templates
6. Submit pull request

---

## 📋 Template Requirements (v2.1.0)

All templates must:
- ✅ Use Discord.py 2.0+
- ✅ Support Python 3.9+
- ✅ Use `.env` files for tokens (security)
- ✅ Auto-load cogs from `cogs/` directory
- ✅ Include structured logging
- ✅ Have graceful shutdown handling
- ✅ Be minimal scaffolding (~150-200 lines)
- ✅ Specify `auto_install_cogs` in manifest if needed
- ✅ Follow Discord.py best practices
- ✅ Be well-documented
- ✅ Not include bot tokens or secrets

## 📋 Cog Requirements

All cogs must:
- ✅ Use Discord.py 2.0+ cog architecture
- ✅ Include `manifest.json` with complete metadata
- ✅ Have `requirements.txt` (even if empty)
- ✅ Include comprehensive `README.md`
- ✅ Implement `async def setup(bot)` function
- ✅ Be standalone (work with any template)
- ✅ Handle errors gracefully
- ✅ Be well-documented with usage examples

---

## 🏷️ Categories

**Templates** are organized by use case:
- **General**: Basic bots, utility bots, starter templates
- **Moderation**: Community management, anti-spam, logging
- **Entertainment**: Music, games, fun commands
- **Utility**: Tools, automation, integration bots
- **Advanced**: Complex architectures, professional projects

**Cogs** are organized by functionality:
- **Administration**: Permissions, roles, security
- **Moderation**: Kick, ban, mute, warnings, auto-mod
- **Entertainment**: Music, games, interactive features
- **Utility**: Tools, automation, helpers
- **Community**: Leveling, economy, engagement

---

## 📚 Resources

- **[Discord.py Documentation](https://discordpy.readthedocs.io/)** - Official Discord.py docs
- **[Discord Developer Docs](https://discord.com/developers/docs)** - Discord API documentation
- **[MultiCord Documentation](https://docs.multicord.io)** - MultiCord CLI guides (coming soon)
- **[Discord.py Community](https://discord.gg/dpy)** - Discord.py support server

---

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/HollowTheSilver/MultiCord-Templates/issues)
- **Discussions**: [GitHub Discussions](https://github.com/HollowTheSilver/MultiCord-Templates/discussions)
- **Discord**: Join the MultiCord community server (coming soon)

---

## 📜 License

All templates and cogs in this repository are released under the MIT License. See [LICENSE](LICENSE) for details.

You are free to:
- Use templates for commercial projects
- Modify templates for your needs
- Distribute modified versions
- Include templates in your own projects

---

## 🌟 Version History

### v2.1.0 (Current)
- **Architecture**: Refactored to cog-based system
- **Templates**: Now minimal scaffolding (~160 lines)
- **Cogs**: Features extracted to reusable cogs
- **Auto-Installation**: Cogs automatically installed during bot creation
- **New Cogs**: moderation-tools, music-player

### v2.0.0
- **Security**: Token storage moved to `.env` files
- **Enhancement**: Auto-load cogs from `cogs/` directory
- **Enhancement**: Structured logging with file and console output
- **Enhancement**: Graceful shutdown handling

### v1.0.0
- Initial release with 4 templates

---

**Made with ❤️ by the MultiCord Team**

Star this repository if you find these templates useful!
