"""Output formatters for collected hardware information."""

from __future__ import annotations

import json
from typing import Any

from .utils import bytes_to_gib, percent


def _line_items(title: str, values: dict[str, Any]) -> list[str]:
    lines = [f"{title}:"]
    for key, value in values.items():
        label = key.replace("_", " ").title()
        lines.append(f"  {label}: {value}")
    return lines


def format_text(data: dict[str, Any]) -> str:
    sections: list[str] = []
    if "system" in data:
        sections.extend(_line_items("System", data["system"]))
        sections.append("")
    if "cpu" in data:
        cpu = dict(data["cpu"])
        if cpu.get("usage_percent") is not None:
            cpu["usage_percent"] = percent(cpu["usage_percent"])
        sections.extend(_line_items("CPU", cpu))
        sections.append("")
    if "memory" in data:
        memory = dict(data["memory"])
        for key in ("total", "available", "used", "swap_total", "swap_used"):
            memory[key] = bytes_to_gib(memory.get(key))
        memory["percent_used"] = percent(memory.get("percent_used"))
        memory["swap_percent_used"] = percent(memory.get("swap_percent_used"))
        sections.extend(_line_items("Memory", memory))
        sections.append("")
    if "disk" in data:
        sections.append("Disk:")
        for partition in data["disk"].get("partitions", []):
            sections.append(f"  {partition['mountpoint']} ({partition['device'] or 'device unknown'}):")
            sections.append(f"    Filesystem: {partition.get('filesystem') or 'Unknown'}")
            sections.append(f"    Total: {bytes_to_gib(partition.get('total'))}")
            sections.append(f"    Used: {bytes_to_gib(partition.get('used'))}")
            sections.append(f"    Free: {bytes_to_gib(partition.get('free'))}")
            sections.append(f"    Percent Used: {percent(partition.get('percent_used'))}")
        if not data["disk"].get("partitions"):
            sections.append("  No readable partitions found")
        sections.append("")
    if "network" in data:
        sections.append("Network:")
        for interface in data["network"].get("interfaces", []):
            state = "up" if interface.get("is_up") else "down"
            sections.append(f"  {interface['name']} ({state}, {interface.get('speed_mbps')} Mbps):")
            for address in interface.get("addresses", []):
                sections.append(f"    {address.get('family')}: {address.get('address')}")
        sections.append("")
    if "gpu" in data:
        sections.append("GPU:")
        gpu_data = data["gpu"]
        if gpu_data.get("gpus"):
            for gpu in gpu_data["gpus"]:
                sections.append(f"  {gpu.get('name', 'Unknown')}:")
                sections.append(f"    Load: {percent(gpu.get('load_percent'))}")
                sections.append(f"    Memory: {gpu.get('memory_used_mb')} / {gpu.get('memory_total_mb')} MB")
                sections.append(f"    Temperature: {gpu.get('temperature_c')} C")
        else:
            sections.append(f"  {gpu_data.get('message', 'No GPU data available')}")
        sections.append("")
    if "sensors" in data:
        sections.append("Sensors:")
        sensors = data["sensors"]
        if "message" in sensors:
            sections.append(f"  {sensors['message']}")
        else:
            sections.append(json.dumps(sensors, indent=2, default=str))
    return "\n".join(sections).rstrip() + "\n"


def format_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, default=str) + "\n"


def format_output(data: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return format_json(data)
    return format_text(data)
