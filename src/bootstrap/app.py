"""Application entry point for the AI Singing Voice Generator desktop tool.

Run as module:
    python -m src.bootstrap.app --input clip.wav --model singer_female_alt_v3

This module owns process-level concerns only: argument parsing, config
loading, device selection, and dispatch into the core engine. All business
logic lives under src/core and below.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.core.engine import SingingVoiceEngine
from src.services.config_service import ConfigService
from src.utils.device import resolve_device
from src.utils.logging_setup import configure_logging


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="asvg",
        description="AI Singing Voice Generator — convert a vocal clip into a target AI singing voice.",
    )
    parser.add_argument("--input", type=Path, help="Source audio file to convert.")
    parser.add_argument("--model", type=str, help="Target voice model id.")
    parser.add_argument("--output", type=Path, default=Path("output/render.wav"))
    parser.add_argument("--config", type=Path, default=Path("configs/default.yaml"))
    parser.add_argument("--device", choices=["auto", "cuda", "cpu"], default="auto")
    parser.add_argument("--selftest", action="store_true", help="Run environment checks and exit.")
    parser.add_argument("--no-plugins", action="store_true", help="Disable third-party handlers.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    config = ConfigService.load(args.config)
    configure_logging(config.logging)
    logger = logging.getLogger("asvg.bootstrap")

    device = resolve_device(args.device)
    logger.info("Resolved compute device: %s", device)

    if args.selftest:
        from src.bootstrap.selftest import run_selftest

        return run_selftest(config, device)

    if not args.input or not args.model:
        logger.error("--input and --model are required for a conversion run.")
        return 2

    engine = SingingVoiceEngine(config=config, device=device, load_plugins=not args.no_plugins)
    result = engine.convert(args.input, model_id=args.model, output_path=args.output)
    logger.info("Wrote %s (%.2fs audio, %.1fx realtime)",
                result.output_path, result.duration_s, result.realtime_factor)
    return 0


if __name__ == "__main__":
    sys.exit(main())