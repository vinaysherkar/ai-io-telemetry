# ⚡ ai-io-telemetry

> **Zero-overhead eBPF and NVML profiler to detect GPU starvation and distributed storage I/O bottlenecks during distributed LLM training.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Linux: Kernel 5.15+](https://img.shields.io/badge/linux-kernel%205.15+-orange.svg)](https://www.kernel.org/)

---

## The Problem

In large-scale AI training, high-end accelerators (H100/A100) often sit idle for 20–40% of compute cycles waiting on dataset batch ingestion, checkpoint flushes, or network-attached NVMe storage. Standard tools like `nvidia-smi` or `iostat` operate in isolation—they don't correlate **GPU SM idle spikes** with **kernel page-cache misses or storage fabric stalls**.

`ai-io-telemetry` binds eBPF kernel probes directly to GPU telemetry in real time to pinpoint whether your bottleneck is PyTorch dataloader worker contention, network fabric latency, or slow backend block storage.

---

## Features

- **Kernel-Level I/O Observability:** Uses eBPF (`libbpf`) to trace `vfs_read`, `vfs_write`, and NVMe block completion queues with < 0.8% CPU overhead.
- **Hardware-Correlated Metrics:** Correlates GPU SM Active % directly against I/O wait times and TCP/RDMA socket stalls.
- **Terminal UI & Exporters:** Native interactive terminal dashboard via `Textual` and Prometheus/Grafana exporter endpoints.
- **Framework Agnostic:** Profiles PyTorch, Megatron-LM, vLLM, and standalone synthetic FIO workloads.

---

## Quickstart

### 1. Installation

```bash
git clone https://github.com/vinaysherkar/ai-io-telemetry.git
cd ai-io-telemetry
pip install .
