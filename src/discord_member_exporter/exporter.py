"""Core export logic: formatting helpers, file writers and the Discord client."""

from __future__ import annotations

import csv
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

import discord

CSV_FIELDNAMES: List[str] = [
    "server_id",
    "server_name",
    "user_id",
    "handle",
    "global_name",
    "server_display_name",
    "is_bot",
    "joined_at",
    "account_created_at",
    "roles",
]

_TS_FORMAT = "%Y-%m-%d %H:%M:%S UTC"


def format_handle(name: str, discriminator: Optional[str]) -> str:
    """Return a user handle.

    Modern Discord accounts have no discriminator (reported as ``"0"``), while
    legacy accounts and some bots still use the ``name#1234`` form.
    """
    if discriminator and discriminator != "0":
        return f"{name}#{discriminator}"
    return name


def format_timestamp(value: Optional[datetime]) -> str:
    """Format a datetime as UTC text, or return an empty string for ``None``."""
    if value is None:
        return ""
    return value.astimezone(timezone.utc).strftime(_TS_FORMAT)


def extract_role_names(member: Any) -> List[str]:
    """Return a member's role names, excluding ``@everyone``."""
    return [r.name for r in member.roles if r.name != "@everyone"]


def matches_role_filter(role_names: Iterable[str], role_filter: Optional[str]) -> bool:
    """Case-insensitive substring match against any role. No filter matches all."""
    if not role_filter:
        return True
    needle = role_filter.lower()
    return any(needle in name.lower() for name in role_names)


def member_to_row(guild: Any, member: Any, role_names: List[str]) -> Dict[str, Any]:
    """Convert a guild member into a CSV row."""
    return {
        "server_id": str(guild.id),
        "server_name": guild.name,
        "user_id": str(member.id),
        "handle": format_handle(member.name, member.discriminator),
        "global_name": member.global_name or "",
        "server_display_name": member.display_name,
        "is_bot": member.bot,
        "joined_at": format_timestamp(member.joined_at),
        "account_created_at": format_timestamp(member.created_at),
        "roles": "; ".join(role_names),
    }


def write_csv(rows: List[Dict[str, Any]], path: str) -> None:
    with open(path, mode="w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_handles(handles: Iterable[str], path: str) -> int:
    """Write unique handles (order preserved), one per line. Returns the count."""
    unique = list(dict.fromkeys(handles))
    with open(path, mode="w", encoding="utf-8") as fh:
        for handle in unique:
            fh.write(f"{handle}\n")
    return len(unique)


class MemberExporterClient(discord.Client):
    """Connects, exports guild member handles, and closes cleanly."""

    def __init__(
        self,
        guild_id: Optional[int],
        output_csv: str,
        handles_file: Optional[str],
        exclude_bots: bool,
        role_filter: Optional[str],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.target_guild_id = guild_id
        self.output_csv = output_csv
        self.handles_file = handles_file
        self.exclude_bots = exclude_bots
        self.role_filter = role_filter
        self.success = False

    async def on_ready(self) -> None:
        print(f"[*] Authenticated as bot: {self.user} (ID: {self.user.id})")
        try:
            await self.export_members()
        except Exception as exc:  # noqa: BLE001 - report and shut down cleanly
            print(f"[!] Error during export: {exc}", file=sys.stderr)
        finally:
            await self.close()

    async def export_members(self) -> None:
        if self.target_guild_id:
            guild = self.get_guild(self.target_guild_id)
            if guild is None:
                try:
                    guild = await self.fetch_guild(self.target_guild_id)
                except discord.DiscordException as exc:
                    print(
                        f"[!] Could not access server ID {self.target_guild_id}. "
                        f"Ensure the bot is invited to that server. Details: {exc}",
                        file=sys.stderr,
                    )
                    return
            target_guilds = [guild]
        else:
            target_guilds = list(self.guilds)
            if not target_guilds:
                print("[!] The bot is not currently a member of any servers.", file=sys.stderr)
                return

        rows: List[Dict[str, Any]] = []
        handles: List[str] = []

        for guild in target_guilds:
            print(f"[*] Fetching members for server: {guild.name} (ID: {guild.id})...")
            members: List[discord.Member] = []
            try:
                async for member in guild.fetch_members(limit=None):
                    members.append(member)
            except discord.Forbidden:
                print(
                    f"[!] Missing permission or 'Server Members Intent' for {guild.name}. "
                    "Make sure SERVER MEMBERS INTENT is enabled in the Discord Developer Portal.",
                    file=sys.stderr,
                )
                continue
            except discord.HTTPException as exc:
                print(f"[!] HTTP error fetching members from {guild.name}: {exc}", file=sys.stderr)
                continue

            for member in members:
                if self.exclude_bots and member.bot:
                    continue
                role_names = extract_role_names(member)
                if not matches_role_filter(role_names, self.role_filter):
                    continue
                row = member_to_row(guild, member, role_names)
                rows.append(row)
                handles.append(row["handle"])

        if not rows:
            print("[!] No matching members found to export.")
            return

        write_csv(rows, self.output_csv)
        print(f"[+] Exported {len(rows)} member records to '{self.output_csv}'.")

        if self.handles_file:
            count = write_handles(handles, self.handles_file)
            print(f"[+] Saved {count} unique handles to '{self.handles_file}'.")

        self.success = True
