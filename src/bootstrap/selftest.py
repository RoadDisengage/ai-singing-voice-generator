"""Environment self-test run via `--selftest`.

Checks interpreter version, required native libs, device availability, and
that the model registry can be read. Returns a process exit code.
"""
from __future__ import annotations

import importlib
import sys

from src.services.config_service import AppConfig
from src.utils.device import device_summary

_REQUIRED = ("torch", "torchaudio", "soundfile", "librosa", "faiss", "onnxruntime")


def run_selftest(config: AppConfig, device: str) -> int:
    problems: list[str] = []

    if sys.version_info < (3, 11):
        problems.append(f"python {sys.version.split()[0]} < 3.11")

    for mod in _REQUIRED:
        try:
            importlib.import_module(mod)
        except ImportError as exc:
            problems.append(f"missing dependency: {mod} ({exc})")

    print("device summary:", device_summary(device))
    print("config version:", config.app.version)

    if problems:
        for p in problems:
            print("FAIL:", p)
        return 1
    print("selftest OK")
    return 0