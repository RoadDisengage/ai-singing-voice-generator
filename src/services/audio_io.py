"""Audio read/write with loudness normalization.

Uses soundfile for PCM I/O and librosa for resampling. All internal arrays
are float32 mono at the configured sample rate.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

from src.utils.logging_setup import get_logger

log = get_logger(__name__)


class AudioIO:
    def __init__(self, sample_rate: int = 40000) -> None:
        self.sample_rate = sample_rate

    def read(self, path: Path) -> np.ndarray:
        data, sr = sf.read(str(path), always_2d=False, dtype="float32")
        if data.ndim > 1:
            data = data.mean(axis=1)
        if sr != self.sample_rate:
            import librosa

            data = librosa.resample(data, orig_sr=sr, target_sr=self.sample_rate)
        return np.ascontiguousarray(data, dtype=np.float32)

    def write(self, path: Path, audio: np.ndarray) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(path), np.clip(audio, -1.0, 1.0), self.sample_rate)

    def duration(self, audio: np.ndarray) -> float:
        return len(audio) / float(self.sample_rate)