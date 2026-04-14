"""Emission utilities — write code, format for MCP, suggest Polyhaven downloads."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def emit_python_file(code: str, path: str | Path) -> Path:
    """Write emitted code to disk and return the resolved Path."""
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(code, encoding="utf-8")
    return p


def format_for_mcp(code: str) -> str:
    """Return code ready to pass as the single argument to execute_blender_code."""
    stripped = code.strip()
    if not stripped:
        return ""
    if not stripped.startswith("import bpy") and "import bpy" not in stripped.splitlines()[0]:
        stripped = "import bpy\n" + stripped
    return stripped


_PALETTE_HDRI_HINTS = {
    "golden_hour_valley": {"asset_id": "kloppenheim_06_puresky", "resolution": "2k"},
    "fog_valley": {"asset_id": "kloofendal_misty_morning_puresky", "resolution": "2k"},
    "overcast_studio": {"asset_id": "studio_small_08", "resolution": "2k"},
    "moonlit_concrete": {"asset_id": "moonlit_golf", "resolution": "2k"},
    "iridescent_candy": {"asset_id": "studio_country_hall", "resolution": "2k"},
    # neon_nightmare, sodium_vapor_liminal, bruised_sunset — no HDRI, procedural world.
}


def suggest_polyhaven_downloads(recipe: Any) -> list[dict[str, Any]]:
    """Return MCP typed-tool calls Claude should issue before executing emitted code."""
    calls: list[dict[str, Any]] = []
    palette = getattr(recipe, "palette", None) or (recipe.get("palette") if isinstance(recipe, dict) else None)
    hint = _PALETTE_HDRI_HINTS.get(palette or "")
    if hint:
        calls.append(
            {
                "tool": "download_polyhaven_asset",
                "params": {
                    "asset_id": hint["asset_id"],
                    "asset_type": "hdris",
                    "resolution": hint.get("resolution", "2k"),
                    "file_format": "hdr",
                },
            }
        )
    forces = getattr(recipe, "forces", None) or (recipe.get("forces", []) if isinstance(recipe, dict) else [])
    if "material_contrast" in forces:
        calls.append(
            {
                "tool": "download_polyhaven_asset",
                "params": {
                    "asset_id": "velvet_fabric_04",
                    "asset_type": "textures",
                    "resolution": "2k",
                    "file_format": "jpg",
                },
            }
        )
    return calls


def render_via_mcp_instructions() -> str:
    """Return a short guide for executing the emitted script via Blender MCP."""
    return (
        "Dimensional Chaos — MCP execution guide\n"
        "---------------------------------------\n"
        "1. If suggest_polyhaven_downloads() returns calls, issue each via the MCP tool\n"
        "   download_polyhaven_asset FIRST (HDRI must exist on disk before the script runs).\n"
        "2. Pass the assembled Python string to execute_blender_code(code=...).\n"
        "3. Call render_thumbnail (or get_viewport_screenshot for a fast preview).\n"
        "4. Call get_scene_info to confirm camera/lights/objects landed as planned.\n"
        "5. Iterate: tweak the Recipe, re-assemble, re-execute.\n"
    )
