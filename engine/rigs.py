"""Lighting rigs — three-point by default, HDRI always preferred over solid background."""
from __future__ import annotations

from typing import Callable


def kelvin_to_rgb(k: int) -> tuple[float, float, float]:
    """Approximate Planckian color temperature to linear RGB (Tanner Helland)."""
    temp = max(1000, min(40000, int(k))) / 100.0
    if temp <= 66:
        r = 255.0
        g = 99.4708025861 * _safe_log(temp) - 161.1195681661
        b = 0.0 if temp <= 19 else 138.5177312231 * _safe_log(temp - 10) - 305.0447927307
    else:
        r = 329.698727446 * ((temp - 60) ** -0.1332047592)
        g = 288.1221695283 * ((temp - 60) ** -0.0755148492)
        b = 255.0
    return tuple(max(0.0, min(1.0, c / 255.0)) for c in (r, g, b))  # type: ignore[return-value]


def _safe_log(x: float) -> float:
    """math.log with a floor to avoid domain errors for low kelvin."""
    from math import log

    return log(max(1e-6, x))


def _rgb_literal(rgb: tuple[float, float, float]) -> str:
    """Render an (r,g,b,a=1.0) tuple for use in emitted Blender code."""
    r, g, b = rgb
    return f"({r:.4f}, {g:.4f}, {b:.4f}, 1.0)"


def three_point(
    key_k: int = 5600,
    key_power: float = 1200.0,
    fill_k: int | None = None,
    fill_power: float | None = None,
    rim_power: float | None = None,
) -> list[str]:
    """Emit a canonical three-point rig (key, fill, rim) as Blender Python."""
    fill_k = fill_k or max(3200, key_k - 1200)
    fill_power = fill_power if fill_power is not None else key_power * 0.35
    rim_power = rim_power if rim_power is not None else key_power * 0.65
    key_rgb = _rgb_literal(kelvin_to_rgb(key_k))
    fill_rgb = _rgb_literal(kelvin_to_rgb(fill_k))
    rim_rgb = _rgb_literal(kelvin_to_rgb(7500))
    return [
        "# three-point lighting rig",
        "bpy.ops.object.light_add(type='AREA', location=(4.0, -4.0, 4.5))",
        "_key = bpy.context.object",
        "_key.name = 'DC_Key'",
        "_key.data.energy = " + f"{key_power:.2f}",
        "_key.data.size = 2.5",
        "_key.data.color = " + key_rgb[:-5] + ")",
        "_key.rotation_euler = (0.9, 0.0, 0.78)",
        "bpy.ops.object.light_add(type='AREA', location=(-3.5, -2.5, 3.0))",
        "_fill = bpy.context.object",
        "_fill.name = 'DC_Fill'",
        "_fill.data.energy = " + f"{fill_power:.2f}",
        "_fill.data.size = 4.0",
        "_fill.data.color = " + fill_rgb[:-5] + ")",
        "_fill.rotation_euler = (1.0, 0.0, -0.6)",
        "bpy.ops.object.light_add(type='AREA', location=(0.0, 4.0, 3.5))",
        "_rim = bpy.context.object",
        "_rim.name = 'DC_Rim'",
        "_rim.data.energy = " + f"{rim_power:.2f}",
        "_rim.data.size = 1.5",
        "_rim.data.color = " + rim_rgb[:-5] + ")",
        "_rim.rotation_euler = (1.4, 0.0, 3.14)",
    ]


def hdri_rig(slug: str, strength: float = 1.0) -> list[str]:
    """Emit a world-HDRI setup; assumes asset already downloaded via MCP."""
    safe_slug = (slug or "studio_small_08").replace("'", "")
    return [
        "# HDRI world setup (download via MCP download_polyhaven_asset first)",
        "_world = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')",
        "bpy.context.scene.world = _world",
        "_world.use_nodes = True",
        "_nt = _world.node_tree",
        "_nt.nodes.clear()",
        "_bg = _nt.nodes.new('ShaderNodeBackground')",
        "_env = _nt.nodes.new('ShaderNodeTexEnvironment')",
        "_out = _nt.nodes.new('ShaderNodeOutputWorld')",
        "_map = _nt.nodes.new('ShaderNodeMapping')",
        "_coord = _nt.nodes.new('ShaderNodeTexCoord')",
        f"_bg.inputs['Strength'].default_value = {strength:.3f}",
        "import os",
        f"_slug = '{safe_slug}'",
        "_candidates = ["
        "os.path.join(bpy.app.tempdir, 'polyhaven', _slug + '.hdr'),"
        "os.path.join(bpy.app.tempdir, _slug + '.hdr'),"
        "os.path.expanduser('~/Documents/polyhaven/' + _slug + '.hdr')]",
        "_found = next((p for p in _candidates if os.path.exists(p)), None)",
        "if _found:",
        "    _env.image = bpy.data.images.load(_found, check_existing=True)",
        "_nt.links.new(_coord.outputs['Generated'], _map.inputs['Vector'])",
        "_nt.links.new(_map.outputs['Vector'], _env.inputs['Vector'])",
        "_nt.links.new(_env.outputs['Color'], _bg.inputs['Color'])",
        "_nt.links.new(_bg.outputs['Background'], _out.inputs['Surface'])",
    ]


def _rig_with_hdri(slug: str, hdri_strength: float, three_pt: list[str]) -> list[str]:
    """Compose HDRI + three-point in the canonical order."""
    return hdri_rig(slug, hdri_strength) + [""] + three_pt


def golden_hour() -> list[str]:
    """Warm low-angle key 3200K, cool rim 7000K, gentle fill."""
    return _rig_with_hdri(
        "kloppenheim_06_puresky",
        0.9,
        three_point(key_k=3200, key_power=1400.0, fill_k=4500, fill_power=400.0, rim_power=700.0),
    )


def neon_nightmare() -> list[str]:
    """Magenta key, cyan rim — saturated, low fill, high contrast."""
    return [
        "# neon_nightmare world (solid dark + colored lamps)",
        "_world = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')",
        "bpy.context.scene.world = _world",
        "_world.use_nodes = True",
        "_nt = _world.node_tree",
        "_nt.nodes.clear()",
        "_bg = _nt.nodes.new('ShaderNodeBackground')",
        "_out = _nt.nodes.new('ShaderNodeOutputWorld')",
        "_bg.inputs['Color'].default_value = (0.01, 0.005, 0.02, 1.0)",
        "_bg.inputs['Strength'].default_value = 0.3",
        "_nt.links.new(_bg.outputs['Background'], _out.inputs['Surface'])",
        "",
        "bpy.ops.object.light_add(type='AREA', location=(3.5, -2.0, 2.5))",
        "_key = bpy.context.object",
        "_key.name = 'DC_NeonKey'",
        "_key.data.energy = 1800.0",
        "_key.data.color = (1.0, 0.15, 0.65)",
        "_key.data.size = 1.2",
        "_key.rotation_euler = (1.0, 0.0, 0.7)",
        "bpy.ops.object.light_add(type='AREA', location=(-3.0, 2.0, 2.0))",
        "_rim = bpy.context.object",
        "_rim.name = 'DC_NeonRim'",
        "_rim.data.energy = 1400.0",
        "_rim.data.color = (0.1, 0.85, 1.0)",
        "_rim.data.size = 1.0",
        "_rim.rotation_euler = (1.2, 0.0, -1.0)",
    ]


def fog_valley() -> list[str]:
    """Cool diffuse key 5500K + volumetric world fog density 0.15."""
    out = _rig_with_hdri(
        "kloofendal_misty_morning_puresky",
        0.7,
        three_point(key_k=5500, key_power=900.0, fill_power=450.0, rim_power=300.0),
    )
    out += [
        "",
        "# volumetric fog",
        "_vol = _nt.nodes.new('ShaderNodeVolumePrincipled')",
        "_vol.inputs['Density'].default_value = 0.15",
        "_vol.inputs['Color'].default_value = (0.72, 0.78, 0.82, 1.0)",
        "_nt.links.new(_vol.outputs['Volume'], _out.inputs['Volume'])",
    ]
    return out


def overcast_studio() -> list[str]:
    """Flat diffuse studio HDRI, muted three-point."""
    return _rig_with_hdri(
        "studio_small_08",
        1.1,
        three_point(key_k=5200, key_power=900.0, fill_power=550.0, rim_power=400.0),
    )


def sodium_vapor() -> list[str]:
    """Amber sodium ~2100K dominant, liminal parking-lot mood."""
    return [
        "# sodium_vapor liminal lamp",
        "_world = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')",
        "bpy.context.scene.world = _world",
        "_world.use_nodes = True",
        "_nt = _world.node_tree",
        "_nt.nodes.clear()",
        "_bg = _nt.nodes.new('ShaderNodeBackground')",
        "_out = _nt.nodes.new('ShaderNodeOutputWorld')",
        "_bg.inputs['Color'].default_value = (0.02, 0.015, 0.005, 1.0)",
        "_bg.inputs['Strength'].default_value = 0.4",
        "_nt.links.new(_bg.outputs['Background'], _out.inputs['Surface'])",
        "",
        "bpy.ops.object.light_add(type='SPOT', location=(0.0, 0.0, 6.0))",
        "_key = bpy.context.object",
        "_key.name = 'DC_SodiumKey'",
        "_key.data.energy = 2500.0",
        "_key.data.color = (1.0, 0.55, 0.12)",
        "_key.data.spot_size = 1.4",
        "_key.data.spot_blend = 0.4",
        "_key.rotation_euler = (3.14, 0.0, 0.0)",
    ]


def moonlit() -> list[str]:
    """Cool 8500K key, deep shadows, low fill."""
    return _rig_with_hdri(
        "moonlit_golf",
        0.6,
        three_point(key_k=8500, key_power=800.0, fill_k=9000, fill_power=120.0, rim_power=300.0),
    )


def iridescent_candy() -> list[str]:
    """Colored-gel rig: pink key, teal fill, lime rim on bright HDRI."""
    base = hdri_rig("studio_country_hall", 1.3)
    return base + [
        "",
        "bpy.ops.object.light_add(type='AREA', location=(3.0, -3.0, 3.5))",
        "_key = bpy.context.object",
        "_key.name = 'DC_CandyKey'",
        "_key.data.energy = 1100.0",
        "_key.data.color = (1.0, 0.6, 0.85)",
        "_key.data.size = 2.0",
        "bpy.ops.object.light_add(type='AREA', location=(-3.0, -1.0, 2.5))",
        "_fill = bpy.context.object",
        "_fill.name = 'DC_CandyFill'",
        "_fill.data.energy = 600.0",
        "_fill.data.color = (0.35, 0.9, 0.95)",
        "_fill.data.size = 3.0",
        "bpy.ops.object.light_add(type='AREA', location=(0.0, 3.5, 2.8))",
        "_rim = bpy.context.object",
        "_rim.name = 'DC_CandyRim'",
        "_rim.data.energy = 800.0",
        "_rim.data.color = (0.75, 1.0, 0.5)",
        "_rim.data.size = 1.2",
    ]


def bruised_sunset() -> list[str]:
    """Magenta-amber-violet gradient world, warm low key."""
    return [
        "# bruised_sunset gradient world",
        "_world = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')",
        "bpy.context.scene.world = _world",
        "_world.use_nodes = True",
        "_nt = _world.node_tree",
        "_nt.nodes.clear()",
        "_bg = _nt.nodes.new('ShaderNodeBackground')",
        "_out = _nt.nodes.new('ShaderNodeOutputWorld')",
        "_gr = _nt.nodes.new('ShaderNodeValToRGB')",
        "_coord = _nt.nodes.new('ShaderNodeTexCoord')",
        "_sep = _nt.nodes.new('ShaderNodeSeparateXYZ')",
        "_gr.color_ramp.elements[0].color = (0.8, 0.15, 0.35, 1.0)",
        "_gr.color_ramp.elements[1].color = (0.25, 0.08, 0.45, 1.0)",
        "_nt.links.new(_coord.outputs['Generated'], _sep.inputs['Vector'])",
        "_nt.links.new(_sep.outputs['Z'], _gr.inputs['Fac'])",
        "_nt.links.new(_gr.outputs['Color'], _bg.inputs['Color'])",
        "_nt.links.new(_bg.outputs['Background'], _out.inputs['Surface'])",
        "_bg.inputs['Strength'].default_value = 0.8",
        "",
    ] + three_point(key_k=2900, key_power=1200.0, fill_k=6000, fill_power=300.0, rim_power=550.0)


_PALETTE_DISPATCH: dict[str, Callable[[], list[str]]] = {
    "golden_hour_valley": golden_hour,
    "neon_nightmare": neon_nightmare,
    "fog_valley": fog_valley,
    "overcast_studio": overcast_studio,
    "sodium_vapor_liminal": sodium_vapor,
    "moonlit_concrete": moonlit,
    "iridescent_candy": iridescent_candy,
    "bruised_sunset": bruised_sunset,
}


def palette_to_rig(palette_key: str) -> list[str]:
    """Dispatch a palette key to its lighting-rig function."""
    fn = _PALETTE_DISPATCH.get(palette_key)
    if fn is None:
        return overcast_studio()
    return fn()
