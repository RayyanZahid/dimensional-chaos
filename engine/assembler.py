"""Assembler — Recipe → Scene → emitted Blender Python."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .cameras import add_camera
from .compositor import apply_mode_post
from .materials import mode_to_material_factory
from .rigs import palette_to_rig

# Keep the canonical key lists aligned with engine/__init__.py (avoid circular import at top).
_MODES = {
    "claymation_warmth",
    "studio_ghibli_nature",
    "brutalist_sculpture",
    "plushcore_soft",
    "hyperreal_chrome",
    "liminal_lowpoly",
    "isometric_diorama",
}
_PALETTES = {
    "golden_hour_valley",
    "neon_nightmare",
    "fog_valley",
    "overcast_studio",
    "sodium_vapor_liminal",
    "moonlit_concrete",
    "iridescent_candy",
    "bruised_sunset",
}
_VOICES = {
    "intimate_macro",
    "gods_eye_ortho",
    "architectural_wide",
    "dolly_cinematic",
    "dutch_drama",
}
_FORCES = {
    "scale_distortion",
    "light_as_character",
    "material_contrast",
    "negative_space",
    "impossible_physics",
    "hand_evidence",
}


@dataclass
class Recipe:
    """An aesthetic recipe: mode + palette + voice + 1-4 forces + optional subject."""

    mode: str
    palette: str
    voice: str
    forces: list[str]
    subject: str = ""
    extras: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Raise ValueError if any key is invalid or forces list malformed."""
        if self.mode not in _MODES:
            raise ValueError(f"invalid mode: {self.mode!r}")
        if self.palette not in _PALETTES:
            raise ValueError(f"invalid palette: {self.palette!r}")
        if self.voice not in _VOICES:
            raise ValueError(f"invalid voice: {self.voice!r}")
        if not (1 <= len(self.forces) <= 4):
            raise ValueError(f"forces must be 1..4 items, got {len(self.forces)}")
        bad = [f for f in self.forces if f not in _FORCES]
        if bad:
            raise ValueError(f"invalid forces: {bad!r}")


def _header(recipe: Recipe) -> list[str]:
    """File header comment block + imports."""
    return [
        "# ==============================================================",
        "# Dimensional Chaos — emitted Blender Python",
        f"# mode:    {recipe.mode}",
        f"# palette: {recipe.palette}",
        f"# voice:   {recipe.voice}",
        f"# forces:  {', '.join(recipe.forces)}",
        f"# subject: {recipe.subject or '(none)'}",
        "# ==============================================================",
        "import bpy",
        "import math",
        "from mathutils import Vector",
        "",
    ]


def _scene_reset() -> list[str]:
    """Wipe scene contents without disturbing addons or preferences.

    `bpy.ops.wm.read_factory_settings(use_empty=True)` was the obvious choice
    but it kills addon state — including the Blender MCP socket addon. So we
    do a manual datablock cleanup that leaves the runtime intact.
    """
    return [
        "# clean scene contents (addon state preserved — no factory reset)",
        "for _o in list(bpy.data.objects): bpy.data.objects.remove(_o, do_unlink=True)",
        "for _m in list(bpy.data.meshes): bpy.data.meshes.remove(_m, do_unlink=True)",
        "for _mat in list(bpy.data.materials): bpy.data.materials.remove(_mat, do_unlink=True)",
        "for _lt in list(bpy.data.lights): bpy.data.lights.remove(_lt, do_unlink=True)",
        "for _cm in list(bpy.data.cameras): bpy.data.cameras.remove(_cm, do_unlink=True)",
        "for _wld in list(bpy.data.worlds):",
        "    if _wld.use_nodes: _wld.node_tree.nodes.clear()",
        "",
    ]


def _apply_mode(mode_tokens: dict[str, Any], mode_key: str) -> list[str]:
    """Set render engine, samples, framerate from mode tokens."""
    bl = mode_tokens.get("blender", {}) if isinstance(mode_tokens, dict) else {}
    engine = bl.get("render_engine", "CYCLES")
    samples = int(bl.get("samples", 128))
    fr = bl.get("framerate", 24)
    if isinstance(fr, dict):
        fps = int(fr.get("target_fps", fr.get("fps", 24)))
        frame_step = int(fr.get("step_frames", 1))
    else:
        fps = int(fr)
        frame_step = 1
    out = [
        f"# mode: {mode_key}",
        f"bpy.context.scene.render.engine = '{engine}'",
    ]
    if engine.upper() == "CYCLES":
        out += [
            f"bpy.context.scene.cycles.samples = {samples}",
            "bpy.context.scene.cycles.use_denoising = True",
            "bpy.context.scene.cycles.device = 'GPU'",
        ]
    else:
        out += [
            f"bpy.context.scene.eevee.taa_render_samples = {samples}",
            "if hasattr(bpy.context.scene.eevee, 'use_bloom'): bpy.context.scene.eevee.use_bloom = True",
        ]
    out += [
        f"bpy.context.scene.render.fps = {fps}",
        f"bpy.context.scene.frame_step = {frame_step}",
        "bpy.context.scene.render.resolution_x = 1920",
        "bpy.context.scene.render.resolution_y = 1080",
        "bpy.context.scene.render.film_transparent = False",
        "",
    ]
    return out


def _apply_palette(palette_key: str) -> list[str]:
    """Delegate to rigs.palette_to_rig for world + lighting."""
    return [f"# palette: {palette_key}"] + palette_to_rig(palette_key) + [""]


def _apply_voice(voice_tokens: dict[str, Any], voice_key: str) -> list[str]:
    """Delegate to cameras.add_camera with voice token dict (+ key)."""
    vt = dict(voice_tokens) if isinstance(voice_tokens, dict) else {}
    vt["key"] = voice_key
    return [f"# voice: {voice_key}"] + add_camera(vt) + [""]


def _subject_primitive(mode_key: str, subject: str) -> list[str]:
    """Spawn a hero primitive appropriate to the mode and apply a mode-matched material."""
    factory = mode_to_material_factory(mode_key)
    mat_name = f"DC_{mode_key}_hero"
    lines = [f"# subject: {subject or '(placeholder)'}"]
    lines += factory(mat_name) if factory.__code__.co_argcount == 1 else factory(mat_name)
    subject_lower = (subject or "").lower()
    if "teapot" in subject_lower or mode_key == "hyperreal_chrome":
        lines += [
            "bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0.0, 0.0, 0.6))",
            "_hero = bpy.context.view_layer.objects.active",
            "bpy.ops.object.shade_smooth()",
        ]
    elif mode_key == "liminal_lowpoly":
        lines += [
            "bpy.ops.mesh.primitive_cube_add(size=1.2, location=(0.0, 0.0, 0.6))",
            "_hero = bpy.context.view_layer.objects.active",
            "bpy.ops.object.modifier_add(type='DECIMATE')",
            "_hero.modifiers[-1].ratio = 0.25",
        ]
    elif mode_key == "isometric_diorama":
        lines += [
            "bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=1.0, location=(0.0, 0.0, 0.5))",
            "_hero = bpy.context.view_layer.objects.active",
            "bpy.ops.object.shade_smooth()",
        ]
    elif mode_key == "plushcore_soft":
        lines += [
            "bpy.ops.mesh.primitive_ico_sphere_add(radius=0.55, subdivisions=4, location=(0.0, 0.0, 0.55))",
            "_hero = bpy.context.view_layer.objects.active",
            "bpy.ops.object.modifier_add(type='SUBSURF')",
            "_hero.modifiers[-1].levels = 2",
            "bpy.ops.object.shade_smooth()",
        ]
    elif mode_key == "brutalist_sculpture":
        lines += [
            "bpy.ops.mesh.primitive_cube_add(size=1.6, location=(0.0, 0.0, 0.8))",
            "_hero = bpy.context.view_layer.objects.active",
            "bpy.ops.object.modifier_add(type='BEVEL')",
            "_hero.modifiers[-1].width = 0.02",
        ]
    elif mode_key == "studio_ghibli_nature":
        lines += [
            "bpy.ops.mesh.primitive_ico_sphere_add(radius=0.45, subdivisions=3, location=(0.0, 0.0, 0.5))",
            "_hero = bpy.context.view_layer.objects.active",
            "bpy.ops.object.shade_smooth()",
        ]
    else:
        lines += [
            "bpy.ops.mesh.primitive_monkey_add(size=1.0, location=(0.0, 0.0, 0.6))",
            "_hero = bpy.context.view_layer.objects.active",
            "bpy.ops.object.shade_smooth()",
        ]
    # Ground plane (always — never float the subject in space).
    lines += [
        "bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0.0, 0.0, 0.0))",
        "_ground = bpy.context.view_layer.objects.active",
        "_ground.name = 'DC_Ground'",
        "if len(_ground.data.materials) == 0:",
        "    _ground.data.materials.append(_mat)",
        "_hero.data.materials.clear()",
        "_hero.data.materials.append(_mat)",
        "",
    ]
    return lines


def _apply_forces(forces: list[str], mode_key: str) -> list[str]:
    """Apply per-force scene tweaks (scale, motion, extra lights, etc.)."""
    out: list[str] = [f"# forces: {', '.join(forces)}"]
    if "scale_distortion" in forces:
        out += [
            "# scale_distortion: hero oversized, secondary minis",
            "_hero.scale = (2.0, 2.0, 2.0)",
            "bpy.ops.mesh.primitive_cube_add(size=0.12, location=(1.2, -0.8, 0.06))",
            "bpy.context.view_layer.objects.active.name = 'DC_Mini'",
        ]
    if "light_as_character" in forces:
        out += [
            "# light_as_character: visible volumetric beam",
            "bpy.ops.object.light_add(type='SPOT', location=(-1.5, -2.5, 3.0))",
            "_beam = bpy.context.view_layer.objects.active",
            "_beam.name = 'DC_Beam'",
            "_beam.data.energy = 3000.0",
            "_beam.data.spot_size = 0.6",
            "_beam.data.spot_blend = 0.15",
            "if hasattr(_beam.data, 'use_shadow'): _beam.data.use_shadow = True",
        ]
    if "material_contrast" in forces:
        out += [
            "# material_contrast: add a matte counterpart cube nearby",
            "bpy.ops.mesh.primitive_cube_add(size=0.8, location=(0.9, 0.4, 0.4))",
            "_counter = bpy.context.view_layer.objects.active",
            "_counter.name = 'DC_ContrastMate'",
            "_contrast_mat = bpy.data.materials.new(name='DC_ContrastMatte')",
            "_contrast_mat.use_nodes = True",
            "_cn = _contrast_mat.node_tree.nodes.get('Principled BSDF')",
            "if _cn is not None:",
            "    _cn.inputs['Roughness'].default_value = 0.98",
            "    _cn.inputs['Base Color'].default_value = (0.08, 0.08, 0.09, 1.0)",
            "_counter.data.materials.clear()",
            "_counter.data.materials.append(_contrast_mat)",
        ]
    if "negative_space" in forces:
        out += [
            "# negative_space: push camera back, darken world",
            "if bpy.context.scene.camera is not None:",
            "    bpy.context.scene.camera.location.y -= 1.5",
            "_w = bpy.context.scene.world",
            "if _w and _w.use_nodes:",
            "    for _bn in _w.node_tree.nodes:",
            "        if _bn.type == 'BACKGROUND' and 'Strength' in _bn.inputs:",
            "            _bn.inputs['Strength'].default_value *= 0.6",
        ]
    if "impossible_physics" in forces:
        out += [
            "# impossible_physics: levitate + tilt the hero off its base",
            "_hero.location.z += 0.4",
            "_hero.rotation_euler[0] += 0.35",
            "bpy.ops.object.light_add(type='POINT', location=(0.0, 0.0, 0.15))",
            "_under = bpy.context.view_layer.objects.active",
            "_under.name = 'DC_UnderGlow'",
            "_under.data.energy = 80.0",
            "_under.data.color = (1.0, 0.9, 0.7)",
        ]
    if "hand_evidence" in forces:
        out += [
            "# hand_evidence: add visible imperfection (fingerprint plane above ground)",
            "bpy.ops.mesh.primitive_plane_add(size=0.4, location=(0.2, 0.0, 0.001))",
            "_print = bpy.context.view_layer.objects.active",
            "_print.name = 'DC_Fingerprint'",
            "_pm = bpy.data.materials.new(name='DC_Smudge')",
            "_pm.use_nodes = True",
            "_pnode = _pm.node_tree.nodes.get('Principled BSDF')",
            "if _pnode is not None:",
            "    _pnode.inputs['Roughness'].default_value = 0.35",
            "    _pnode.inputs['Base Color'].default_value = (0.15, 0.15, 0.18, 1.0)",
            "_print.data.materials.clear()",
            "_print.data.materials.append(_pm)",
        ]
    out.append("")
    return out


def _apply_compositor(mode_key: str) -> list[str]:
    """Compositor pass (never skipped)."""
    return [f"# compositor: {mode_key}"] + apply_mode_post(mode_key) + [""]


def _final_render_settings(mode_tokens: dict[str, Any]) -> list[str]:
    """Output path + color management finishing touches."""
    bl = mode_tokens.get("blender", {}) if isinstance(mode_tokens, dict) else {}
    post = bl.get("post", {}) if isinstance(bl, dict) else {}
    if isinstance(post, dict):
        view_transform = post.get("view_transform", "AgX")
    else:
        view_transform = "AgX"
    return [
        "# final render settings",
        "bpy.context.scene.render.image_settings.file_format = 'PNG'",
        "bpy.context.scene.render.image_settings.color_mode = 'RGBA'",
        "bpy.context.scene.render.filepath = '//render/dc_output_'",
        f"try: bpy.context.scene.view_settings.view_transform = '{view_transform}'",
        "except Exception: pass",
        "",
    ]


class Scene:
    """A Recipe + loaded tokens → emitted Blender Python script."""

    def __init__(self, recipe: Recipe, tokens: dict[str, dict[str, Any]] | None = None) -> None:
        recipe.validate()
        self.recipe = recipe
        if tokens is None:
            # Import here to avoid circular import at module load.
            from . import load_tokens

            tokens = load_tokens()
        self.tokens = tokens
        self._assembled: str | None = None

    def _mode_tokens(self) -> dict[str, Any]:
        """Return the mode entry (or empty dict if tokens file absent)."""
        return self.tokens.get("modes", {}).get(self.recipe.mode, {}) or {}

    def _voice_tokens(self) -> dict[str, Any]:
        """Return the voice entry."""
        return self.tokens.get("voices", {}).get(self.recipe.voice, {}) or {}

    def assemble(self) -> str:
        """Compose the complete Blender Python script and cache the string."""
        if self._assembled is not None:
            return self._assembled
        parts: list[str] = []
        parts += _header(self.recipe)
        parts += _scene_reset()
        parts += _apply_mode(self._mode_tokens(), self.recipe.mode)
        parts += _apply_palette(self.recipe.palette)
        parts += _apply_voice(self._voice_tokens(), self.recipe.voice)
        parts += _subject_primitive(self.recipe.mode, self.recipe.subject)
        parts += _apply_forces(self.recipe.forces, self.recipe.mode)
        parts += _apply_compositor(self.recipe.mode)
        parts += _final_render_settings(self._mode_tokens())
        self._assembled = "\n".join(parts) + "\n"
        return self._assembled

    def preview_plan(self) -> dict[str, Any]:
        """Return a human-readable summary of what assemble() will emit."""
        code = self.assemble()
        lines = code.splitlines()
        mt = self._mode_tokens()
        bl = mt.get("blender", {}) if isinstance(mt, dict) else {}
        engine = bl.get("render_engine", "CYCLES")
        samples = int(bl.get("samples", 128))
        estimated = int(samples * (1.2 if engine.upper() == "CYCLES" else 0.4))
        hdri_hint = {
            "golden_hour_valley": "kloppenheim_06_puresky",
            "fog_valley": "kloofendal_misty_morning_puresky",
            "overcast_studio": "studio_small_08",
            "moonlit_concrete": "moonlit_golf",
            "iridescent_candy": "studio_country_hall",
        }.get(self.recipe.palette, None)
        return {
            "mode": self.recipe.mode,
            "palette": self.recipe.palette,
            "voice": self.recipe.voice,
            "forces": list(self.recipe.forces),
            "subject": self.recipe.subject,
            "render_engine": engine,
            "samples": samples,
            "emitted_lines": len(lines),
            "estimated_render_seconds": estimated,
            "hdri_slug": hdri_hint,
            "has_compositor_post": True,
        }


if __name__ == "__main__":
    demo = Recipe(
        mode="hyperreal_chrome",
        palette="iridescent_candy",
        voice="intimate_macro",
        forces=["material_contrast", "light_as_character"],
        subject="chrome teapot on velvet cube",
    )
    scene = Scene(demo)
    print(scene.assemble())
    print("# ---- preview_plan ----")
    print(scene.preview_plan())
