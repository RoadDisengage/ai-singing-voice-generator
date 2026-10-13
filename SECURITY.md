# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | yes       |
| 0.5.x   | security fixes only |
| < 0.5   | no        |

## Reporting a vulnerability

Do not open a public issue for security problems. Email
`security@ai-singing-voice-generator.dev` with a description, a repro, and the
affected module path. We aim to acknowledge within 72 hours.

## Scope

This is a **local desktop tool**. It does not run a server, does not phone
home, and does not upload audio anywhere by default. The attack surface is:

- **Model file loading.** `.pth` / `.onnx` / `.safetensors` checkpoints are
  loaded with `torch.load(..., weights_only=True)` and `safetensors` where
  possible. A malicious checkpoint is the primary risk. Only load weights from
  sources you trust.
- **Plugin handlers.** Third-party handlers under `src/handlers/plugins/` run
  in-process. Review plugin source before enabling it.
- **Audio import.** Decoding uses `soundfile`/`ffmpeg`. Malformed media files
  are a known class of parser bug; keep ffmpeg patched.

## Out of scope

- Voice cloning of a person without consent. That is a legal and ethical
  matter for the user, not a code vulnerability. See `docs/ethics.md`.
- Quality complaints about generated audio.

## Hardening notes

- Run with a dedicated non-admin Windows account.
- Keep `models/checkpoints/` read-only after download.
- Disable plugin auto-load (`--no-plugins`) for untrusted sessions.