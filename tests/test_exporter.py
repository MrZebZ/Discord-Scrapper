from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from discord_member_exporter.cli import parse_args
from discord_member_exporter.exporter import (
    CSV_FIELDNAMES,
    extract_role_names,
    format_handle,
    format_timestamp,
    matches_role_filter,
    member_to_row,
    write_csv,
    write_handles,
)


def make_member(**overrides):
    base = dict(
        id=111,
        name="alice",
        discriminator="0",
        global_name="Alice A.",
        display_name="Alice",
        bot=False,
        joined_at=datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
        created_at=datetime(2020, 5, 6, 7, 8, 9, tzinfo=timezone.utc),
        roles=[SimpleNamespace(name="@everyone"), SimpleNamespace(name="Moderator")],
    )
    base.update(overrides)
    return SimpleNamespace(**base)


GUILD = SimpleNamespace(id=999, name="Test Server")


def test_format_handle_modern_and_legacy():
    assert format_handle("alice", "0") == "alice"
    assert format_handle("alice", None) == "alice"
    assert format_handle("alice", "1234") == "alice#1234"


def test_format_timestamp_converts_to_utc():
    tz = timezone(timedelta(hours=5))
    dt = datetime(2024, 1, 1, 5, 0, 0, tzinfo=tz)
    assert format_timestamp(dt) == "2024-01-01 00:00:00 UTC"
    assert format_timestamp(None) == ""


def test_extract_role_names_skips_everyone():
    assert extract_role_names(make_member()) == ["Moderator"]


def test_role_filter():
    assert matches_role_filter(["Moderator"], None)
    assert matches_role_filter(["Moderator"], "mod")
    assert not matches_role_filter(["Member"], "mod")
    assert not matches_role_filter([], "mod")


def test_member_to_row_has_all_columns():
    member = make_member()
    row = member_to_row(GUILD, member, extract_role_names(member))
    assert list(row) == CSV_FIELDNAMES
    assert row["handle"] == "alice"
    assert row["server_id"] == "999"
    assert row["roles"] == "Moderator"
    assert row["joined_at"] == "2024-01-02 03:04:05 UTC"


def test_write_outputs(tmp_path):
    member = make_member()
    row = member_to_row(GUILD, member, ["Moderator"])
    csv_path = tmp_path / "out.csv"
    txt_path = tmp_path / "handles.txt"
    write_csv([row], str(csv_path))
    count = write_handles(["a", "b", "a"], str(txt_path))
    assert csv_path.read_text(encoding="utf-8").startswith(",".join(CSV_FIELDNAMES))
    assert count == 2
    assert txt_path.read_text(encoding="utf-8") == "a\nb\n"


def test_parse_args_defaults(monkeypatch):
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    args = parse_args([])
    assert args.output == "discord_members.csv"
    assert args.exclude_bots is False
    assert args.token is None
