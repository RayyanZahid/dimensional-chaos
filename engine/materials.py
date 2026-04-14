"""Shader presets per mode — PBR always, never flat Diffuse."""
from __future__ import annotations

from typing import Callable


def _rgb4(rgb: tuple[float, float, float]) -> str:
    """Render an (r,g,b,1.0) literal for emitted shader code."""
    r, g, b = rgb
    return f"({r:.4f}, {g:.4f}, {b:.4f}, 1.0)"


def _mat_header(name: str) -> list[str]:
    """Create a fresh node-based material and wipe default nodes."""
    safe = name.replace("'", "")
    return [
        f"_mat = bpy.data.materials.new(name='{safe}')",
        "_mat.use_nodes = True",
        "_nt = _mat.node_tree",
        "_nt.nodes.clear()",
        "_out = _nt.nodes.new('ShaderNodeOutputMaterial')",
    ]


def _principled(name: str = "_bsdf") -> str:
    """Emit a Principled BSDF node binding line."""
    return f"{name} = _nt.nodes.new('ShaderNodeBsdfPrincipled')"


def make_claymation_material(name: str, base_rgb: tuple[float, float, float] = (0.85, 0.55, 0.38)) -> list[str]:
    """Clay with slight SSS, velvet sheen 0.3, roughness 0.62."""
    lines = _mat_header(name)
    lines += [
        _principled("_bsdf"),
        f"_bsdf.inputs['Base Color'].default_value = {_rgb4(base_rgb)}",
        "_bsdf.inputs['Roughness'].default_value = 0.62",
        "if 'Sheen Weight' in _bsdf.inputs:",
        "    _bsdf.inputs['Sheen Weight'].default_value = 0.3",
        "elif 'Sheen' in _bsdf.inputs:",
        "    _bsdf.inputs['Sheen'].default_value = 0.3",
        "if 'Subsurface Weight' in _bsdf.inputs:",
        "    _bsdf.inputs['Subsurface Weight'].default_value = 0.12",
        "elif 'Subsurface' in _bsdf.inputs:",
        "    _bsdf.inputs['Subsurface'].default_value = 0.12",
        "_nt.links.new(_bsdf.outputs['BSDF'], _out.inputs['Surface'])",
    ]
    return lines


def make_brutalist_concrete(name: str) -> list[str]:
    """Noise-driven concrete bump, roughness 0.85, low spec."""
    lines = _mat_header(name)
    lines += [
        _principled("_bsdf"),
        "_bsdf.inputs['Base Color'].default_value = (0.42, 0.42, 0.43, 1.0)",
        "_bsdf.inputs['Roughness'].default_value = 0.85",
        "if 'Specular IOR Level' in _bsdf.inputs:",
        "    _bsdf.inputs['Specular IOR Level'].default_value = 0.3",
        "elif 'Specular' in _bsdf.inputs:",
        "    _bsdf.inputs['Specular'].default_value = 0.3",
        "_noise = _nt.nodes.new('ShaderNodeTexNoise')",
        "_noise.inputs['Scale'].default_value = 12.0",
        "_noise.inputs['Detail'].default_value = 8.0",
        "_bump = _nt.nodes.new('ShaderNodeBump')",
        "_bump.inputs['Strength'].default_value = 0.3",
        "_nt.links.new(_noise.outputs['Fac'], _bump.inputs['Height'])",
        "_nt.links.new(_bump.outputs['Normal'], _bsdf.inputs['Normal'])",
        "_nt.links.new(_bsdf.outputs['BSDF'], _out.inputs['Surface'])",
    ]
    return lines


def make_plush_velvet(name: str, base_rgb: tuple[float, float, float] = (0.92, 0.72, 0.78)) -> list[str]:
    """Velvet/sheen-heavy plush via Principled BSDF sheen inputs."""
    lines = _mat_header(name)
    lines += [
        _principled("_bsdf"),
        f"_bsdf.inputs['Base Color'].default_value = {_rgb4(base_rgb)}",
        "_bsdf.inputs['Roughness'].default_value = 0.92",
        "if 'Sheen Weight' in _bsdf.inputs:",
        "    _bsdf.inputs['Sheen Weight'].default_value = 0.85",
        "    _bsdf.inputs['Sheen Roughness'].default_value = 0.45",
        "    _bsdf.inputs['Sheen Tint'].default_value = (1.0, 0.95, 0.95, 1.0)",
        "elif 'Sheen' in _bsdf.inputs:",
        "    _bsdf.inputs['Sheen'].default_value = 0.85",
        "_velvet = _nt.nodes.new('ShaderNodeBsdfVelvet') if 'ShaderNodeBsdfVelvet' in dir(bpy.types) else None",
        "if _velvet is not None:",
        f"    _velvet.inputs['Color'].default_value = {_rgb4(base_rgb)}",
        "    _mix = _nt.nodes.new('ShaderNodeMixShader')",
        "    _mix.inputs['Fac'].default_value = 0.35",
        "    _nt.links.new(_bsdf.outputs['BSDF'], _mix.inputs[1])",
        "    _nt.links.new(_velvet.outputs['BSDF'], _mix.inputs[2])",
        "    _nt.links.new(_mix.outputs['Shader'], _out.inputs['Surface'])",
        "else:",
        "    _nt.links.new(_bsdf.outputs['BSDF'], _out.inputs['Surface'])",
    ]
    return lines


def make_chrome_iridescent(name: str) -> list[str]:
    """Metallic chrome with thin-film iridescence (Blender 4.x Coat Tint)."""
    lines = _mat_header(name)
    lines += [
        _principled("_bsdf"),
        "_bsdf.inputs['Base Color'].default_value = (0.88, 0.89, 0.93, 1.0)",
        "_bsdf.inputs['Metallic'].default_value = 1.0",
        "_bsdf.inputs['Roughness'].default_value = 0.08",
        "if 'Coat Weight' in _bsdf.inputs:",
        "    _bsdf.inputs['Coat Weight'].default_value = 0.6",
        "    _bsdf.inputs['Coat Roughness'].default_value = 0.05",
        "if 'Coat Tint' in _bsdf.inputs:",
        "    _bsdf.inputs['Coat Tint'].default_value = (0.6, 0.85, 1.0, 1.0)",
        "# iridescent tint via Fresnel-driven ColorRamp",
        "_fres = _nt.nodes.new('ShaderNodeFresnel')",
        "_fres.inputs['IOR'].default_value = 1.45",
        "_ramp = _nt.nodes.new('ShaderNodeValToRGB')",
        "_ramp.color_ramp.elements[0].color = (0.3, 0.1, 0.85, 1.0)",
        "_ramp.color_ramp.elements[1].color = (1.0, 0.65, 0.25, 1.0)",
        "_nt.links.new(_fres.outputs['Fac'], _ramp.inputs['Fac'])",
        "_nt.links.new(_ramp.outputs['Color'], _bsdf.inputs['Base Color'])",
        "_nt.links.new(_bsdf.outputs['BSDF'], _out.inputs['Surface'])",
    ]
    return lines


def make_liminal_flat(name: str, tex_path: str | None = None) -> list[str]:
    """Flat PS1-ish texture with Closest interpolation, shadeless feel."""
    lines = _mat_header(name)
    lines += [
        "_em = _nt.nodes.new('ShaderNodeEmission')",
        _principled("_bsdf"),
        "_bsdf.inputs['Roughness'].default_value = 1.0",
        "_bsdf.inputs['Base Color'].default_value = (0.72, 0.68, 0.55, 1.0)",
    ]
    if tex_path:
        safe = tex_path.replace("'", "").replace("\\", "/")
        lines += [
            "_img = _nt.nodes.new('ShaderNodeTexImage')",
            "import os as _os",
            f"_p = '{safe}'",
            "if _os.path.exists(_p):",
            "    _img.image = bpy.data.images.load(_p, check_existing=True)",
            "_img.interpolation = 'Closest'",
            "_nt.links.new(_img.outputs['Color'], _em.inputs['Color'])",
            "_em.inputs['Strength'].default_value = 1.0",
            "_nt.links.new(_em.outputs['Emission'], _out.inputs['Surface'])",
        ]
    else:
        lines += [
            "_em.inputs['Color'].default_value = (0.72, 0.68, 0.55, 1.0)",
            "_em.inputs['Strength'].default_value = 0.8",
            "_nt.links.new(_em.outputs['Emission'], _out.inputs['Surface'])",
        ]
    return lines


def make_toon_ghibli(name: str, base_rgb: tuple[float, float, float] = (0.48, 0.72, 0.40)) -> list[str]:
    """Shader-to-RGB clamped 2-band toon ramp + emission mix, Ghibli nature palette."""
    lines = _mat_header(name)
    lines += [
        _principled("_bsdf"),
        f"_bsdf.inputs['Base Color'].default_value = {_rgb4(base_rgb)}",
        "_bsdf.inputs['Roughness'].default_value = 0.7",
        "_s2rgb = _nt.nodes.new('ShaderNodeShaderToRGB') if 'ShaderNodeShaderToRGB' in dir(bpy.types) else None",
        "if _s2rgb is not None:",
        "    _ramp = _nt.nodes.new('ShaderNodeValToRGB')",
        "    _ramp.color_ramp.interpolation = 'CONSTANT'",
        "    _ramp.color_ramp.elements[0].position = 0.0",
        f"    _ramp.color_ramp.elements[0].color = {_rgb4((base_rgb[0]*0.55, base_rgb[1]*0.55, base_rgb[2]*0.55))}",
        "    _ramp.color_ramp.elements[1].position = 0.5",
        f"    _ramp.color_ramp.elements[1].color = {_rgb4(base_rgb)}",
        "    _em = _nt.nodes.new('ShaderNodeEmission')",
        "    _mix = _nt.nodes.new('ShaderNodeMixShader')",
        "    _mix.inputs['Fac'].default_value = 0.1",
        "    _nt.links.new(_bsdf.outputs['BSDF'], _s2rgb.inputs['Shader'])",
        "    _nt.links.new(_s2rgb.outputs['Color'], _ramp.inputs['Fac'])",
        "    _nt.links.new(_ramp.outputs['Color'], _em.inputs['Color'])",
        "    _nt.links.new(_em.outputs['Emission'], _mix.inputs[1])",
        "    _nt.links.new(_bsdf.outputs['BSDF'], _mix.inputs[2])",
        "    _nt.links.new(_mix.outputs['Shader'], _out.inputs['Surface'])",
        "else:",
        "    _nt.links.new(_bsdf.outputs['BSDF'], _out.inputs['Surface'])",
    ]
    return lines


def make_diorama_plastic(name: str, base_rgb: tuple[float, float, float] = (0.7, 0.35, 0.25)) -> list[str]:
    """Diorama model paint — mild SSS, medium roughness, slight coat."""
    lines = _mat_header(name)
    lines += [
        _principled("_bsdf"),
        f"_bsdf.inputs['Base Color'].default_value = {_rgb4(base_rgb)}",
        "_bsdf.inputs['Roughness'].default_value = 0.45",
        "if 'Subsurface Weight' in _bsdf.inputs:",
        "    _bsdf.inputs['Subsurface Weight'].default_value = 0.05",
        "elif 'Subsurface' in _bsdf.inputs:",
        "    _bsdf.inputs['Subsurface'].default_value = 0.05",
        "if 'Coat Weight' in _bsdf.inputs:",
        "    _bsdf.inputs['Coat Weight'].default_value = 0.2",
        "_nt.links.new(_bsdf.outputs['BSDF'], _out.inputs['Surface'])",
    ]
    return lines


_MODE_MATERIALS: dict[str, Callable[..., list[str]]] = {
    "claymation_warmth": make_claymation_material,
    "studio_ghibli_nature": make_toon_ghibli,
    "brutalist_sculpture": lambda name, base_rgb=None: make_brutalist_concrete(name),
    "plushcore_soft": make_plush_velvet,
    "hyperreal_chrome": lambda name, base_rgb=None: make_chrome_iridescent(name),
    "liminal_lowpoly": lambda name, base_rgb=None: make_liminal_flat(name),
    "isometric_diorama": make_diorama_plastic,
}


def mode_to_material_factory(mode_key: str) -> Callable[..., list[str]]:
    """Return the material-factory function for a given mode."""
    return _MODE_MATERIALS.get(mode_key, make_diorama_plastic)
