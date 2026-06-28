"""Backward-compatible entry point for running the hardware information CLI."""

from hardware_info_tool.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
