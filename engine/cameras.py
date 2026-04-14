"""Camera rigs per voice — rule-of-thirds default, never center-framed."""
from __future__ import annotations

from typing import Any

# Rule-of-thirds offset on X (subject-world) — pushes subject off-center.
_THIRDS_OFFSET = 0.33


def _emit_base_camera(loc: tuple[float, float, float], rot: tuple[float, float, float]) -> list[str]:
    """Create a camera at loc/rot and set it active."""
    return [
        f"bpy.ops.object.camera_add(location={loc}, rotation={rot})",
        "_cam = bpy.context.object",
        "_cam.name = 'DC_Camera'",
        "bpy.context.scene.camera = _cam",
    ]


def _dof(focus_m: float, fstop: float) -> list[str]:
    """Enable depth-of-field with a given focus distance and f-stop."""
    return [
        "_cam.data.dof.use_dof = True",
        f"_cam.data.dof.focus_distance = {focus_m:.3f}",
        f"_cam.data.dof.aperture_fstop = {fstop:.2f}",
    ]


def _intimate_macro(v: dict[str, Any]) -> list[str]:
    """85mm macro, tight focus, shallow DOF, rule-of-thirds."""
    lens = float(v.get("lens_mm", 85))
    sensor = float(v.get("sensor_mm", 36))
    focus = float(v.get("focus_distance_m", 0.35))
    fstop = float(v.get("aperture", 1.8))
    out = _emit_base_camera((0.55, -0.9, 0.42), (1.25, 0.0, 0.55))
    out += [
        f"_cam.data.lens = {lens:.2f}",
        f"_cam.data.sensor_width = {sensor:.2f}",
        f"_cam.location.x += {_THIRDS_OFFSET}",
    ]
    out += _dof(focus, fstop)
    return out


def _gods_eye_ortho(v: dict[str, Any]) -> list[str]:
    """Top-down orthographic, square framing, scale set for scene."""
    scale = float(v.get("ortho_scale", 5.0))
    out = _emit_base_camera((0.0, 0.0, 8.0), (0.0, 0.0, 0.0))
    out += [
        "_cam.data.type = 'ORTHO'",
        f"_cam.data.ortho_scale = {scale:.3f}",
    ]
    return out


def _architectural_wide(v: dict[str, Any]) -> list[str]:
    """24mm wide, deep DOF, slight elevation."""
    lens = float(v.get("lens_mm", 24))
    sensor = float(v.get("sensor_mm", 36))
    fstop = float(v.get("aperture", 8.0))
    focus = float(v.get("focus_distance_m", 6.0))
    out = _emit_base_camera((-4.5, -6.5, 2.2), (1.37, 0.0, -0.62))
    out += [
        f"_cam.data.lens = {lens:.2f}",
        f"_cam.data.sensor_width = {sensor:.2f}",
    ]
    out += _dof(focus, fstop)
    return out


def _dolly_cinematic(v: dict[str, Any]) -> list[str]:
    """50mm dolly — 120-frame bezier path, camera tracks subject."""
    lens = float(v.get("lens_mm", 50))
    sensor = float(v.get("sensor_mm", 36))
    fstop = float(v.get("aperture", 2.8))
    focus = float(v.get("focus_distance_m", 3.0))
    out = _emit_base_camera((-3.0, -5.5, 1.6), (1.3, 0.0, -0.55))
    out += [
        f"_cam.data.lens = {lens:.2f}",
        f"_cam.data.sensor_width = {sensor:.2f}",
    ]
    out += _dof(focus, fstop)
    out += [
        "# dolly path (bezier curve, 120 frames)",
        "bpy.ops.curve.primitive_bezier_curve_add(location=(0.0, 0.0, 1.6))",
        "_path = bpy.context.object",
        "_path.name = 'DC_DollyPath'",
        "_path.data.path_duration = 120",
        "_path.data.use_path = True",
        "_path.data.bezier_points_radius = 0.0 if False else None",
        "_ptA = _path.data.splines[0].bezier_points[0]",
        "_ptB = _path.data.splines[0].bezier_points[1]",
        "_ptA.co = (-3.5, -5.5, 0.0)",
        "_ptA.handle_left = (-5.0, -5.5, 0.0)",
        "_ptA.handle_right = (-2.0, -5.5, 0.0)",
        "_ptB.co = (2.5, -3.5, 0.0)",
        "_ptB.handle_left = (1.0, -4.5, 0.0)",
        "_ptB.handle_right = (4.0, -2.5, 0.0)",
        "_con = _cam.constraints.new('FOLLOW_PATH')",
        "_con.target = _path",
        "_con.use_curve_follow = True",
        "bpy.context.scene.frame_start = 1",
        "bpy.context.scene.frame_end = 120",
    ]
    return out


def _dutch_drama(v: dict[str, Any]) -> list[str]:
    """35mm tilted roll ~18deg, medium shallow DOF, dramatic angle."""
    lens = float(v.get("lens_mm", 35))
    sensor = float(v.get("sensor_mm", 36))
    fstop = float(v.get("aperture", 2.8))
    focus = float(v.get("focus_distance_m", 2.5))
    roll = float(v.get("dutch_roll_rad", 0.31))
    out = _emit_base_camera((2.5, -4.0, 1.3), (1.30, 0.0, 0.6))
    out += [
        f"_cam.data.lens = {lens:.2f}",
        f"_cam.data.sensor_width = {sensor:.2f}",
        f"_cam.rotation_euler[1] = {roll:.4f}",
    ]
    out += _dof(focus, fstop)
    return out


_VOICE_DISPATCH = {
    "intimate_macro": _intimate_macro,
    "gods_eye_ortho": _gods_eye_ortho,
    "architectural_wide": _architectural_wide,
    "dolly_cinematic": _dolly_cinematic,
    "dutch_drama": _dutch_drama,
}


def add_camera(voice_tokens: dict[str, Any], subject_bbox: tuple[float, float, float] | None = None) -> list[str]:
    """Emit camera setup for a given voice; subject_bbox hints framing distance."""
    name = voice_tokens.get("key") or voice_tokens.get("name") or "intimate_macro"
    fn = _VOICE_DISPATCH.get(name, _intimate_macro)
    lines = fn(voice_tokens)
    if subject_bbox is not None:
        sx, sy, sz = subject_bbox
        lines.append(f"# subject bbox hint: ({sx:.2f}, {sy:.2f}, {sz:.2f})")
    return lines
