"""Local model store: resolves voice model ids to checkpoints on disk.

Layout:
    temp/cache/<model_id>/model.pth
    temp/cache/<model_id>/model.index
    temp/cache/<model_id>/meta.json
"""
from __future__ import annotations

import json
from pathlib import Path

from src.models.voice_model import VoiceModel
from src.utils.logging_setup import get_logger

log = get_logger(__name__)


class ModelStoreError(RuntimeError):
    pass


class ModelStore:
    def __init__(self, cache_dir: str | Path) -> None:
        self.root = Path(cache_dir)

    def path_for(self, model_id: str) -> Path:
        return self.root / model_id

    def load(self, model_id: str, device: str) -> VoiceModel:
        model_dir = self.path_for(model_id)
        if not model_dir.exists():
            raise ModelStoreError(f"voice model not found: {model_id} at {model_dir}")
        meta_file = model_dir / "meta.json"
        meta = json.loads(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else {}
        return VoiceModel.load(model_dir, device=device, meta=meta)

    def list_installed(self) -> list[str]:
        if not self.root.exists():
            return []
        return sorted(p.name for p in self.root.iterdir() if (p / "model.pth").exists())