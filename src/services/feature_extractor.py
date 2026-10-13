"""Content + pitch feature extraction feeding the converter.

Produces a dict with keys:
    content : (T, D) float32  — HuBERT-style content codes
    f0      : (T,)   float32  — fundamental frequency track
    energy  : (T,)   float32  — frame RMS
"""
from __future__ import annotations

import numpy as np

from src.services.config_service import AudioConfig
from src.utils.logging_setup import get_logger

log = get_logger(__name__)


class FeatureExtractor:
    def __init__(self, cfg: AudioConfig) -> None:
        self.cfg = cfg

    def run(self, waveform: np.ndarray) -> dict[str, np.ndarray]:
        f0 = self._extract_f0(waveform)
        energy = self._frame_rms(waveform)
        content = self._content_codes(waveform)
        return {"content": content, "f0": f0, "energy": energy}

    def _extract_f0(self, waveform: np.ndarray) -> np.ndarray:
        import pyworld

        f0, _ = pyworld.harvest(
            waveform.astype(np.float64),
            self.cfg.sample_rate,
            f0_floor=self.cfg.f0_min,
            f0_ceil=self.cfg.f0_max,
        )
        return f0.astype(np.float32)

    def _frame_rms(self, waveform: np.ndarray) -> np.ndarray:
        hop = self.cfg.hop_length
        frames = np.lib.stride_tricks.sliding_window_view(waveform, self.cfg.win_length)[::hop]
        return np.sqrt(np.mean(frames**2, axis=1)).astype(np.float32)

    def _content_codes(self, waveform: np.ndarray) -> np.ndarray:
        # Placeholder for the HuBERT encoder forward pass; the real encoder is
        # loaded lazily by the converter to keep this module import-light.
        frames = len(waveform) // self.cfg.hop_length
        return np.zeros((frames, 256), dtype=np.float32)