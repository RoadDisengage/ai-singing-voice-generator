"""De-esser handler for sibilant-heavy vocal takes before conversion."""
from __future__ import annotations

import numpy as np

from src.utils.logging_setup import get_logger

log = get_logger(__name__)

HANDLER_NAME = "deesser"
_SIBILANT_BAND_HZ = (5000, 9000)


class _DeesserHandler:
    name = HANDLER_NAME

    def transform(self, audio: np.ndarray, ctx: dict) -> np.ndarray:
        sr = int(ctx.get("config").audio.sample_rate)
        n = len(audio)
        if n == 0:
            return audio
        spectrum = np.fft.rfft(audio)
        freqs = np.fft.rfftfreq(n, d=1.0 / sr)
        band = (freqs >= _SIBILANT_BAND_HZ[0]) & (freqs <= _SIBILANT_BAND_HZ[1])
        spectrum[band] *= 0.7
        return np.fft.irfft(spectrum, n=n)


def HANDLER() -> _DeesserHandler:
    return _DeesserHandler()