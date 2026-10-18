"""Import-time compatibility shim for CPUs without AVX2.

LiveKit Agents 1.6+ eagerly imports ``livekit.local_inference``, a native
(pybind11 + ONNX Runtime) module that bundles the local ``turn-detector-v1-mini``
end-of-turn model and the bundled Silero VAD. The published wheels are compiled
for AVX2, so importing them on an older CPU (for example Intel Sandy Bridge or
Ivy Bridge) aborts the interpreter with ``STATUS_ILLEGAL_INSTRUCTION``
(``0xC000001D``), taking the whole agent process with it.

Importing this module registers a placeholder for ``livekit.local_inference``
when AVX2 is unavailable, which lets ``import livekit.agents`` (and every
plugin) succeed. The bundled local models cannot run on such a CPU, so the
agent is configured without them in ``src/agent.py``: ``vad=None`` plus a
cloud-only ``inference.TurnDetector(local_fallback=False)``.

On AVX2-capable machines nothing is stubbed and the real module is used.
"""

from __future__ import annotations

import sys
import types

VAD_WINDOW_SAMPLES = 512
EOT_MAX_SAMPLES = 19200

_UNAVAILABLE = (
    "livekit.local_inference is unavailable on this CPU because the bundled ONNX "
    "Runtime requires AVX2. Use the cloud turn detector (local_fallback=False) and "
    "vad=None, or run the agent on an AVX2-capable machine."
)


def _avx2_available() -> bool:
    """Report whether numpy detected AVX2 support at runtime."""
    try:
        from numpy._core import _multiarray_umath
    except ImportError:  # pragma: no cover - numpy layout differences
        try:
            from numpy.core import _multiarray_umath  # type: ignore[no-redef]
        except ImportError:
            return True

    features = getattr(_multiarray_umath, "__cpu_features__", None)
    if features is None:
        return True
    return bool(features.get("AVX2", True))


class _UnavailableModel:
    """Stand-in for the native ``VAD``/``EOT`` classes that cannot load here."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        raise RuntimeError(_UNAVAILABLE)

    def predict(self, *args: object, **kwargs: object) -> None:
        raise RuntimeError(_UNAVAILABLE)

    def reset(self) -> None:
        raise RuntimeError(_UNAVAILABLE)

    def close(self) -> None:
        raise RuntimeError(_UNAVAILABLE)

    def __enter__(self) -> _UnavailableModel:
        raise RuntimeError(_UNAVAILABLE)

    def __exit__(self, *exc: object) -> bool:
        return False


def install() -> bool:
    """Stub ``livekit.local_inference`` when AVX2 is missing.

    Returns ``True`` when the placeholder was registered.
    """
    if "livekit.local_inference" in sys.modules:
        return False
    if _avx2_available():
        return False

    module = types.ModuleType("livekit.local_inference")
    module.__doc__ = _UNAVAILABLE
    module.VAD = _UnavailableModel  # type: ignore[attr-defined]
    module.EOT = _UnavailableModel  # type: ignore[attr-defined]
    module.VAD_WINDOW_SAMPLES = VAD_WINDOW_SAMPLES
    module.EOT_MAX_SAMPLES = EOT_MAX_SAMPLES
    module.init_vad = lambda: None
    module.init_eot = lambda: None
    module._parallelism = lambda: 1
    module.__all__ = [
        "EOT",
        "EOT_MAX_SAMPLES",
        "VAD",
        "VAD_WINDOW_SAMPLES",
        "init_eot",
        "init_vad",
    ]

    sys.modules["livekit.local_inference"] = module

    package = sys.modules.get("livekit")
    if package is not None:
        package.local_inference = module  # type: ignore[attr-defined]

    return True


INSTALLED = install()
