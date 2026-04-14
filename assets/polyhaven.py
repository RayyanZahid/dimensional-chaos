"""Poly Haven bridge — free CC0 HDRIs, PBR textures, and models.

No auth. All assets are CC0. We hit the public JSON API at
https://api.polyhaven.com and cache downloads under ./cache/polyhaven/.

Also emits typed MCP tool-call payloads for Blender MCP's
`download_polyhaven_asset` tool so the engine layer can dispatch to
Blender directly without re-downloading.
"""

import json
import os
import time
from pathlib import Path

import requests

BASE_URL = "https://api.polyhaven.com"
TIMEOUT = 60
CACHE_ROOT = Path("./cache/polyhaven")

# Common PBR map names Poly Haven ships for textures — we hoist these
# into a friendly dict shape on download_texture.
TEXTURE_MAP_KEYS = [
    "Diffuse", "diffuse",
    "nor_gl", "nor_dx", "Normal", "normal",
    "Rough", "rough", "Roughness", "roughness",
    "AO", "ao",
    "Displacement", "displacement",
    "Metal", "metal", "Metalness",
    "arm",
]


class PolyHavenBridge:
    """Public Poly Haven client — search, download HDRIs/textures, emit MCP calls."""

    def __init__(self):
        """No auth required."""
        CACHE_ROOT.mkdir(parents=True, exist_ok=True)

    def _get(self, path: str, params: dict = None) -> dict:
        """GET helper with 60s timeout and one retry."""
        url = f"{BASE_URL}{path}"
        for attempt in range(2):
            try:
                resp = requests.get(url, params=params, timeout=TIMEOUT)
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as err:
                if attempt == 0:
                    time.sleep(2.0)
                    continue
                raise RuntimeError(f"PolyHaven GET {path} failed: {err}") from err

    def search(self, asset_type: str = "hdris", categories: list = None) -> dict:
        """Search assets by type ('hdris'|'textures'|'models') and optional categories."""
        params = {"t": asset_type}
        if categories:
            params["categories"] = ",".join(categories)
        return self._get("/assets", params=params)

    def _files(self, slug: str) -> dict:
        """Internal: full file manifest for a slug (all resolutions/formats)."""
        return self._get(f"/files/{slug}")

    def _download(self, url: str, dest: Path) -> str:
        """Stream-download URL to dest. Returns str path. Skips if already present."""
        if dest.exists() and dest.stat().st_size > 0:
            return str(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(url, stream=True, timeout=TIMEOUT) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        fh.write(chunk)
        return str(dest)

    def _cache_dir(self, slug: str, resolution: str) -> Path:
        """Cache dir per slug+resolution."""
        return CACHE_ROOT / f"{slug}_{resolution}"

    def download_hdri(self, slug: str, resolution: str = "2k") -> str:
        """Download the .hdr for `slug` at `resolution`, return local path."""
        cdir = self._cache_dir(slug, resolution)
        dest = cdir / f"{slug}.hdr"
        if dest.exists() and dest.stat().st_size > 0:
            return str(dest)

        files = self._files(slug)
        hdri_block = files.get("hdri") or {}
        res_block = hdri_block.get(resolution) or {}
        hdr_info = res_block.get("hdr")
        if not hdr_info or "url" not in hdr_info:
            raise RuntimeError(
                f"PolyHaven: no hdr url for {slug} @ {resolution} (have: {list(res_block.keys())})"
            )
        return self._download(hdr_info["url"], dest)

    def download_texture(self, slug: str, resolution: str = "2k") -> dict:
        """Download PBR maps for a texture slug. Returns friendly map-name -> path dict."""
        cdir = self._cache_dir(slug, resolution)
        files = self._files(slug)
        out: dict = {}

        # Poly Haven nests files under map-type keys, then resolution, then format
        for map_key in list(files.keys()):
            if map_key.lower() in ("hdri",):
                continue
            map_block = files.get(map_key) or {}
            res_block = map_block.get(resolution) or {}
            if not isinstance(res_block, dict):
                continue

            # Pick best format: jpg > png > exr depending on map
            chosen = None
            for fmt in ("jpg", "png", "exr"):
                if fmt in res_block and isinstance(res_block[fmt], dict) and "url" in res_block[fmt]:
                    chosen = (fmt, res_block[fmt]["url"])
                    break
            if not chosen:
                continue

            fmt, url = chosen
            friendly = _friendly_map_name(map_key)
            dest = cdir / f"{slug}_{map_key}.{fmt}"
            try:
                out[friendly] = self._download(url, dest)
            except Exception as err:
                print(f"[PolyHaven] {slug}/{map_key} skipped: {err}")
        if not out:
            raise RuntimeError(f"PolyHaven: no texture maps resolved for {slug} @ {resolution}")
        return out

    def emit_polyhaven_mcp_call(
        self,
        slug: str,
        asset_type: str,
        resolution: str = "2k",
        file_format: str = "hdr",
    ) -> dict:
        """Emit typed payload for Blender MCP's download_polyhaven_asset tool."""
        return {
            "tool": "download_polyhaven_asset",
            "params": {
                "asset_id": slug,
                "asset_type": asset_type,
                "resolution": resolution,
                "file_format": file_format,
            },
        }


def _friendly_map_name(raw: str) -> str:
    """Normalize Poly Haven map keys to a standard PBR map name."""
    k = raw.lower()
    if k in ("diffuse", "diff", "col"):
        return "diffuse"
    if k.startswith("nor"):
        return "normal"
    if k.startswith("rough"):
        return "roughness"
    if k == "ao":
        return "ao"
    if k.startswith("disp"):
        return "displacement"
    if k.startswith("metal"):
        return "metalness"
    if k == "arm":
        return "arm"
    return k
