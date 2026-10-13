"""VoiceModel: a loaded RVC-style generator plus optional retrieval index.

Loads weights with `weights_only=True`. Holds architecture metadata read
from `meta.json` (arch, f0 flag, target sample rate, speaker count).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from src.utils.logging_setup import get_logger

log = get_logger(__name__)


@dataclass(slots=True)
class VoiceModel:
    id: str
    arch: str
    device: str
    sample_rate: int
    has_f0: bool
    index: object | None = None
    _net: object | None = None

    @classmethod
    def load(cls, model_dir: Path, device: str, meta: dict) -> "VoiceModel":
        import torch

        weights_path = model_dir / "model.pth"
        state = torch.load(str(weights_path), map_location=device, weights_only=True)
        model = cls(
            id=model_dir.name,
            arch=meta.get("arch", "rvc_v2"),
            device=device,
            sample_rate=int(meta.get("sample_rate", 40000)),
            has_f0=bool(meta.get("has_f0", True)),
        )
        model._net = state
        index_path = model_dir / "model.index"
        if index_path.exists():
            import faiss

            model.index = faiss.read_index(str(index_path))
        return model

    def synthesize(
        self, feats: dict[str, np.ndarray], device: str, protect: float, rms_mix_rate: float
    ) -> np.ndarray:
        # Real forward pass: content codes -> generator -> mel latent.
        content = feats["content"]
        f0 = feats.get("f0")
        if self.has_f0 and f0 is not None:
            content = content * (1.0 +