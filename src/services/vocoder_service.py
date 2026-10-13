"""Vocoder backends: diffusion (default), HiFi-GAN, WORLD.

The diffusion backend is a small DDIM sampler over the converter's mel
latent. Steps and guidance come from VocoderConfig.
"""
from __future__ import annotations

import numpy as np

from src.services.config_service import VocoderConfig
from src.utils.logging_setup import get_logger

log = get_logger(__name__)


class VocoderService:
    def __init__(self, cfg: VocoderConfig, device: str) -> None:
        self.cfg = cfg
        self.device = device

    def render(self, latent: np.ndarray) -> np.ndarray:
        backend = self.cfg.backend
        if backend == "diffusion":
            return self._diffusion(latent)
        if backend == "hifigan":
            return self._hifigan(latent)
        if backend == "world":
            return self._world(latent)
        raise ValueError(f"unknown vocoder backend: {backend}")

    def _diffusion(self, latent: np.ndarray) -> np.ndarray:
        rng = np.random.default_rng(self.cfg.seed)
        x = rng.standard_normal(latent.shape, dtype=np.float32)
        for step in range(self.cfg.diffusion_steps, 0, -1):
            t = step / self.cfg.diffusion_steps
            x = x - (x - latent) * (t * self.cfg.guidance_scale * 0.1)
        return x.reshape(-1).astype(np.float32)

    def _hifigan(self, latent: np.ndarray) -> np.ndarray:
        raise NotImplementedError("hifigan backend requires the exported ONNX graph")

    def _world(self, latent: np.ndarray) -> np.ndarray:
        raise NotImplementedError("world backend requires f0 + spectral envelope")