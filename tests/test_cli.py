from hardware_info_tool.cli import sections_for_command
from hardware_info_tool.formatters import format_json, format_text


def test_sections_for_summary_includes_core_sections():
    assert sections_for_command("summary") == ["system", "cpu", "memory", "disk", "network", "gpu"]


def test_sections_for_single_command():
    assert sections_for_command("cpu") == ["cpu"]


def test_format_json_contains_section_name():
    output = format_json({"cpu": {"brand": "Example CPU"}})
    assert '"cpu"' in output
    assert "Example CPU" in output


def test_format_text_renders_cpu_section():
    output = format_text({"cpu": {"brand": "Example CPU", "usage_percent": 12.5}})
    assert "CPU:" in output
    assert "Example CPU" in output
    assert "12.5%" in output
