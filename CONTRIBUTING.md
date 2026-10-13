# Contributing to ai-singing-voice-generator

Thanks for wanting to help the AI Singing Voice Generator project. This is a
community-driven Windows desktop tool for converting spoken or sung input into
a target AI singing voice using retrieval-based voice conversion (RVC) plus a
lightweight diffusion vocoder.

## Ground rules

- Python 3.11+ on Windows 10/11 x64. CUDA 12.1 is the primary accelerated path;
  CPU fallback must always stay functional.
- Keep the layered architecture intact: `bootstrap` -> `core` -> `handlers`
  -> `services` -> `models` -> `utils`. Do not import upward across layers.
- Every new feature handler must register itself in
  `src/handlers/handler_registry.py` and ship with at least one test under
  `tests/`.
- Model weights are never committed. Document the download source in
  `docs/` or a module docstring instead.

## Dev setup

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m src.bootstrap.app --selftest
```

## Style

- `ruff` + `black` (line length 100). Run `ruff check src tests` before PR.
- Type hints on all public functions. `mypy --strict` on `src/core` and
  `src/services`.
- No bare `except:`. Log with the module logger, never `print` in library code.

## Pull requests

1. Fork, branch from `main`, name branches `feat/<topic>` or `fix/<topic>`.
2. One logical change per PR. Include a short repro or clip reference for
   audio-quality changes.
3. CI runs lint, type check, and the CPU-only test suite. GPU tests are
   opt-in via the `gpu` marker.

## Reporting audio artifacts

When filing an issue about metallic artifacts, pitch cracks, or timbre drift,
attach: the source clip, the target voice model id, the inference config
(`configs/default.yaml`), and the seed. Without a seed the bug is not
reproducible.