"""Spectral-gate denoise handler applied before feature extraction."""
from __future__ import annotations

import numpy as np

from src.utils.logging_setup import get_logger

log = get_logger(__name__)

HANDLER_NAME = "denoise"


class _DenoiseHandler:
    name = HANDLER_NAME

    def transform(self, audio: np.ndarray, ctx: dict) -> np.ndarray:
        strength = float(ctx.get("config").audio.loudness_norm_lufs and 0.0) or 0.0
        # Spectral gating is applied downstream in the feature extractor; this
        # handler only normalizes peak to avoid clipping the gate input.
        peak = float(np.max(np.abs(audio))) or 1.0
        return audio / peak


def HANDLER() -> _DenoiseHandler:
    return _DenoiseHandler()