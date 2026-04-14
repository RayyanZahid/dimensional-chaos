# AGENTS.md

Machine-first contract for AI coding agents (Claude, Codex, Cursor, Aider, etc.) working with Dimensional Chaos.

This file is the canonical agent entry point. **Humans: see [README.md](README.md).** **Claude skill: see [CLAUDE.md](CLAUDE.md)** (skill frontmatter + invocation).

---

## Identity

```
name:        dimensional-chaos
purpose:     compile an aesthetic recipe into Blender 4.x Python via MCP
language:    Python 3.10+
repo:        github.com/RayyanZahid/dimensional-chaos
license:     Creative Commons (public domain)
sibling:     github.com/RayyanZahid/controlledchaos (web design system, same pattern)
```

---

## Your Contract When Invoked

Given a natural-language request for a 3D scene, you MUST:

1. **Parse the request into 5 axes.** No silent drops. No hallucinated values.
2. **Fill gaps deterministically.** If an axis is missing, pick from `compatible_*` in tokens and log which axis you chose.
3. **Build a `Recipe`.** Call `recipe.validate()` — it raises on bad keys.
4. **Assemble via `Scene(recipe).assemble()`** — returns a complete Blender Python string.
5. **Execute via MCP `execute_blender_code`** — the string is self-contained and starts with `bpy.ops.wm.read_factory_settings(use_empty=True)`. Do not prepend your own reset.
6. **Render via MCP `render_thumbnail`** — save to `render/<timestamp>_<mode>_<subject_slug>.png`.
7. **Return to the user:** the resolved recipe (all 5 axes), the render, and exactly two iteration knobs.

Never ship a render without its recipe. The user cannot iterate if they cannot see the axes.

---

## Valid Axis Values (exhaustive — do not invent)

### modes (7)
```
claymation_warmth
studio_ghibli_nature
brutalist_sculpture
plushcore_soft
hyperreal_chrome
liminal_lowpoly
isometric_diorama
```

### palettes (8)
```
golden_hour_valley
neon_nightmare
fog_valley
overcast_studio
sodium_vapor_liminal
moonlit_concrete
iridescent_candy
bruised_sunset
```

### voices (5)
```
intimate_macro
gods_eye_ortho
architectural_wide
dolly_cinematic
dutch_drama
```

### forces (6)
```
scale_distortion
light_as_character
material_contrast
negative_space
impossible_physics
hand_evidence
```

**Recipe grammar:** exactly `1 mode + 1 palette + 1 voice + 2..3 forces + subject`.
Force count outside `[1, 4]` raises `ValueError`. Pair 2 forces by default; use 3 only when the mode's `philosophy` explicitly benefits from a third tension.

---

## Python API

```python
from engine import Recipe, Scene, MODES, PALETTES, VOICES, FORCES

recipe = Recipe(
    mode="hyperreal_chrome",
    palette="iridescent_candy",
    voice="intimate_macro",
    forces=["material_contrast", "light_as_character"],
    subject="chrome teapot on velvet cube",
    extras={},  # optional: {"hero_glb": "/path/to/asset.glb"}
)
recipe.validate()                   # raises ValueError on bad keys / bad force count

scene = Scene(recipe)
blender_python = scene.assemble()   # str: complete, self-contained Blender script
plan = scene.preview_plan()         # dict: {mode, palette, voice, forces, hdri_slug, estimated_render_seconds, ...}
```

For asset generation (optional, costs Meshy credits):

```python
from assets import MeshyBridge, PolyHavenBridge, PRIMITIVES

bridge = MeshyBridge()              # reads MESHY_API_KEY env
asset = bridge.generate_asset(
    "chrome teapot on velvet cube, product photography, iridescent thin film"
)
# asset = {"glb_path": "...", "textures": [...], "meshy_task_id": "...", "credits_used": 18}

recipe.extras["hero_glb"] = asset["glb_path"]
```

---

## MCP Tools This System Expects

Order of invocation per scene:

1. (optional) `download_polyhaven_asset(asset_id, asset_type, resolution, file_format)` — preload HDRIs and PBR textures referenced by the recipe. Get the list via `engine.mcp_bridge.suggest_polyhaven_downloads(recipe)` — it returns typed payloads.
2. `execute_blender_code(code)` — pipe in `Scene(recipe).assemble()`.
3. `get_scene_info()` — verify the scene built (optional sanity).
4. `render_thumbnail(...)` — produce the preview image.
5. (optional) `get_viewport_screenshot()` — cheap iteration during editing.

Works with either `ahujasid/blender-mcp` (community) or `blender.org/lab/blender_mcp` (official, 2026-04). Prefer the official one when available — it has safety annotations and API/manual as MCP resources.

---

## Parsing Heuristics (when the user is vague)

| User signal | Default axis pick |
|---|---|
| "hero shot" / "product" | `voice=intimate_macro`, `forces+=light_as_character` |
| "chrome" / "metal" / "product" | `mode=hyperreal_chrome`, `palette=iridescent_candy` |
| "ghibli" / "nature" / "painterly" | `mode=studio_ghibli_nature`, `palette=fog_valley`, `voice=dolly_cinematic` |
| "brutalist" / "architecture" / "concrete" | `mode=brutalist_sculpture`, `palette=moonlit_concrete`, `voice=architectural_wide`, `forces+=negative_space` |
| "plush" / "cozy" / "cute" | `mode=plushcore_soft`, `palette=overcast_studio`, `voice=intimate_macro` |
| "backrooms" / "liminal" / "pool hall" | `mode=liminal_lowpoly`, `palette=sodium_vapor_liminal`, `forces+=hand_evidence` |
| "diorama" / "tiny world" / "isometric" | `mode=isometric_diorama`, `voice=gods_eye_ortho`, `forces+=scale_distortion` |
| "claymation" / "stop-motion" / "plasticine" | `mode=claymation_warmth`, `forces+=hand_evidence` |
| "empty frame" / "minimal" | `forces+=negative_space` |
| "floating" / "impossible" / "dreamlike" | `forces+=impossible_physics` |

If you pick any axis the user did not specify, **announce the pick** in your response ("I chose `X` because Y") and offer a one-line swap.

---

## Pre-Delivery Checklist

Mental pass before returning. All ten must be green.

```
[ ] Recipe fully specified (5 axes, 2-3 forces, subject is a concrete noun phrase)
[ ] tokens/*.yaml loaded; every key resolves
[ ] hdri_slug is a real Poly Haven asset (check palettes.yaml.<palette>.lighting.hdri_slug)
[ ] Assembled code starts with bpy.ops.wm.read_factory_settings(use_empty=True)
[ ] Mode, palette, voice, and >=2 forces all emitted (grep the output for each key)
[ ] Discord ingredient applied (modes.yaml.<mode>.discord_ingredient appears in the scene)
[ ] Render engine matches mode (CYCLES for material-rich modes; EEVEE_NEXT for lowpoly/isometric)
[ ] Compositor pass applied (mode post-processing)
[ ] Camera named "camera_main" and scene.camera set
[ ] >=1 Principled BSDF with non-default metallic, roughness, and one of {subsurface, anisotropic, coat}
```

If anything fails, fix before returning. Never silently drop an axis.

---

## Output Format You Return to the User

```markdown
**Recipe**
- mode: `{mode}`
- palette: `{palette}`
- voice: `{voice}`
- forces: `{forces}`
- subject: `{subject}`

[render.png]

**Iterate**
- Try `{alternative_palette}` for a {adjective} read.
- Try `{alternative_voice}` to push the tension.
```

Exactly two knobs. Not five, not the whole taxonomy. Two.

---

## Failure Modes & Recovery

| Failure | Response |
|---|---|
| User prompt has no subject | Ask exactly one question: "What is the scene of?" Do not guess. |
| `recipe.validate()` raises | Report which axis was invalid, suggest the closest valid key, do not silently substitute. |
| HDRI fetch fails (404 / offline) | Fall back to procedural sky with palette-matched sun strength. Warn the user. |
| `execute_blender_code` times out | Drop Cycles samples by 50% and retry once. If still failing, return `scene.preview_plan()` + ask user how to proceed. |
| Meshy credit exhausted | Fall back to `PRIMITIVES` library (`from assets import PRIMITIVES`). Inform the user of the swap. |
| Mode + palette listed as incompatible | Warn the user, do not silently override. Proceed only on explicit confirmation. |

Do not use destructive fallbacks (deleting the scene, force-pushing, etc.). All recovery is additive.

---

## Invariants

- One scene per invocation. Blender MCP is single-session.
- Two forces is the default. Three is the ceiling for normal use. Four is a debug mode.
- `light_as_character` pairs with every mode. The other five forces have `compatible_modes` and `incompatible_modes` in `tokens/forces.yaml` — respect them.
- Discord is mandatory. Every mode has a `discord_ingredient`. It must appear in the scene.

---

## File Map

```
tokens/           # the soul — YAML DNA (modes, palettes, voices, forces, visual-language)
engine/           # the taste engine — compiles Recipe → Blender Python
  assembler.py    # Recipe, Scene, assemble()
  rigs.py         # lighting rigs per palette
  cameras.py      # camera framing per voice
  materials.py    # shader presets per mode
  compositor.py   # post-processing per mode
  mcp_bridge.py   # suggest_polyhaven_downloads, format_for_mcp
assets/           # pipelines
  meshy_bridge.py # text → Nano Banana → image-to-3D → GLB
  polyhaven.py    # HDRI + PBR via MCP typed tool
  primitives.py   # curated Blender primitives (hero_cube, monolith_slab, ...)
showcase/         # 3 canonical demos
  sf_chrome_hero.py
  ghibli_intro.py
  brutalist_cover.py
AXIOMS.md         # three axioms + five corollaries (first principles)
DESIGN.md         # extended philosophy per mode and per force
CLAUDE.md         # Claude skill frontmatter + invocation
README.md         # human-facing guide
```

---

## Contributing Code (for agents making changes)

- Add a Mode: append to `tokens/modes.yaml` + extend `engine/materials.py` factory + `engine/compositor.py` post + update taxonomy here.
- Add a Palette: append to `tokens/palettes.yaml` with a real Poly Haven HDRI slug + extend `engine/rigs.py` dispatch.
- Add a Voice: append to `tokens/voices.yaml` + extend `engine/cameras.py` dispatch.
- Add a Force: append to `tokens/forces.yaml` with concrete `blender_hooks` + extend assembler's `apply_forces()`.

All new keys must be enumerated in AGENTS.md, CLAUDE.md, and README.md. Taxonomy drift across these three files is the only hard-block bug class.

---

*Creative commons. Build fearlessly. The scene is not a stage.*
