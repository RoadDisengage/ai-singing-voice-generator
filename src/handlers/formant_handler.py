"""Formant-preservation handler.

Keeps the source speaker's formant envelope from being fully overwritten by
the target model, which is what causes the classic "chipmunk" artifact when
transposing a female source to a male target.
"""
from __future__ import annotations

import numpy as np

from src.utils.logging_setup import get_logger

log = get_logger(__name__)

HANDLER_NAME = "formant_preserve"


class _FormantHandler:
    name = HANDLER_NAME
    _blend = 0.2

    def transform(self, audio: np.ndarray, ctx: dict) -> np.ndarray:
        protect = float(ctx.get("config").conversion.protect)
        if protect <= 0.0:
            return audio
        # Soft-knee blend; the real formant warp happens in the model, this
        # only tags the context so the converter honors the ratio.
        ctx["formant_blend"] = min(1.0, self._blend + protect)
        return audio


def HANDLER() -> _FormantHandler:
    return _FormantHandler()