"""Individual pipeline stages as free functions.

Kept separate from the pipeline class so each stage is unit-testable in
isolation with synthetic arrays and a fake model handle.
"""
from __future__ import annotations

import numpy as np

from src.models.voice_model import VoiceModel
from src.services.config_service import AudioConfig, ConversionConfig, VocoderConfig
from src.utils.logging_setup import get_logger
from src.utils.pitch import semitones_to_ratio

log = get_logger(__name__)


def extract_features(waveform: np.ndarray, cfg: AudioConfig) -> dict[str, np.ndarray]:
    from src.services.feature_extractor import FeatureExtractor

    extractor = FeatureExtractor(cfg)
    return extractor.run(waveform)


def retrieval_blend(feats: dict[str, np.ndarray], index, ratio: float) -> dict[str, np.ndarray]:
    if not 0.0 <= ratio <= 1.0:
        raise ValueError(f"index_ratio out of range: {ratio}")
    blended = index.query(feats["content"], top_k=8)
    feats["content"] = (1.0 - ratio) * feats["content"] + ratio * blended
    return feats


def pitch_shift(feats: dict[str, np.ndarray], semitones: int) -> dict[str, np.ndarray]:
    if semitones == 0:
        return feats
    feats["f0"] = feats["f0"] * semitones_to_ratio(semitones)
    return feats


def run_conversion(
    feats: dict[str, np.ndarray], model: VoiceModel, device: str, cfg: ConversionConfig
) -> np.ndarray:
    return model.synthesize(feats, device=device, protect=cfg.protect, rms_mix_rate=cfg.rms_mix_rate)


def vocode(latent: np.ndarray, cfg: VocoderConfig, device: str) -> np.ndarray:
    from src.services.vocoder_service import VocoderService

    return VocoderService(cfg, device).render(latent)