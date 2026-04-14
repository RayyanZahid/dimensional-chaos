"""Compositor post-processing per mode — never skip post."""
from __future__ import annotations

_COMP_HEADER = [
    "bpy.context.scene.use_nodes = True",
    "_ctree = bpy.context.scene.node_tree",
    "for _n in list(_ctree.nodes):",
    "    _ctree.nodes.remove(_n)",
    "_rl = _ctree.nodes.new('CompositorNodeRLayers')",
    "_comp = _ctree.nodes.new('CompositorNodeComposite')",
    "_viewer = _ctree.nodes.new('CompositorNodeViewer')",
]


def _ghibli_post() -> list[str]:
    """Freestyle line art + soft film curve."""
    return [
        "# ghibli post: freestyle lines + soft curve",
        "bpy.context.scene.render.use_freestyle = True",
        "bpy.context.view_layer.use_freestyle = True",
        "_fs = bpy.context.view_layer.freestyle_settings",
        "if len(_fs.linesets) == 0:",
        "    _fs.linesets.new(name='DC_Ghibli')",
        "_ls = _fs.linesets[0]",
        "_ls.linestyle.thickness = 0.4",
        "_ls.linestyle.color = (0.08, 0.12, 0.10)",
    ] + _COMP_HEADER + [
        "_curve = _ctree.nodes.new('CompositorNodeCurveRGB')",
        "_curve.mapping.curves[3].points.new(0.5, 0.55)",
        "_ctree.links.new(_rl.outputs['Image'], _curve.inputs['Image'])",
        "_ctree.links.new(_curve.outputs['Image'], _comp.inputs['Image'])",
        "_ctree.links.new(_curve.outputs['Image'], _viewer.inputs['Image'])",
    ]


def _claymation_post() -> list[str]:
    """High grain + 12fps step (frame_step=2 on 24fps timeline)."""
    return [
        "# claymation post: heavy grain + stop-motion cadence",
        "bpy.context.scene.frame_step = 2",
        "bpy.context.scene.render.fps = 24",
    ] + _COMP_HEADER + [
        "_lens = _ctree.nodes.new('CompositorNodeLensdist')",
        "_lens.inputs['Dispersion'].default_value = 0.01",
        "_glare = _ctree.nodes.new('CompositorNodeGlare')",
        "_glare.glare_type = 'FOG_GLOW'",
        "_glare.size = 6",
        "_noise = _ctree.nodes.new('CompositorNodeMixRGB')",
        "_noise.blend_type = 'OVERLAY'",
        "_noise.inputs['Fac'].default_value = 0.14",
        "_tex = _ctree.nodes.new('CompositorNodeTexture')",
        "_ctree.links.new(_rl.outputs['Image'], _lens.inputs['Image'])",
        "_ctree.links.new(_lens.outputs['Image'], _glare.inputs['Image'])",
        "_ctree.links.new(_glare.outputs['Image'], _noise.inputs[1])",
        "_ctree.links.new(_tex.outputs['Color'], _noise.inputs[2])",
        "_ctree.links.new(_noise.outputs['Image'], _comp.inputs['Image'])",
    ]


def _hyperreal_post() -> list[str]:
    """High bloom, low grain, High Contrast look."""
    return [
        "# hyperreal_chrome post: bloom + high contrast look",
        "bpy.context.scene.view_settings.look = 'AgX - High Contrast'",
        "try: bpy.context.scene.view_settings.look = 'AgX - High Contrast'\n"
        "except Exception: bpy.context.scene.view_settings.look = 'High Contrast'",
    ] + _COMP_HEADER + [
        "_glare = _ctree.nodes.new('CompositorNodeGlare')",
        "_glare.glare_type = 'BLOOM'",
        "_glare.mix = 0.4",
        "_glare.threshold = 0.85",
        "_ctree.links.new(_rl.outputs['Image'], _glare.inputs['Image'])",
        "_ctree.links.new(_glare.outputs['Image'], _comp.inputs['Image'])",
        "_ctree.links.new(_glare.outputs['Image'], _viewer.inputs['Image'])",
    ]


def _liminal_post() -> list[str]:
    """CRT scanline overlay + heavy vignette."""
    return _COMP_HEADER + [
        "# liminal post: CRT scanlines + heavy vignette",
        "_vig = _ctree.nodes.new('CompositorNodeEllipseMask')",
        "_vig.width = 1.3",
        "_vig.height = 1.3",
        "_vig_blur = _ctree.nodes.new('CompositorNodeBlur')",
        "_vig_blur.size_x = 120",
        "_vig_blur.size_y = 120",
        "_mul = _ctree.nodes.new('CompositorNodeMixRGB')",
        "_mul.blend_type = 'MULTIPLY'",
        "_mul.inputs['Fac'].default_value = 0.75",
        "_scan = _ctree.nodes.new('CompositorNodeMixRGB')",
        "_scan.blend_type = 'OVERLAY'",
        "_scan.inputs['Fac'].default_value = 0.18",
        "_tex = _ctree.nodes.new('CompositorNodeTexture')",
        "_ctree.links.new(_rl.outputs['Image'], _scan.inputs[1])",
        "_ctree.links.new(_tex.outputs['Color'], _scan.inputs[2])",
        "_ctree.links.new(_scan.outputs['Image'], _mul.inputs[1])",
        "_ctree.links.new(_vig.outputs['Mask'], _vig_blur.inputs['Image'])",
        "_ctree.links.new(_vig_blur.outputs['Image'], _mul.inputs[2])",
        "_ctree.links.new(_mul.outputs['Image'], _comp.inputs['Image'])",
    ]


def _brutalist_post() -> list[str]:
    """Push contrast, medium grain, crush blacks."""
    return _COMP_HEADER + [
        "# brutalist post: contrast push + crushed blacks",
        "_curve = _ctree.nodes.new('CompositorNodeCurveRGB')",
        "_curve.mapping.curves[3].points[0].location = (0.05, 0.0)",
        "_curve.mapping.curves[3].points[1].location = (0.95, 1.0)",
        "_mix = _ctree.nodes.new('CompositorNodeMixRGB')",
        "_mix.blend_type = 'OVERLAY'",
        "_mix.inputs['Fac'].default_value = 0.08",
        "_tex = _ctree.nodes.new('CompositorNodeTexture')",
        "_ctree.links.new(_rl.outputs['Image'], _curve.inputs['Image'])",
        "_ctree.links.new(_curve.outputs['Image'], _mix.inputs[1])",
        "_ctree.links.new(_tex.outputs['Color'], _mix.inputs[2])",
        "_ctree.links.new(_mix.outputs['Image'], _comp.inputs['Image'])",
    ]


def _plush_post() -> list[str]:
    """Soft bloom + warm tint."""
    return _COMP_HEADER + [
        "_glare = _ctree.nodes.new('CompositorNodeGlare')",
        "_glare.glare_type = 'FOG_GLOW'",
        "_glare.mix = 0.2",
        "_cb = _ctree.nodes.new('CompositorNodeColorBalance')",
        "_cb.correction_method = 'LIFT_GAMMA_GAIN'",
        "_cb.gain = (1.03, 1.0, 0.98)",
        "_ctree.links.new(_rl.outputs['Image'], _glare.inputs['Image'])",
        "_ctree.links.new(_glare.outputs['Image'], _cb.inputs['Image'])",
        "_ctree.links.new(_cb.outputs['Image'], _comp.inputs['Image'])",
    ]


def _diorama_post() -> list[str]:
    """Subtle DOF-style tilt-shift vibe via slight blur + saturation."""
    return _COMP_HEADER + [
        "_sat = _ctree.nodes.new('CompositorNodeHueSat')",
        "_sat.inputs['Saturation'].default_value = 1.15",
        "_ctree.links.new(_rl.outputs['Image'], _sat.inputs['Image'])",
        "_ctree.links.new(_sat.outputs['Image'], _comp.inputs['Image'])",
    ]


_MODE_POST = {
    "studio_ghibli_nature": _ghibli_post,
    "claymation_warmth": _claymation_post,
    "hyperreal_chrome": _hyperreal_post,
    "liminal_lowpoly": _liminal_post,
    "brutalist_sculpture": _brutalist_post,
    "plushcore_soft": _plush_post,
    "isometric_diorama": _diorama_post,
}


def apply_mode_post(mode_key: str) -> list[str]:
    """Dispatch mode key to its compositor routine."""
    fn = _MODE_POST.get(mode_key, _diorama_post)
    return fn()
