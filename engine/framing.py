"""Spatial-awareness framing — bbox-aware camera fitter.

Closes the gap between aesthetic taste (palette, mode) and spatial taste
(composition, scale). Engine assembler calls these emits as the last step
before the compositor pass. Emitted code runs inside Blender via MCP
execute_blender_code, queries the actual subject bbox, then repositions
+ retargets the camera so the subject lands in-frame at the right size.
"""
from __future__ import annotations

from typing import Sequence


# Voice fallback fill ratios (overridden by tokens/voices.yaml.fill_ratio if present)
_VOICE_FILL_FALLBACK = {
    "intimate_macro":      0.7,
    "gods_eye_ortho":      0.6,
    "architectural_wide":  0.30,
    "dolly_cinematic":     0.50,
    "dutch_drama":         0.60,
}

# Force framing modifiers (fallback if tokens/forces.yaml lacks them)
_FORCE_FALLBACK = {
    "negative_space":     {"fill_ratio_mul": 0.40, "add_reference_human": False},
    "scale_distortion":   {"fill_ratio_mul": 0.30, "add_reference_human": True},
    "light_as_character": {"fill_ratio_mul": 1.0,  "add_reference_human": False},
    "material_contrast":  {"fill_ratio_mul": 1.0,  "add_reference_human": False},
    "impossible_physics": {"fill_ratio_mul": 1.0,  "add_reference_human": False},
    "hand_evidence":      {"fill_ratio_mul": 1.0,  "add_reference_human": False},
}


def _names_literal(names: Sequence[str]) -> str:
    """Render a sequence of subject names as a safe Python list literal."""
    cleaned = [str(n).replace("'", "") for n in names if n]
    return "[" + ", ".join("'" + n + "'" for n in cleaned) + "]"


def emit_compute_bbox(subject_names: Sequence[str], min_var: str = "_dc_bb_min", max_var: str = "_dc_bb_max", center_var: str = "_dc_bb_center", size_var: str = "_dc_bb_size") -> list[str]:
    """Emit Python computing world-space bbox of all named objects + descendants."""
    names_lit = _names_literal(subject_names)
    return [
        "# --- bbox: walk subject + descendants, world-space ---",
        "_dc_roots = " + names_lit,
        "_dc_targets = []",
        "for _dc_n in _dc_roots:",
        "    _dc_o = bpy.data.objects.get(_dc_n)",
        "    if _dc_o is None:",
        "        continue",
        "    _dc_targets.append(_dc_o)",
        "    try:",
        "        _dc_targets.extend(list(_dc_o.children_recursive))",
        "    except Exception:",
        "        for _dc_c in list(_dc_o.children):",
        "            _dc_targets.append(_dc_c)",
        "_dc_targets = [_t for _t in _dc_targets if getattr(_t, 'bound_box', None) is not None]",
        "if not _dc_targets:",
        "    raise RuntimeError('DC framing: no subject objects found for ' + str(_dc_roots))",
        "_dc_pts = []",
        "for _dc_t in _dc_targets:",
        "    try:",
        "        _dc_mw = _dc_t.matrix_world",
        "        for _dc_corner in _dc_t.bound_box:",
        "            _dc_pts.append(_dc_mw @ Vector(_dc_corner))",
        "    except Exception:",
        "        continue",
        "if not _dc_pts:",
        "    raise RuntimeError('DC framing: subject has no bound_box corners')",
        f"{min_var} = Vector((min(_p.x for _p in _dc_pts), min(_p.y for _p in _dc_pts), min(_p.z for _p in _dc_pts)))",
        f"{max_var} = Vector((max(_p.x for _p in _dc_pts), max(_p.y for _p in _dc_pts), max(_p.z for _p in _dc_pts)))",
        f"{center_var} = ({min_var} + {max_var}) * 0.5",
        f"{size_var} = {max_var} - {min_var}",
    ]


def emit_normalize_scale(subject_names: Sequence[str], target_max_axis: float = 2.0, anchor: str = "ground") -> list[str]:
    """Emit Python scaling subject so bbox longest axis = target_max_axis meters."""
    names_lit = _names_literal(subject_names)
    anchor_mode = "ground" if anchor == "ground" else "center"
    # Compute bbox at top-level (raises if subject missing — caller guards earlier).
    lines = [
        "# --- normalize: scale subject root to target max-axis ---",
        "_dc_norm_roots = " + names_lit,
        "_dc_norm_root = None",
        "for _dc_nn in _dc_norm_roots:",
        "    _dc_rr = bpy.data.objects.get(_dc_nn)",
        "    if _dc_rr is not None:",
        "        _dc_norm_root = _dc_rr",
        "        break",
        "if _dc_norm_root is None:",
        "    pass  # nothing to normalize",
        "else:",
    ]
    bbox = emit_compute_bbox(subject_names, "_dc_nb_min", "_dc_nb_max", "_dc_nb_center", "_dc_nb_size")
    lines += ["    " + ln for ln in bbox]
    lines += [
        "    _dc_max_axis = max(_dc_nb_size.x, _dc_nb_size.y, _dc_nb_size.z)",
        f"    _dc_target = {float(target_max_axis):.4f}",
        "    if _dc_max_axis > 1e-6:",
        "        _dc_ratio = _dc_target / _dc_max_axis",
        "        if _dc_ratio < 0.8 or _dc_ratio > 1.2:",
        "            _dc_cur = _dc_norm_root.scale.copy()",
        "            _dc_norm_root.scale = (_dc_cur.x * _dc_ratio, _dc_cur.y * _dc_ratio, _dc_cur.z * _dc_ratio)",
        "            try: bpy.context.view_layer.update()",
        "            except Exception: pass",
    ]
    if anchor_mode == "ground":
        lines += [
            "            try:",
            "                _dc_norm_root.location.z += _dc_nb_min.z - (_dc_nb_min.z * _dc_ratio)",
            "            except Exception: pass",
        ]
    else:
        lines += [
            "            try:",
            "                _dc_norm_root.location.x += _dc_nb_center.x * (1.0 - _dc_ratio)",
            "                _dc_norm_root.location.y += _dc_nb_center.y * (1.0 - _dc_ratio)",
            "            except Exception: pass",
        ]
    return lines


def emit_fit_camera(camera_name: str, subject_names: Sequence[str], fill_ratio: float = 0.5, rule_of_thirds_x: float = 0.0, voice_position_hint: tuple[float, float, float] | None = None, track_to: bool = True) -> list[str]:
    """Emit Python that fits camera distance + adds a Track-To empty on the subject."""
    cam_name_safe = str(camera_name).replace("'", "")
    fr = max(0.05, min(0.98, float(fill_ratio)))
    rot_x = float(rule_of_thirds_x)
    lines = [
        "# --- fit camera to subject bbox at fill_ratio " + f"{fr:.3f}" + " ---",
        "_dc_cam = bpy.data.objects.get('" + cam_name_safe + "')",
        "if _dc_cam is None:",
        "    _dc_cam = bpy.context.scene.camera",
        "if _dc_cam is None:",
        "    raise RuntimeError('DC framing: no camera named ' + '" + cam_name_safe + "' + ' and scene.camera is None')",
    ]
    lines += emit_compute_bbox(subject_names, "_dc_fb_min", "_dc_fb_max", "_dc_fb_center", "_dc_fb_size")
    lines += [
        "_dc_max_w = max(_dc_fb_size.x, _dc_fb_size.y, _dc_fb_size.z)",
        "_dc_max_w = max(1e-4, _dc_max_w)",
        f"_dc_fr = {fr:.4f}",
        "_dc_pad = 1.10  # 10% safety padding",
    ]
    if voice_position_hint is not None:
        hx, hy, hz = (float(v) for v in voice_position_hint)
        lines += [
            f"_dc_dir = Vector(({hx:.4f}, {hy:.4f}, {hz:.4f}))",
            "if _dc_dir.length < 1e-6:",
            "    _dc_dir = Vector((0.0, -1.0, 0.3))",
            "_dc_dir.normalize()",
        ]
    else:
        lines += [
            "_dc_cur_vec = _dc_cam.location - _dc_fb_center",
            "if _dc_cur_vec.length < 1e-6:",
            "    _dc_cur_vec = Vector((0.0, -1.0, 0.3))",
            "_dc_dir = _dc_cur_vec.normalized()",
        ]
    lines += [
        "_dc_is_ortho = False",
        "try: _dc_is_ortho = (_dc_cam.data.type == 'ORTHO')",
        "except Exception: _dc_is_ortho = False",
        "if _dc_is_ortho:",
        "    try: _dc_cam.data.ortho_scale = (_dc_max_w / max(0.05, _dc_fr)) * _dc_pad",
        "    except Exception: pass",
        "    _dc_distance = max(_dc_max_w * 3.0, 5.0)",
        "else:",
        "    _dc_lens = 50.0",
        "    _dc_sensor = 36.0",
        "    try:",
        "        _dc_lens = float(_dc_cam.data.lens)",
        "        _dc_sensor = float(_dc_cam.data.sensor_width)",
        "    except Exception: pass",
        "    _dc_lens = max(1.0, _dc_lens)",
        "    _dc_hfov = 2.0 * math.atan(_dc_sensor / (2.0 * _dc_lens))",
        "    _dc_tan = max(1e-4, math.tan(_dc_hfov / 2.0))",
        "    _dc_distance = (_dc_max_w / (2.0 * max(0.05, _dc_fr) * _dc_tan)) * _dc_pad",
        "_dc_new_loc = _dc_fb_center + _dc_dir * _dc_distance",
        "# Underground guard: keep camera above ground at >=40% subject height (or 30cm).",
        "_dc_min_z = max(_dc_fb_max.z * 0.4, 0.3)",
        "if _dc_new_loc.z < _dc_min_z:",
        "    _dc_lift = _dc_min_z - _dc_new_loc.z",
        "    _dc_new_loc = Vector((_dc_new_loc.x, _dc_new_loc.y, _dc_min_z))",
        "    # re-extend slightly so the lifted camera still sees the bbox at fill_ratio",
        "    _dc_planar = Vector((_dc_new_loc.x - _dc_fb_center.x, _dc_new_loc.y - _dc_fb_center.y, 0.0))",
        "    if _dc_planar.length < _dc_distance * 0.7:",
        "        _dc_pl = _dc_planar.normalized() if _dc_planar.length > 1e-6 else Vector((0.6, -0.7, 0.0)).normalized()",
        "        _dc_new_loc = _dc_fb_center + _dc_pl * _dc_distance + Vector((0.0, 0.0, _dc_min_z))",
        "_dc_cam.location = (_dc_new_loc.x, _dc_new_loc.y, _dc_new_loc.z)",
    ]
    if track_to:
        lines += [
            "# --- Track-To empty at bbox center with rule-of-thirds X offset ---",
            f"_dc_rot_x = {rot_x:.4f}",
            "_dc_empty_name = 'DC_FrameTarget'",
            "_dc_empty = bpy.data.objects.get(_dc_empty_name)",
            "if _dc_empty is None:",
            "    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 0.0))",
            "    _dc_empty = bpy.context.view_layer.objects.active",
            "    _dc_empty.name = _dc_empty_name",
            "_dc_empty.location = (_dc_fb_center.x + _dc_rot_x * _dc_fb_size.x, _dc_fb_center.y, _dc_fb_center.z)",
            "_dc_has_trackto = False",
            "for _dc_con in list(_dc_cam.constraints):",
            "    if _dc_con.type == 'TRACK_TO':",
            "        _dc_has_trackto = True",
            "        _dc_con.target = _dc_empty",
            "        break",
            "if not _dc_has_trackto:",
            "    try:",
            "        _dc_tc = _dc_cam.constraints.new('TRACK_TO')",
            "        _dc_tc.target = _dc_empty",
            "        _dc_tc.track_axis = 'TRACK_NEGATIVE_Z'",
            "        _dc_tc.up_axis = 'UP_Y'",
            "    except Exception: pass",
        ]
    return lines


def emit_add_scale_reference(location: tuple[float, float, float] = (1.5, 0.0, 0.0), height_m: float = 1.8, name: str = "DC_ScaleRef") -> list[str]:
    """Emit Python adding a thin tall cylinder as a silhouette scale reference."""
    lx, ly, lz = (float(v) for v in location)
    h = max(0.1, float(height_m))
    n = str(name).replace("'", "")
    cz = lz + h * 0.5
    return [
        "# --- scale reference (human-ish silhouette, not part of subject) ---",
        f"bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth={h:.3f}, location=({lx:.3f}, {ly:.3f}, {cz:.3f}))",
        "_dc_ref = bpy.context.view_layer.objects.active",
        "_dc_ref.name = '" + n + "'",
        "_dc_ref_mat = bpy.data.materials.new(name='" + n + "_mat')",
        "_dc_ref_mat.use_nodes = True",
        "_dc_ref_bsdf = _dc_ref_mat.node_tree.nodes.get('Principled BSDF')",
        "if _dc_ref_bsdf is not None:",
        "    _dc_ref_bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.06, 1.0)",
        "    _dc_ref_bsdf.inputs['Roughness'].default_value = 0.9",
        "    try: _dc_ref_bsdf.inputs['Metallic'].default_value = 0.0",
        "    except Exception: pass",
        "    try: _dc_ref_bsdf.inputs['Emission Strength'].default_value = 0.0",
        "    except Exception: pass",
        "_dc_ref.data.materials.clear()",
        "_dc_ref.data.materials.append(_dc_ref_mat)",
    ]


def _resolve_fill_ratio(voice_key: str, voice_tokens: dict) -> float:
    """Pull fill_ratio from voice tokens, falling back to voices.yaml framing or default table."""
    if isinstance(voice_tokens, dict):
        if "fill_ratio" in voice_tokens:
            try:
                return float(voice_tokens["fill_ratio"])
            except (TypeError, ValueError):
                pass
        framing = voice_tokens.get("framing") if isinstance(voice_tokens.get("framing"), dict) else None
        if framing and "subject_fills_frame_pct" in framing:
            try:
                return float(framing["subject_fills_frame_pct"]) / 100.0
            except (TypeError, ValueError):
                pass
    return float(_VOICE_FILL_FALLBACK.get(voice_key, 0.5))


def _resolve_rot_x(voice_key: str, voice_tokens: dict) -> float:
    """Pull rule-of-thirds X offset from voice tokens (subject_placement_x or placement list)."""
    if isinstance(voice_tokens, dict):
        if "subject_placement_x" in voice_tokens:
            try:
                return float(voice_tokens["subject_placement_x"]) - 0.5
            except (TypeError, ValueError):
                pass
        sp = voice_tokens.get("subject_placement")
        if isinstance(sp, (list, tuple)) and len(sp) >= 1:
            try:
                return float(sp[0]) - 0.5
            except (TypeError, ValueError):
                pass
    return 0.0


def _resolve_track_to(voice_tokens: dict) -> bool:
    """Voices can opt out of track-to with `track_to_default: false`."""
    if isinstance(voice_tokens, dict) and "track_to_default" in voice_tokens:
        return bool(voice_tokens["track_to_default"])
    return True


def _resolve_force_mods(force_keys: Sequence[str], forces_tokens: dict) -> tuple[float, bool]:
    """Combine force framing modifiers: multiply fill_ratio, OR reference-human."""
    mul = 1.0
    ref_human = False
    for fk in force_keys:
        mod = None
        if isinstance(forces_tokens, dict):
            entry = forces_tokens.get(fk)
            if isinstance(entry, dict):
                mod = entry.get("framing_modifier")
        if not isinstance(mod, dict):
            mod = _FORCE_FALLBACK.get(fk, {})
        try:
            mul *= float(mod.get("fill_ratio_mul", 1.0))
        except (TypeError, ValueError):
            pass
        if bool(mod.get("add_reference_human", False)):
            ref_human = True
    return mul, ref_human


def emit_frame_scene(voice_key: str, voice_tokens: dict, force_keys: Sequence[str], forces_tokens: dict, subject_name: str = "DC_Hero", camera_name: str = "DC_Camera", normalize_subject: bool = True) -> list[str]:
    """Top-level orchestrator: bbox + optional normalize + camera fit + optional scale ref."""
    base_fill = _resolve_fill_ratio(voice_key, voice_tokens)
    mul, ref_human = _resolve_force_mods(force_keys, forces_tokens)
    final_fill = max(0.05, min(0.95, base_fill * mul))
    rot_x = _resolve_rot_x(voice_key, voice_tokens)
    track_to = _resolve_track_to(voice_tokens)
    subjects = [subject_name]

    lines: list[str] = [
        "# ==============================================================",
        "# framing pass — bbox-aware camera fit (voice: " + str(voice_key) + ")",
        "# fill_ratio: " + f"{final_fill:.3f}" + " (base " + f"{base_fill:.3f}" + " x force_mul " + f"{mul:.3f}" + ")",
        "# ==============================================================",
    ]
    if normalize_subject:
        lines += emit_normalize_scale(subjects, target_max_axis=2.0, anchor="ground")
        lines.append("")
    lines += emit_fit_camera(
        camera_name=camera_name,
        subject_names=subjects,
        fill_ratio=final_fill,
        rule_of_thirds_x=rot_x,
        voice_position_hint=None,
        track_to=track_to,
    )
    if ref_human:
        lines.append("")
        lines += emit_add_scale_reference(location=(1.6, 0.2, 0.0), height_m=1.8, name="DC_ScaleRef")
    lines.append("")
    return lines


if __name__ == "__main__":
    print("# --- emit_compute_bbox ---")
    print("\n".join(emit_compute_bbox(["DC_Hero"])))
    print("\n# --- emit_normalize_scale ---")
    print("\n".join(emit_normalize_scale(["DC_Hero"])))
    print("\n# --- emit_fit_camera ---")
    print("\n".join(emit_fit_camera("DC_Camera", ["DC_Hero"], 0.5, 0.15, (0.5, -0.8, 0.3), True)))
    print("\n# --- emit_add_scale_reference ---")
    print("\n".join(emit_add_scale_reference()))
    print("\n# --- emit_frame_scene ---")
    print("\n".join(emit_frame_scene(
        "intimate_macro",
        {"framing": {"subject_fills_frame_pct": 70}, "subject_placement": [0.5, 0.55]},
        ["scale_distortion", "light_as_character"],
        {},
    )))
