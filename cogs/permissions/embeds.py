"""
Embed Utilities for Permissions System
=======================================

Professional embed system for consistent, beautiful Discord embeds with smart
defaults, automatic truncation, and contextual styling.

Based on MultiCord's original embed utilities, modernized for the permissions cog.
"""

import discord
from datetime import datetime, timezone
from typing import Optional, Union
from enum import Enum


# ========================================( Enums & Constants )======================================== #


class EmbedType(Enum):
    """Predefined embed types with consistent styling (emoji, color)."""
    SUCCESS = ("✅", discord.Color.green())
    ERROR = ("❌", discord.Color.red())
    WARNING = ("⚠️", discord.Color.yellow())
    INFO = ("ℹ️", discord.Color.blue())
    LOADING = ("⏳", discord.Color.purple())
    SECURITY = ("🔒", discord.Color.dark_red())


# Discord embed limits (official API constraints)
EMBED_TITLE_LIMIT = 256
EMBED_DESCRIPTION_LIMIT = 4096
EMBED_FIELD_NAME_LIMIT = 256
EMBED_FIELD_VALUE_LIMIT = 1024
EMBED_FOOTER_LIMIT = 2048
EMBED_AUTHOR_LIMIT = 256


# ========================================( Utility Functions )======================================== #


def truncate_text(text: str, limit: int, suffix: str = "...") -> str:
    """
    Truncate text to fit within Discord embed limits.

    Args:
        text: Text to truncate
        limit: Character limit
        suffix: Suffix to add when truncating (default: "...")

    Returns:
        Truncated text with suffix if needed
    """
    if not text:
        return ""

    if len(text) <= limit:
        return text

    return text[:limit - len(suffix)] + suffix


# ========================================( Main Embed Builder )======================================== #


class EmbedBuilder:
    """
    Professional embed builder with smart defaults and automatic truncation.

    Provides fluent interface for creating Discord embeds with consistent styling.
    """

    def __init__(
            self,
            embed_type: Optional[EmbedType] = None,
            title: Optional[str] = None,
            description: Optional[str] = None,
            color: Optional[discord.Color] = None
    ) -> None:
        """
        Initialize embed builder.

        Args:
            embed_type: Predefined embed type for consistent styling
            title: Embed title
            description: Embed description
            color: Custom color (overrides embed_type color)
        """
        self.embed = discord.Embed()

        # Apply embed type styling
        if embed_type:
            icon, default_color = embed_type.value
            self.embed.color = color or default_color

            # Add icon to title if provided
            if title:
                self.embed.title = f"{icon} {truncate_text(title, EMBED_TITLE_LIMIT - 2)}"

        else:
            if title:
                self.embed.title = truncate_text(title, EMBED_TITLE_LIMIT)
            if color:
                self.embed.color = color

        if description:
            self.embed.description = truncate_text(description, EMBED_DESCRIPTION_LIMIT)

    def set_title(self, title: str, with_icon: bool = True) -> "EmbedBuilder":
        """
        Set embed title with optional icon preservation.

        Args:
            title: New title text
            with_icon: Preserve existing icon if present (default: True)

        Returns:
            Self for method chaining
        """
        if with_icon and self.embed.title and self.embed.title[0] in ("✅", "❌", "⚠️", "ℹ️", "⏳", "🔒"):
            # Preserve existing icon
            icon = self.embed.title.split(" ", 1)[0]
            self.embed.title = f"{icon} {truncate_text(title, EMBED_TITLE_LIMIT - 2)}"
        else:
            self.embed.title = truncate_text(title, EMBED_TITLE_LIMIT)
        return self

    def set_description(self, description: str) -> "EmbedBuilder":
        """
        Set embed description with automatic truncation.

        Args:
            description: Description text

        Returns:
            Self for method chaining
        """
        self.embed.description = truncate_text(description, EMBED_DESCRIPTION_LIMIT)
        return self

    def add_field(
            self,
            name: str,
            value: str,
            inline: bool = False
    ) -> "EmbedBuilder":
        """
        Add field with automatic truncation.

        Args:
            name: Field name
            value: Field value
            inline: Display inline (default: False)

        Returns:
            Self for method chaining
        """
        self.embed.add_field(
            name=truncate_text(name, EMBED_FIELD_NAME_LIMIT),
            value=truncate_text(value, EMBED_FIELD_VALUE_LIMIT),
            inline=inline
        )
        return self

    def set_footer(
            self,
            text: str,
            icon_url: Optional[str] = None,
            timestamp: bool = True
    ) -> "EmbedBuilder":
        """
        Set footer with optional timestamp.

        Args:
            text: Footer text
            icon_url: Footer icon URL (optional)
            timestamp: Add current timestamp (default: True)

        Returns:
            Self for method chaining
        """
        self.embed.set_footer(
            text=truncate_text(text, EMBED_FOOTER_LIMIT),
            icon_url=icon_url
        )
        if timestamp:
            self.embed.timestamp = datetime.now(timezone.utc)
        return self

    def set_author(
            self,
            name: str,
            icon_url: Optional[str] = None,
            url: Optional[str] = None
    ) -> "EmbedBuilder":
        """
        Set author information.

        Args:
            name: Author name
            icon_url: Author icon URL (optional)
            url: Author URL (optional)

        Returns:
            Self for method chaining
        """
        self.embed.set_author(
            name=truncate_text(name, EMBED_AUTHOR_LIMIT),
            icon_url=icon_url,
            url=url
        )
        return self

    def set_thumbnail(self, url: str) -> "EmbedBuilder":
        """
        Set thumbnail image.

        Args:
            url: Thumbnail image URL

        Returns:
            Self for method chaining
        """
        self.embed.set_thumbnail(url=url)
        return self

    def set_image(self, url: str) -> "EmbedBuilder":
        """
        Set main embed image.

        Args:
            url: Image URL

        Returns:
            Self for method chaining
        """
        self.embed.set_image(url=url)
        return self

    def build(self) -> discord.Embed:
        """
        Build and return the final Discord embed.

        Returns:
            Configured discord.Embed object
        """
        return self.embed


# ========================================( Quick Helper Functions )======================================== #


def create_success_embed(
        title: str = "Success",
        description: Optional[str] = None,
        user: Optional[Union[discord.User, discord.Member]] = None
) -> discord.Embed:
    """
    Create a success embed with green color and checkmark icon.

    Args:
        title: Embed title (default: "Success")
        description: Embed description (optional)
        user: User for footer attribution (optional)

    Returns:
        Configured success embed
    """
    builder = EmbedBuilder(EmbedType.SUCCESS, title, description)

    if user:
        builder.set_footer(
            f"Requested by {user.display_name}",
            icon_url=user.display_avatar.url if user.display_avatar else None
        )

    return builder.build()


def create_error_embed(
        title: str = "Error",
        description: Optional[str] = None,
        user: Optional[Union[discord.User, discord.Member]] = None
) -> discord.Embed:
    """
    Create an error embed with red color and X icon.

    Args:
        title: Embed title (default: "Error")
        description: Embed description (optional)
        user: User for footer attribution (optional)

    Returns:
        Configured error embed
    """
    builder = EmbedBuilder(EmbedType.ERROR, title, description)

    if user:
        builder.set_footer(
            f"Requested by {user.display_name}",
            icon_url=user.display_avatar.url if user.display_avatar else None
        )

    return builder.build()


def create_warning_embed(
        title: str = "Warning",
        description: Optional[str] = None,
        user: Optional[Union[discord.User, discord.Member]] = None
) -> discord.Embed:
    """
    Create a warning embed with yellow color and warning icon.

    Args:
        title: Embed title (default: "Warning")
        description: Embed description (optional)
        user: User for footer attribution (optional)

    Returns:
        Configured warning embed
    """
    builder = EmbedBuilder(EmbedType.WARNING, title, description)

    if user:
        builder.set_footer(
            f"Requested by {user.display_name}",
            icon_url=user.display_avatar.url if user.display_avatar else None
        )

    return builder.build()


def create_info_embed(
        title: str = "Information",
        description: Optional[str] = None,
        user: Optional[Union[discord.User, discord.Member]] = None
) -> discord.Embed:
    """
    Create an info embed with blue color and info icon.

    Args:
        title: Embed title (default: "Information")
        description: Embed description (optional)
        user: User for footer attribution (optional)

    Returns:
        Configured info embed
    """
    builder = EmbedBuilder(EmbedType.INFO, title, description)

    if user:
        builder.set_footer(
            f"Requested by {user.display_name}",
            icon_url=user.display_avatar.url if user.display_avatar else None
        )

    return builder.build()
