import argparse
import sys
import time
import psutil

try:
    import pynvml
    HAS_NVML = True
except ImportError:
    HAS_NVML = False

def classify_state(gpu_util: float, disk_read_mb: float) -> str:
    """Classifies GPU/Storage correlation state."""
    if gpu_util >= 70.0:
        return "HEALTHY_COMPUTE"
    elif gpu_util < 35.0 and disk_read_mb > 50.0:
        return "CRITICAL_IO_STARVATION"
    elif gpu_util < 35.0 and disk_read_mb > 15.0:
        return "WARN_IO_BOTTLENECK"
    elif gpu_util < 15.0 and disk_read_mb < 5.0:
        return "SYSTEM_IDLE"
    return "MIXED_WORKLOAD"

def monitor_system(interval: float = 1.0):
    print("⚡ ai-io-telemetry active (Press Ctrl+C to exit)")
    print(f"{'Timestamp':<20} | {'GPU Util (%)':<14} | {'VRAM Used (MB)':<16} | {'Disk Read (MB/s)':<18} | {'Status'}")
    print("-" * 92)

    handle = None
    if HAS_NVML:
        try:
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        except Exception:
            handle = None

    last_disk = psutil.disk_io_counters()
    last_time = time.time()

    try:
        while True:
            time.sleep(interval)
            now = time.time()
            elapsed = max(now - last_time, 1e-6)
            current_disk = psutil.disk_io_counters()

            read_bytes_sec = (current_disk.read_bytes - last_disk.read_bytes) / elapsed
            read_mb_s = read_bytes_sec / (1024 * 1024)

            last_disk = current_disk
            last_time = now

            ts = time.strftime("%Y-%m-%d %H:%M:%S")

            if handle:
                try:
                    gpu_util = float(pynvml.nvmlDeviceGetUtilizationRates(handle).gpu)
                    vram_mb = pynvml.nvmlDeviceGetMemoryInfo(handle).used // (1024 * 1024)
                except Exception:
                    gpu_util, vram_mb = 0.0, 0
            else:
                gpu_util, vram_mb = 0.0, 0

            status = classify_state(gpu_util, read_mb_s)
            print(f"{ts:<20} | {gpu_util:<14.1f} | {vram_mb:<16d} | {read_mb_s:<18.2f} | {status}")

    except KeyboardInterrupt:
        print("\n[+] Telemetry session ended.")

def main():
    parser = argparse.ArgumentParser(description="AI GPU & Storage I/O Profiler")
    subparsers = parser.add_subparsers(dest="command")

    monitor_parser = subparsers.add_parser("monitor", help="Start real-time monitoring")
    monitor_parser.add_argument("--interval", type=float, default=1.0, help="Sampling interval in seconds")

    args = parser.parse_args()
    if args.command == "monitor":
        monitor_system(args.interval)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()