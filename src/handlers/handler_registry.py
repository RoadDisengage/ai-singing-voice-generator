"""Discovers and holds active feature handlers.

Handlers are plain classes exposing `name` and `transform(audio, ctx)`.
Built-ins live in this package; third-party plugins under
`src/handlers/plugins/` are loaded only when `load_plugins=True`.
"""
from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass, field

from src.utils.logging_setup import get_logger

log = get_logger(__name__)

_BUILTIN_MODULES = (
    "src.handlers.denoise_handler",
    "src.handlers.formant_handler",
    "src.handlers.deesser_handler",
)


@dataclass(slots=True)
class HandlerRegistry:
    handlers: list = field(default_factory=list)

    @classmethod
    def discover(cls, load_plugins: bool = True) -> "HandlerRegistry":
        registry = cls()
        for module_name in _BUILTIN_MODULES:
            module = importlib.import_module(module_name)
            registry.handlers.append(module.HANDLER())
        if load_plugins:
            registry._load_plugins()
        log.info("Active handlers: %s", [h.name for h in registry.handlers])
        return registry

    def _load_plugins(self) -> None:
        try:
            from src.handlers import plugins
        except ImportError:
            return
        for info in pkgutil.iter_modules(plugins.__path__):
            module = importlib.import_module(f"src.handlers.plugins.{info.name}")
            if hasattr(module, "HANDLER"):
                self.handlers.append(module.HANDLER())
                log.warning("Loaded third-party plugin handler: %s", info.name)

    def active(self) -> list:
        return list(self.handlers)