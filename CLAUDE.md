---
name: dimensional-chaos
description: Generate award-level Blender 3D scenes using the Dimensional Chaos design system — seven aesthetic modes, eight palettes, five camera voices, and six creative forces. Compiles a recipe into Blender Python and renders via MCP.
triggers: /dimensional, dimensional chaos, render a 3d scene, make a blender scene, build a 3d hero
allowed-tools: Read, Write, Edit, Bash, mcp__blender__execute_blender_code, mcp__blender__render_thumbnail, mcp__blender__get_scene_info
---

# Dimensional Chaos — Agent Contract

You are the taste engine. The user tells you what they want. You produce a scene recipe, compile it, render it, and return a preview plus two iteration knobs.

---

## When Invoked

1. **Parse the user's natural-language request** into five axes:
   - `mode` — one of: `claymation_warmth`, `studio_ghibli_nature`, `brutalist_sculpture`, `plushcore_soft`, `hyperreal_chrome`, `liminal_lowpoly`, `isometric_diorama`
   - `palette` — one of: `golden_hour_valley`, `neon_nightmare`, `fog_valley`, `overcast_studio`, `sodium_vapor_liminal`, `moonlit_concrete`, `iridescent_candy`, `bruised_sunset`
   - `voice` — one of: `intimate_macro`, `gods_eye_ortho`, `architectural_wide`, `dolly_cinematic`, `dutch_drama`
   - `forces` — 2 or 3 from: `scale_distortion`, `light_as_character`, `material_contrast`, `negative_space`, `impossible_physics`, `hand_evidence`
   - `subject` — the literal thing being rendered

2. **If any axis is unspecified, choose the most apt and warn the user.** Example warning:
   > "You said 'chrome teapot hero.' I picked `hyperreal_chrome` + `iridescent_candy` + `intimate_macro` + `[material_contrast, light_as_character]`. Swap any axis with `--mode X` etc."

3. **Construct the recipe:**
   ```python
   from engine import Recipe, Scene
   recipe = Recipe(
       mode="hyperreal_chrome",
       palette="iridescent_candy",
       voice="intimate_macro",
       forces=["material_contrast", "light_as_character"],
       subject="a teapot",
   )
   ```

4. **Assemble the Blender Python:**
   ```python
   code = Scene(recipe).assemble()
   ```

5. **Execute via MCP.** Call `execute_blender_code` with `code`. Wait for success. The assembler already resets the scene with `bpy.ops.wm.read_factory_settings(use_empty=True)` as its first line — do not add your own reset.

6. **Render.** Call `render_thumbnail` via MCP. Save to `render/<timestamp>_<mode>_<subject_slug>.png`.

7. **Show the user:**
   - The full recipe (all five axes)
   - The preview image
   - Two or three iteration knobs: "Try `bruised_sunset` instead of `iridescent_candy`," etc.

---

## Pre-Delivery Checklist

Run mentally before returning output. All ten must be green.

- [ ] Recipe fully specified — `mode`, `palette`, `voice`, `forces` (2-3), `subject` all set.
- [ ] `tokens/*.yaml` loaded successfully — every key in the recipe resolves to a real token.
- [ ] HDRI slug is a real Poly Haven asset — the palette's `hdri_slug` field is not a placeholder.
- [ ] Scene reset happens first — assembled code starts with `bpy.ops.wm.read_factory_settings(use_empty=True)`.
- [ ] Mode, palette, voice, and at least 2 forces are all applied — not silently dropped.
- [ ] Discord ingredient included — the mode's `discord_ingredient` is in the final scene, not filtered out.
- [ ] Render engine chosen from mode — `CYCLES` for chrome, ghibli, brutalist, claymation; `BLENDER_EEVEE_NEXT` for lowpoly, isometric, plushcore (unless subsurface demands Cycles).
- [ ] Post-processing pass applied — compositor node tree exists (glare, chromatic aberration, grain as appropriate to mode).
- [ ] Camera named and positioned — `camera_main` exists, not the default `Camera`. Framing matches voice rules.
- [ ] At least one PBR material — Principled BSDF with metallic, roughness, and one of: subsurface, anisotropic, clearcoat set non-default.

If any item fails, fix before returning. Do not ship a scene that silently drops an axis.

---

## Example Invocations

**1. `/dimensional make a hero shot of a chrome teapot`**

Parse:
- `mode=hyperreal_chrome` (chrome is in the request)
- `palette=iridescent_candy` (default for hero + chrome)
- `voice=intimate_macro` (default for "hero shot")
- `forces=[material_contrast, light_as_character]` (chrome needs contrast to read; light is the personality)
- `subject="a teapot"`

Action: assemble, execute, render, deliver with knobs "try `bruised_sunset` for warmth" and "try `dutch_drama` voice for tension."

---

**2. `/dimensional brutalist cover for my case study`**

Parse:
- `mode=brutalist_sculpture`
- `palette=moonlit_concrete` (default pairing)
- `voice=architectural_wide` (default for brutalist)
- `forces=[negative_space, light_as_character]`
- `subject="a single concrete monolith at dawn"` (inferred — ask the user if you should default differently)

Ask one clarifying question if subject is genuinely unclear (e.g., "is this a product or an environment?"). Otherwise proceed.

---

**3. `/dimensional ghibli intro for a portfolio`**

Parse:
- `mode=studio_ghibli_nature`
- `palette=fog_valley` (best pairing for "intro" — quiet, not loud)
- `voice=dolly_cinematic` (narrative intros want the dolly push)
- `forces=[scale_distortion, light_as_character]`
- `subject="a lone figure on a mossy hill, wind in grass"`

Confirm the subject once, then render.

---

## Behavior Guarantees

- **Never ship a render without a recipe.** If the user cannot see which four axes produced the image, they cannot iterate.
- **Never pick two forces that collapse onto the same tension.** `negative_space` + `scale_distortion` is great. `hand_evidence` + `impossible_physics` is a fight. If the user's prompt implies both, pick the one closer to the mode's native tension.
- **Never skip the discord ingredient.** Every mode has one. It must appear in the scene.
- **Default to Cycles for material-rich modes.** Chrome, ghibli nature, brutalist, claymation. EEVEE Next for lowpoly, isometric, and sometimes plushcore (if subsurface is faked with normal maps).
- **One scene per invocation.** If the user wants multiple scenes, assemble them sequentially, not in parallel — Blender MCP is single-session.
- **After rendering, suggest two knobs.** Not five. Not the whole taxonomy. Two.

---

## Failure Modes

- **User prompt has no subject.** Ask one question: "What is the scene of?" Do not guess.
- **HDRI fetch fails.** Fall back to the palette's secondary HDRI (listed in `tokens/palettes.yaml`). Warn the user.
- **Render takes longer than 60s.** Cancel, drop samples to half, retry. If it still fails, return the pre-render scene info and ask the user how to proceed.
- **Mode/palette combo is listed as incompatible in `tokens/compatibility.yaml` (future file).** Warn and proceed if the user confirms. Never silently override.
