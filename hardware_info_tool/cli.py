"""Command-line interface for the hardware information tool."""

from __future__ import annotations

import argparse
from pathlib import Path

from .collectors import ALL_SECTIONS, COLLECTORS, SUMMARY_SECTIONS
from .formatters import format_output


def collect_sections(sections: list[str]) -> dict[str, object]:
    return {section: COLLECTORS[section]() for section in sections}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect hardware and system information.")
    parser.add_argument(
        "command",
        nargs="?",
        default="summary",
        choices=["summary", "all", *COLLECTORS.keys()],
        help="Information to collect (default: summary).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Optional path where the formatted output should be saved.",
    )
    return parser


def sections_for_command(command: str) -> list[str]:
    if command == "summary":
        return SUMMARY_SECTIONS
    if command == "all":
        return ALL_SECTIONS
    return [command]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    data = collect_sections(sections_for_command(args.command))
    output = format_output(data, args.format)
    print(output, end="")
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
