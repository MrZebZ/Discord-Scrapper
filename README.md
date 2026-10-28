<p align="center">
  <img src="assets/banner.svg" alt="Discord Member Exporter" width="100%">
</p>

<p align="center">
  <a href="https://github.com/OWNER/discord-member-exporter/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/OWNER/discord-member-exporter/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.9%2B-blue">
  <img alt="discord.py" src="https://img.shields.io/badge/discord.py-2.x-5865F2">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green"></a>
</p>

A small, dependable command-line tool that exports **member handles, display names, user IDs, roles and join dates** from a Discord server where **your own official bot** is installed. Output is a clean CSV plus an optional plain-text list of handles.

## Features

- Uses the official Discord Bot API through `discord.py`; no user-token tricks or scraping
- Exports to **CSV** (10 columns) and a **handles-only `.txt`** file
- Handles modern usernames (no discriminator) and legacy `name#1234` handles
- Filter by **role** (case-insensitive substring) and **exclude bots**
- Works for one server (`--guild-id`) or every server the bot is in
- Clear error messages and proper exit codes, ready for scripts and cron jobs
- Unit-tested, linted, CI on Python 3.9 to 3.13

## How it works

![Workflow](docs/images/workflow.svg)

## Quick start

```bash
git clone https://github.com/OWNER/discord-member-exporter.git
cd discord-member-exporter
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

### 1. Prepare your bot

Create the bot, enable **Server Members Intent**, and invite it to your server. Full walkthrough: **[docs/setup.md](docs/setup.md)**.

![Enable Server Members Intent](docs/images/intents.svg)

### 2. Run it

```bash
export DISCORD_BOT_TOKEN="your_bot_token_here"      # Windows PowerShell: $env:DISCORD_BOT_TOKEN="..."
discord-member-exporter --guild-id 123456789012345678 --output members.csv --handles-only handles.txt
```

![Terminal example](docs/images/terminal.svg)

You can also run it as a module: `python -m discord_member_exporter --help`.

## Options

| Option | Description | Default |
|---|---|---|
| `--token` | Bot token (prefer the `DISCORD_BOT_TOKEN` env var) | env var |
| `--guild-id` | Server ID to export; omit to export all servers the bot is in | all |
| `--output` | CSV output path | `discord_members.csv` |
| `--handles-only` | Text file with one unique handle per line | `discord_handles.txt` |
| `--exclude-bots` | Skip bot accounts | off |
| `--role` | Only members with a role containing this text | none |
| `--version` | Show version | |

### Examples

```bash
# Only moderators, humans only
discord-member-exporter --guild-id 123456789012345678 --role moderator --exclude-bots

# Every server your bot belongs to
discord-member-exporter --output all_servers.csv
```

## Output

![CSV preview](docs/images/csv-preview.svg)

| Column | Meaning |
|---|---|
| `server_id`, `server_name` | The server |
| `user_id` | Permanent numeric Discord user ID |
| `handle` | Username (`name` or legacy `name#1234`) |
| `global_name` | Account display name, if set |
| `server_display_name` | Nickname shown in this server |
| `is_bot` | Whether the account is a bot |
| `joined_at` | When the member joined the server (UTC) |
| `account_created_at` | When the account was created (UTC) |
| `roles` | Role names separated by `; ` |

A full sample lives in [`examples/sample_output.csv`](examples/sample_output.csv).

## Responsible use

Member lists are **personal data**. Please:

- Only export from servers you own or administer, with your bot properly invited.
- Follow the [Discord Developer Policy](https://discord.com/developers/docs/policies-and-agreements/developer-policy) and [Terms of Service](https://discord.com/terms).
- Comply with privacy laws that apply to you (for example GDPR) and tell your community what you collect and why.
- Do not use exports for spam, unsolicited messaging or harassment.
- Store exports securely and delete them when no longer needed. They are git-ignored by default.

## Troubleshooting

| Problem | Fix |
|---|---|
| `SERVER MEMBERS INTENT is not enabled` | Enable it in the Developer Portal, Bot tab. |
| `Login failed: the bot token is invalid` | Reset the token and use the new value. |
| `Could not access server ID` | Check the ID and that the bot is in the server. |
| Empty export | Your `--role` or `--exclude-bots` filters matched nobody. |

More in [docs/setup.md](docs/setup.md).

## Development

```bash
pip install -e ".[dev]"
make lint
make test
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) and [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE). This project is not affiliated with or endorsed by Discord Inc.
