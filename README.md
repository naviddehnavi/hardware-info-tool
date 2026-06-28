# Hardware Information Tool

A Python command-line tool that collects hardware and operating-system information with best-effort support across platforms. It can print human-readable text, emit JSON, and save either format to a file.

## Features

- Package-style Python CLI configured with `pyproject.toml`
- Collectors for:
  - system / operating system
  - CPU
  - memory and swap
  - disks and mounted partitions
  - network interfaces
  - GPU details (best effort via optional `GPUtil`)
  - sensors (best effort via `psutil` platform support)
- Output formats:
  - text
  - JSON
- Optional `--output` / `-o` flag to save the formatted report to a file

## Requirements

- Python 3.10 or newer
- Dependencies from `requirements.txt`

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

For editable CLI development:

```bash
python -m pip install -e .
```

## Usage

Run the default summary:

```bash
python main.py
```

Or use the package CLI module directly:

```bash
python -m hardware_info_tool.cli summary
```

After installing the package, the console script is available:

```bash
hardware-info summary
```

### Commands

```text
summary   system, CPU, memory, disk, network, and GPU
all       every collector, including sensors
system    system and OS details
os        alias-style OS details
cpu       CPU details
memory    memory and swap details
disk      mounted disk / partition usage
network   network interface addresses and state
gpu       best-effort GPU details
sensors   best-effort temperature, fan, and battery details
```

### Output formats

Text output is the default:

```bash
python main.py cpu
```

JSON output:

```bash
python main.py all --format json
```

Save output to a file:

```bash
python main.py summary --output hardware-summary.txt
python main.py all --format json --output hardware-report.json
```

## Windows launcher

On Windows, double-click `start.bat` to install dependencies and run the default summary.
