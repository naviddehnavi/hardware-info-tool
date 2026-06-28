"""Best-effort hardware and operating-system collectors."""

from __future__ import annotations

import platform
import socket
from typing import Any, Callable

import psutil
from cpuinfo import get_cpu_info

CollectorResult = dict[str, Any]


def _safe_call(default: Any, func: Callable[[], Any]) -> Any:
    try:
        return func()
    except Exception:
        return default


def collect_system() -> CollectorResult:
    return {
        "hostname": platform.node() or "Unknown",
        "system": platform.system() or "Unknown",
        "release": platform.release() or "Unknown",
        "version": platform.version() or "Unknown",
        "machine": platform.machine() or "Unknown",
        "processor": platform.processor() or "Unknown",
        "python_version": platform.python_version(),
    }


def collect_os() -> CollectorResult:
    return collect_system()


def collect_cpu() -> CollectorResult:
    info = _safe_call({}, get_cpu_info)
    freq = _safe_call(None, psutil.cpu_freq)
    return {
        "brand": info.get("brand_raw") or platform.processor() or "Unknown",
        "architecture": info.get("arch") or platform.machine() or "Unknown",
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "usage_percent": _safe_call(None, lambda: psutil.cpu_percent(interval=0.2)),
        "frequency_mhz": getattr(freq, "current", None),
    }


def collect_memory() -> CollectorResult:
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total": vm.total,
        "available": vm.available,
        "used": vm.used,
        "percent_used": vm.percent,
        "swap_total": swap.total,
        "swap_used": swap.used,
        "swap_percent_used": swap.percent,
    }


def collect_disk() -> CollectorResult:
    disks: list[CollectorResult] = []
    for partition in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except (PermissionError, OSError):
            continue
        disks.append(
            {
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "filesystem": partition.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent_used": usage.percent,
            }
        )
    return {"partitions": disks}


def collect_network() -> CollectorResult:
    interfaces: list[CollectorResult] = []
    stats = psutil.net_if_stats()
    for name, addresses in psutil.net_if_addrs().items():
        interface_addresses: list[CollectorResult] = []
        for address in addresses:
            family = getattr(address.family, "name", str(address.family))
            interface_addresses.append(
                {
                    "family": family,
                    "address": address.address,
                    "netmask": address.netmask,
                    "broadcast": address.broadcast,
                }
            )
        stat = stats.get(name)
        interfaces.append(
            {
                "name": name,
                "is_up": getattr(stat, "isup", None),
                "speed_mbps": getattr(stat, "speed", None),
                "addresses": interface_addresses,
            }
        )
    return {"interfaces": interfaces}


def collect_gpu() -> CollectorResult:
    try:
        import GPUtil
    except ImportError:
        return {"available": False, "message": "GPUtil is not installed", "gpus": []}

    try:
        gpus = GPUtil.getGPUs()
    except Exception as exc:
        return {"available": False, "message": f"Unable to retrieve GPU info: {exc}", "gpus": []}

    return {
        "available": bool(gpus),
        "message": "OK" if gpus else "No GPU detected",
        "gpus": [
            {
                "id": gpu.id,
                "name": gpu.name,
                "load_percent": round(gpu.load * 100, 2),
                "memory_total_mb": gpu.memoryTotal,
                "memory_used_mb": gpu.memoryUsed,
                "memory_free_mb": gpu.memoryFree,
                "temperature_c": gpu.temperature,
            }
            for gpu in gpus
        ],
    }


def collect_sensors() -> CollectorResult:
    sensors: CollectorResult = {}
    if hasattr(psutil, "sensors_temperatures"):
        sensors["temperatures"] = _safe_call({}, psutil.sensors_temperatures)
    if hasattr(psutil, "sensors_fans"):
        sensors["fans"] = _safe_call({}, psutil.sensors_fans)
    if hasattr(psutil, "sensors_battery"):
        battery = _safe_call(None, psutil.sensors_battery)
        sensors["battery"] = battery._asdict() if battery else None
    return sensors or {"message": "Sensors are not supported on this platform"}


COLLECTORS: dict[str, Callable[[], CollectorResult]] = {
    "system": collect_system,
    "os": collect_os,
    "cpu": collect_cpu,
    "memory": collect_memory,
    "disk": collect_disk,
    "network": collect_network,
    "gpu": collect_gpu,
    "sensors": collect_sensors,
}

SUMMARY_SECTIONS = ["system", "cpu", "memory", "disk", "network", "gpu"]
ALL_SECTIONS = ["system", "cpu", "memory", "disk", "network", "gpu", "sensors"]
