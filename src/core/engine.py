"""Top-level conversion engine.

`SingingVoiceEngine` wires the pipeline stages together:
    load -> analyze -> convert -> vocode -> write

It holds no UI concerns and is safe to construct in tests with a stub
device. Concurrency: one engine instance is single-threaded; batch runs
should create one engine per worker process.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from src.core.pipeline import ConversionPipeline
from src.handlers.handler_registry import HandlerRegistry
from src.models.voice_model import VoiceModel
from src.services.audio_io import AudioIO
from src.services.config_service import AppConfig
from src.services.model_store import ModelStore
from src.utils.logging_setup import get_logger

log = get_logger(__name__)


@dataclass(slots=True)
class ConversionResult:
    output_path: Path
    duration_s: float
    realtime_factor: float
    model_id: str


class SingingVoiceEngine:
    """Owns the model store, handler registry, and pipeline for a session."""

    def __init__(self, config: AppConfig, device: str, load_plugins: bool = True) -> None:
        self.config = config
        self.device = device
        self.store = ModelStore(config.app.cache_dir)
        self.audio = AudioIO(sample_rate=config.audio.sample_rate)
        self.registry = HandlerRegistry.discover(load_plugins=load_plugins)
        self.pipeline = ConversionPipeline(config=config, store=self.store, device=device)

    def convert(self, input_path: Path, model_id: str, output_path: Path) -> ConversionResult:
        model: VoiceModel = self.store.load(model_id, device=self.device)
        log.info("Loaded voice model %s (%s)", model_id, model.arch)

        started = time.perf_counter()
        waveform = self.audio.read(input_path)
        rendered = self.pipeline.run(waveform, model, handlers=self.registry.active())
        self.audio.write(output_path, rendered)

        elapsed = time.perf_counter() - started
        duration = self.audio.duration(rendered)
        return ConversionResult(
            output_path=output_path,
            duration_s=duration,
            realtime_factor=(duration / elapsed) if elapsed > 0 else 0.0,
            model_id=model_id,
        )