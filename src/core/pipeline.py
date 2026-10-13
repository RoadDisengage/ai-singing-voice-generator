"""Conversion pipeline: feature extraction -> retrieval -> conversion -> vocode.

Each stage is a pure-ish transform over arrays plus a model handle. The
pipeline is deliberately linear and inspectable; branching logic lives in
handlers, not here.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

import numpy as np

from src.core.stages import (
    extract_features,
    pitch_shift,
    retrieval_blend,
    run_conversion,
    vocode,
)
from src.models.voice_model import VoiceModel
from src.services.config_service import AppConfig
from src.utils.logging_setup import get_logger

log = get_logger(__name__)


class StageHandler(Protocol):
    name: str

    def transform(self, audio: np.ndarray, ctx: dict) -> np.ndarray: ...


class ConversionPipeline:
    def __init__(self, config: AppConfig, store, device: str) -> None:
        self.config = config
        self.store = store
        self.device = device

    def run(
        self,
        waveform: np.ndarray,
        model: VoiceModel,
        handlers: Sequence[StageHandler] = (),
    ) -> np.ndarray:
        ctx: dict = {"config": self.config, "device": self.device, "model_id": model.id}

        for handler in handlers:
            log.debug("handler: %s", handler.name)
            waveform = handler.transform(waveform, ctx)

        feats = extract_features(waveform, self.config.audio)
        if model.index is not None:
            feats = retrieval_blend(feats, model.index, self.config.conversion.index_ratio)
        feats = pitch_shift(feats, self.config.conversion.transpose_semitones)

        converted = run_conversion(feats, model, self.device, self.config.conversion)
        return vocode(converted, self.config.vocoder, self.device)