"""Dimensional Chaos engine — taste layer over Blender MCP."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .assembler import Recipe, Scene

__all__ = [
    "Recipe",
    "Scene",
    "load_tokens",
    "MODES",
    "PALETTES",
    "VOICES",
    "FORCES",
    "TOKENS_DIR",
]

# Canonical keys — source of truth for validation before token files land.
MODES = [
    "claymation_warmth",
    "studio_ghibli_nature",
    "brutalist_sculpture",
    "plushcore_soft",
    "hyperreal_chrome",
    "liminal_lowpoly",
    "isometric_diorama",
]

PALETTES = [
    "golden_hour_valley",
    "neon_nightmare",
    "fog_valley",
    "overcast_studio",
    "sodium_vapor_liminal",
    "moonlit_concrete",
    "iridescent_candy",
    "bruised_sunset",
]

VOICES = [
    "intimate_macro",
    "gods_eye_ortho",
    "architectural_wide",
    "dolly_cinematic",
    "dutch_drama",
]

FORCES = [
    "scale_distortion",
    "light_as_character",
    "material_contrast",
    "negative_space",
    "impossible_physics",
    "hand_evidence",
]

TOKENS_DIR = Path(__file__).resolve().parent.parent / "tokens"


def _safe_load(path: Path) -> dict[str, Any]:
    """Load YAML if present, else return empty dict."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_tokens(tokens_dir: Path | str | None = None) -> dict[str, dict[str, Any]]:
    """Load modes/palettes/voices/forces YAML into a single dict."""
    base = Path(tokens_dir) if tokens_dir else TOKENS_DIR
    return {
        "modes": _safe_load(base / "modes.yaml").get("modes", {}),
        "palettes": _safe_load(base / "palettes.yaml").get("palettes", {}),
        "voices": _safe_load(base / "voices.yaml").get("voices", {}),
        "forces": _safe_load(base / "forces.yaml").get("forces", {}),
    }
