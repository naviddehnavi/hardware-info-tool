import platform
import socket

import psutil
from cpuinfo import get_cpu_info

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

    print("CPU:")
    print(f"  Name: {name}")
    print(f"  Cores: {physical} physical / {logical} logical")
    print(f"  Usage: {usage}%")


def print_ram_info():
    vm = psutil.virtual_memory()
    print("RAM:")
    print(f"  Total: {bytes_to_gb(vm.total)}")
    print(f"  Available: {bytes_to_gb(vm.available)}")
    print(f"  Used: {bytes_to_gb(vm.used)}")
    print(f"  Percent Used: {vm.percent}%")


def print_gpu_info():
    print("GPU:")
    if GPUtil is None:
        print("  GPUtil not installed or GPU not accessible")
        return
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            print("  No GPU detected")
        for gpu in gpus:
            print(f"  Name: {gpu.name}")
            print(f"    Memory Total: {gpu.memoryTotal} MB")
            print(f"    Memory Used: {gpu.memoryUsed} MB")
    except Exception as exc:
        print(f"  Unable to retrieve GPU info: {exc}")


def print_disk_info():
    print("Disk:")
    try:
        c_usage = psutil.disk_usage('C:\\')
        print("  Drive C:\\:")
        print(f"    Total: {bytes_to_gb(c_usage.total)}")
        print(f"    Used: {bytes_to_gb(c_usage.used)}")
        print(f"    Free: {bytes_to_gb(c_usage.free)}")
        print(f"    Percent Used: {c_usage.percent}%")
    except Exception as exc:
        print(f"  Unable to read C drive info: {exc}")

    partitions = psutil.disk_partitions()
    for part in partitions:
        if part.mountpoint.lower().startswith('c:'):
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            print(f"  Drive {part.mountpoint}:")
            print(f"    Total: {bytes_to_gb(usage.total)}")
            print(f"    Used: {bytes_to_gb(usage.used)}")
            print(f"    Free: {bytes_to_gb(usage.free)}")
            print(f"    Percent Used: {usage.percent}%")
        except Exception:
            pass


def print_motherboard_info():
    print("Motherboard:")
    if wmi is None:
        print("  WMI module not installed or not running on Windows")
        return
    try:
        c = wmi.WMI()
        for board in c.Win32_BaseBoard():
            print(f"  Manufacturer: {board.Manufacturer}")
            print(f"  Product: {board.Product}")
            break
    except Exception as exc:
        print(f"  Unable to retrieve motherboard info: {exc}")


def print_os_info():
    print("OS:")
    print(f"  System: {platform.system()} {platform.release()}")
    print(f"  Version: {platform.version()}")
    print(f"  Architecture: {platform.machine()}")
    print(f"  Hostname: {platform.node()}")


def print_network_info():
    print("Network Interfaces:")
    addrs = psutil.net_if_addrs()
    for name, addr_list in addrs.items():
        for addr in addr_list:
            if addr.family == socket.AF_INET:
                print(f"  {name}: {addr.address}")


def main():
    print_cpu_info()
    print()
    print_ram_info()
    print()
    print_gpu_info()
    print()
    print_disk_info()
    print()
    print_motherboard_info()
    print()
    print_os_info()
    print()
    print_network_info()


if __name__ == "__main__":
    main()
