"""Typed config loading with deep-merge override support.

Config is validated by pydantic so a bad YAML fails fast at startup, not
mid-render. `load` merges an optional override file over the default.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class AppSection(BaseModel):
    name: str = "AI Singing Voice Generator"
    version: str = "0.6.2"
    device: str = "auto"
    max_workers: int = 4
    cache_dir: str = "temp/cache"


class AudioConfig(BaseModel):
    sample_rate: int = 40000
    hop_length: int = 320
    win_length: int = 1280
    f0_method: str = "rmvpe"
    f0_min: int = 50
    f0_max: int = 1100
    loudness_norm_lufs: float = -18.0


class ConversionConfig(BaseModel):
    model_id: str = "singer_female_alt_v3"
    index_ratio: float = Field(0.66, ge=0.0, le=1.0)
    filter_radius: int = 3
    resample_sr: int = 0
    rms_mix_rate: float = 0.25
    protect: float = Field(0.33, ge=0.0, le=0.5)
    transpose_semitones: int = 0


class VocoderConfig(BaseModel):
    backend: str = "diffusion"
    diffusion_steps: int = 32
    guidance_scale: float = 1.8
    seed: int = 6767


class TrainingConfig(BaseModel):
    epochs: int = 300
    batch_size: int = 8
    save_every: int = 50
    segment_seconds: float = 3.7
    pretrained_g: str = ""
    pretrained_d: str = ""


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: str = "logs/asvg.log"
    rich_tracebacks: bool = True


class AppConfig(BaseModel):
    app: AppSection = AppSection()
    audio: AudioConfig = AudioConfig()
    conversion: ConversionConfig = ConversionConfig()
    vocoder: VocoderConfig = VocoderConfig()
    training: TrainingConfig = TrainingConfig()
    logging: LoggingConfig = LoggingConfig()


class ConfigService:
    @staticmethod
    def load(path: Path, override: Path | None = None) -> AppConfig:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        if override is not None:
            raw = _deep_merge(raw, yaml.safe_load(Path(override).read_text(encoding="utf-8")) or {})
        return AppConfig.model_validate(raw)


def _deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for key, value in over.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out