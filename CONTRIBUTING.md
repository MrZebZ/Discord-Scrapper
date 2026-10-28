# Contributing

Thanks for your interest in improving Discord Member Exporter!

1. Fork the repo and create a branch: `git checkout -b feature/my-change`
2. Set up your environment:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -e ".[dev]"
   ```
3. Make your change and add tests under `tests/`.
4. Run `ruff check .` and `pytest`.
5. Open a pull request describing what and why.

Never include bot tokens or real member data in commits, issues, or screenshots.
