"""Command-line interface."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional, Sequence

import discord

from . import __version__
from .exporter import MemberExporterClient


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="discord-member-exporter",
        description="Export Discord server member handles and metadata using an official Discord Bot.",
    )
    parser.add_argument(
        "--token",
        type=str,
        default=os.environ.get("DISCORD_BOT_TOKEN"),
        help="Discord Bot Token (defaults to DISCORD_BOT_TOKEN environment variable).",
    )
    parser.add_argument(
        "--guild-id",
        type=int,
        default=None,
        help="Target Discord Server (Guild) ID. If omitted, exports from all servers the bot is in.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="discord_members.csv",
        help="Output CSV file path (default: discord_members.csv).",
    )
    parser.add_argument(
        "--handles-only",
        type=str,
        default="discord_handles.txt",
        help="Plain-text file with one handle per line (default: discord_handles.txt).",
    )
    parser.add_argument(
        "--exclude-bots",
        action="store_true",
        help="Exclude bot accounts from the exported list.",
    )
    parser.add_argument(
        "--role",
        type=str,
        default=None,
        help="Only export members whose role name matches this substring (case-insensitive).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    if not args.token:
        print(
            "[!] Error: Bot token is required. Set DISCORD_BOT_TOKEN or pass --token.",
            file=sys.stderr,
        )
        sys.exit(1)

    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True  # Privileged intent required to list server members

    client = MemberExporterClient(
        guild_id=args.guild_id,
        output_csv=args.output,
        handles_file=args.handles_only,
        exclude_bots=args.exclude_bots,
        role_filter=args.role,
        intents=intents,
    )

    try:
        client.run(args.token)
    except discord.LoginFailure:
        print("[!] Login failed: the bot token is invalid.", file=sys.stderr)
        sys.exit(1)
    except discord.PrivilegedIntentsRequired:
        print(
            "[!] SERVER MEMBERS INTENT is not enabled. Turn it on in the Discord "
            "Developer Portal (Bot tab -> Privileged Gateway Intents).",
            file=sys.stderr,
        )
        sys.exit(1)

    sys.exit(0 if client.success else 1)
