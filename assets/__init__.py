"""Dimensional Chaos — asset pipeline.

Feeds 3D assets into the engine from these sources:
- Meshy (text -> Nano Banana image -> image-to-3D -> GLB)
- Poly Haven (CC0 HDRIs, PBR textures, models)
- BlenderKit (curated community library; free-tier only, via in-Blender addon)

Plus curated Blender primitives for when generation isn't needed.
"""

from assets.meshy_bridge import MeshyBridge
from assets.polyhaven import PolyHavenBridge
from assets.primitives import PRIMITIVES
from assets.blenderkit_bridge import (
    emit_blenderkit_probe,
    emit_blenderkit_fetch,
    emit_blenderkit_place,
    recipe_to_search_query,
    ASSET_TYPES as BLENDERKIT_ASSET_TYPES,
)


class AssetRegistry:
    """Central registry for assets produced by the pipeline.

    Tracks (name -> descriptor) where descriptor is a dict describing
    the asset's source, local path(s), and any provenance metadata.
    Used by the engine/scene composer to resolve asset references.
    """

    def __init__(self):
        self._items: dict = {}

    def register(self, name: str, descriptor: dict) -> None:
        """Register or overwrite an asset descriptor under `name`."""
        self._items[name] = dict(descriptor)

    def get(self, name: str) -> dict:
        """Return descriptor for `name` or raise KeyError."""
        return self._items[name]

    def has(self, name: str) -> bool:
        """True if `name` is registered."""
        return name in self._items

    def all(self) -> dict:
        """Shallow copy of all registered assets."""
        return dict(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, name: str) -> bool:
        return name in self._items


__all__ = [
    "MeshyBridge",
    "PolyHavenBridge",
    "AssetRegistry",
    "PRIMITIVES",
    "emit_blenderkit_probe",
    "emit_blenderkit_fetch",
    "emit_blenderkit_place",
    "recipe_to_search_query",
    "BLENDERKIT_ASSET_TYPES",
]
