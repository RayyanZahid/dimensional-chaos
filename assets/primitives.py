"""Curated Blender primitives for scenes that don't need Meshy generation.

Each entry in PRIMITIVES is a callable that returns a list[str] of Python
lines intended to be executed in Blender's `bpy` environment. The engine
concatenates these and sends them over Blender MCP.

Philosophy: every primitive ships with sane subdivisions, bevels, and
names so it renders cleanly in Cycles/Eevee without post-tweaking. The
comments in each callable explain the AESTHETIC purpose — why this
primitive exists in the design system, not what `bpy.ops` does.
"""


def hero_cube() -> list:
    """Beveled hero cube — the default object of Dimensional Chaos.

    Soft edges catch rim light; subdivided so shaders don't look flat.
    """
    return [
        "import bpy",
        "bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))",
        "obj = bpy.context.active_object",
        "obj.name = 'HeroCube'",
        "# Bevel — the single modifier that makes cubes photographable.",
        "bev = obj.modifiers.new(name='Bevel', type='BEVEL')",
        "bev.width = 0.04",
        "bev.segments = 4",
        "bev.limit_method = 'ANGLE'",
        "# Subsurf for silky shading (2 levels = render-ready, cheap in viewport).",
        "sub = obj.modifiers.new(name='Subdivision', type='SUBSURF')",
        "sub.levels = 1",
        "sub.render_levels = 2",
        "bpy.ops.object.shade_smooth()",
    ]


def hero_sphere() -> list:
    """UV sphere with enough segments to survive macro shots."""
    return [
        "import bpy",
        "bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, segments=64, ring_count=32, location=(0, 0, 0.5))",
        "obj = bpy.context.active_object",
        "obj.name = 'HeroSphere'",
        "# Auto-smooth so equator seams disappear under Cycles denoiser.",
        "bpy.ops.object.shade_smooth()",
        "# Subsurf adds extra density for sharp highlights on chrome / glass shaders.",
        "sub = obj.modifiers.new(name='Subdivision', type='SUBSURF')",
        "sub.levels = 1",
        "sub.render_levels = 2",
    ]


def hero_teapot() -> list:
    """Teapot (via Extra Objects addon) or Suzanne fallback — the 'camera test' object.

    Teapots are the canonical product-photography subject; Suzanne is Blender's
    built-in stand-in if the Extra Objects addon isn't enabled.
    """
    return [
        "import bpy",
        "# Try the classic Utah teapot from Add Mesh Extra Objects; fall back to Suzanne.",
        "try:",
        "    bpy.ops.preferences.addon_enable(module='add_mesh_extra_objects')",
        "    bpy.ops.mesh.primitive_teapot_add(resolution=8, size=0.5, location=(0, 0, 0.3))",
        "except Exception:",
        "    bpy.ops.mesh.primitive_monkey_add(size=0.6, location=(0, 0, 0.5))",
        "obj = bpy.context.active_object",
        "obj.name = 'HeroTeapot'",
        "sub = obj.modifiers.new(name='Subdivision', type='SUBSURF')",
        "sub.levels = 2",
        "sub.render_levels = 3",
        "bpy.ops.object.shade_smooth()",
    ]


def display_pedestal() -> list:
    """Short wide cylinder with a beveled top — museum product pedestal."""
    return [
        "import bpy",
        "bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=0.2, vertices=96, location=(0, 0, 0.1))",
        "obj = bpy.context.active_object",
        "obj.name = 'DisplayPedestal'",
        "# Soft chamfer on the top/bottom edges — product photography needs this.",
        "bev = obj.modifiers.new(name='Bevel', type='BEVEL')",
        "bev.width = 0.015",
        "bev.segments = 6",
        "bpy.ops.object.shade_smooth()",
        "# Smooth only the curved sides; keep top/bottom crisp.",
        "bpy.ops.object.shade_auto_smooth(angle=1.047)",
    ]


def velvet_cube() -> list:
    """Heavily beveled cube meant to carry a velvet/fabric sheen shader.

    Subsurf density is higher than hero_cube so cloth shaders (with sheen
    falloff) modulate smoothly across the surface.
    """
    return [
        "import bpy",
        "bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))",
        "obj = bpy.context.active_object",
        "obj.name = 'VelvetCube'",
        "# Wider bevel to simulate stuffed / padded corners.",
        "bev = obj.modifiers.new(name='Bevel', type='BEVEL')",
        "bev.width = 0.08",
        "bev.segments = 8",
        "# Denser subsurf = velvet sheen rolls across the form.",
        "sub = obj.modifiers.new(name='Subdivision', type='SUBSURF')",
        "sub.levels = 2",
        "sub.render_levels = 3",
        "bpy.ops.object.shade_smooth()",
    ]


def infinity_curve() -> list:
    """Plane bent upward at the back — infinity backdrop for studio shots.

    This is the 'no horizon' look: a seamless sweep where floor meets wall.
    """
    return [
        "import bpy",
        "bpy.ops.mesh.primitive_plane_add(size=6.0, location=(0, 1.5, 0))",
        "obj = bpy.context.active_object",
        "obj.name = 'InfinityCurve'",
        "# Dense subdivisions so the bend modifier curves smoothly.",
        "sub = obj.modifiers.new(name='Subdivision', type='SUBSURF')",
        "sub.subdivision_type = 'SIMPLE'",
        "sub.levels = 4",
        "sub.render_levels = 5",
        "# Bend the back edge upward 90deg — instant cyclorama.",
        "bend = obj.modifiers.new(name='Bend', type='SIMPLE_DEFORM')",
        "bend.deform_method = 'BEND'",
        "bend.angle = 1.5708",
        "bend.deform_axis = 'X'",
        "bpy.ops.object.shade_smooth()",
    ]


def monolith_slab() -> list:
    """Tall thin cube — the 2001: A Space Odyssey proportions (1:4:9)."""
    return [
        "import bpy",
        "bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.0))",
        "obj = bpy.context.active_object",
        "obj.name = 'Monolith'",
        "# Kubrick ratio 1:4:9 — uncannily tall, thin, imposing.",
        "obj.scale = (0.2, 0.8, 1.8)",
        "bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)",
        "# Tiny bevel so edges catch a single specular line, nothing more.",
        "bev = obj.modifiers.new(name='Bevel', type='BEVEL')",
        "bev.width = 0.005",
        "bev.segments = 2",
        "bpy.ops.object.shade_smooth()",
    ]


def grass_patch() -> list:
    """Plane with a hair particle emitter — instant grass field.

    Defaults are minimal; the shader side (ground color + tip color) is
    left to the material system. This primitive is about geometry only.
    """
    return [
        "import bpy",
        "bpy.ops.mesh.primitive_plane_add(size=4.0, location=(0, 0, 0))",
        "obj = bpy.context.active_object",
        "obj.name = 'GrassPatch'",
        "# Hair particle system — each strand is a single-segment hair curve.",
        "psys = obj.modifiers.new(name='Grass', type='PARTICLE_SYSTEM').particle_system",
        "settings = psys.settings",
        "settings.type = 'HAIR'",
        "settings.count = 20000",
        "settings.hair_length = 0.15",
        "settings.child_type = 'SIMPLE'",
        "settings.rendered_child_count = 40",
        "settings.child_length = 0.6",
        "# Jitter the roots so the field doesn't look gridded.",
        "settings.use_rotations = True",
        "settings.rotation_mode = 'NOR_TAN'",
    ]


def fog_volume() -> list:
    """Cube with a Volume Principled shader — atmospheric god-rays / mist.

    Density is intentionally low; volumetrics punch hard in Cycles so a little
    goes a long way. Scale the cube to cover your scene, not the camera frustum.
    """
    return [
        "import bpy",
        "bpy.ops.mesh.primitive_cube_add(size=10.0, location=(0, 0, 2.5))",
        "obj = bpy.context.active_object",
        "obj.name = 'FogVolume'",
        "# Material with ONLY a Volume output — no surface shader so rays pass through.",
        "mat = bpy.data.materials.new(name='FogVolumeMat')",
        "mat.use_nodes = True",
        "nt = mat.node_tree",
        "for n in list(nt.nodes):",
        "    nt.nodes.remove(n)",
        "out = nt.nodes.new('ShaderNodeOutputMaterial')",
        "vol = nt.nodes.new('ShaderNodeVolumePrincipled')",
        "vol.inputs['Density'].default_value = 0.02",
        "vol.inputs['Anisotropy'].default_value = 0.3",
        "nt.links.new(vol.outputs['Volume'], out.inputs['Volume'])",
        "obj.data.materials.append(mat)",
    ]


PRIMITIVES = {
    "hero_cube": hero_cube,
    "hero_sphere": hero_sphere,
    "hero_teapot": hero_teapot,
    "display_pedestal": display_pedestal,
    "velvet_cube": velvet_cube,
    "infinity_curve": infinity_curve,
    "monolith_slab": monolith_slab,
    "grass_patch": grass_patch,
    "fog_volume": fog_volume,
}
