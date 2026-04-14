# Showcase: 3 Canonical Recipes

These are the three reference scenes for **Dimensional Chaos**. Each one pins a
different combination of `mode + palette + voice + forces` so you can see how
the design system composes end-to-end — from Recipe to emitted Blender Python
to a rendered frame.

Treat them as the "try this now" artifacts. Copy a recipe, swap one axis
(e.g. flip palette from `iridescent_candy` to `moonlit_concrete`), and rerun.

| Demo               | Mode                   | Palette             | Voice               | Forces                                    |
|--------------------|------------------------|---------------------|---------------------|-------------------------------------------|
| SF Chrome Hero     | `hyperreal_chrome`     | `iridescent_candy`  | `intimate_macro`    | `material_contrast`, `light_as_character` |
| Ghibli Intro       | `studio_ghibli_nature` | `fog_valley`        | `dolly_cinematic`   | `scale_distortion`, `light_as_character`  |
| Brutalist Cover    | `brutalist_sculpture`  | `moonlit_concrete`  | `architectural_wide`| `negative_space`, `light_as_character`    |

---

## Prereqs

- **Python 3.10+**
- **Dimensional Chaos installed** — from the repo root: `pip install -e .`
- **Blender 4.x** — 4.5 LTS recommended (4.2+ required for the iridescent
  thin-film shader used by `hyperreal_chrome`)
- **One of the following renderers**:
  - *Blender MCP addon* (from [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp)
    or the official `blender.org/lab` build) connected to Claude, OR
  - *Blender CLI* — `blender --background --python <script>`
- **Optional: `MESHY_API_KEY`** env var — required only if you pass
  `--use-meshy` to generate hero assets (costs ~18 credits per asset).
  Without it, the engine falls back to Blender primitives.

---

## Three run modes

Each demo can be driven three ways. Pick whichever matches your workflow.

### 1. Python emit (fastest feedback loop)

```bash
python showcase/sf_chrome_hero.py
```

Writes the Blender script to `render/sf_chrome_hero.py` and prints the plan,
recipe, and next-step commands. No Blender needed to emit — only to render.

Useful flags on every demo:

| Flag                | Effect                                                   |
|---------------------|----------------------------------------------------------|
| `--use-meshy`       | Generate hero asset via Meshy API (~18 credits)          |
| `--output-dir PATH` | Override the default `render/` directory                 |
| `--print-code`      | Echo the emitted Blender Python to stdout after writing  |
| `--still`           | (Ghibli Intro only) emit a single frame, not animation   |

### 2. Blender CLI

After emitting the script:

```bash
blender --background --python render/sf_chrome_hero.py \
    -o render/sf_chrome_hero_# -F PNG -x 1 \
    -f 1
```

For the animated Ghibli Intro, use a sequence render:

```bash
blender --background --python render/ghibli_intro.py \
    -o render/ghibli_intro_#### -F PNG -x 1 \
    -s 1 -e 120 -a
```

### 3. Claude + Blender MCP

Either of these works:

- Slash command: `/dimensional render sf-chrome-hero`
- Manual: open the emitted file, copy its contents, paste into the
  `execute_blender_code` MCP tool.

Claude will orchestrate `download_polyhaven_asset` (for HDRIs), execute the
scene, and trigger the render from within Blender.

---

## Per-demo notes

### SF Chrome Hero — `showcase/sf_chrome_hero.py`

Chrome teapot on a magenta velvet cube. The iridescent thin-film shader
gradients across the teapot; a single rim light acts as a character.

- **Output**: single still frame, 1920x1080
- **Render engine**: Cycles, 256 samples
- **Approx render time**: 30-60 seconds on a modern GPU
- **Meshy**: optional (`--use-meshy`); without it the teapot is a bpy primitive
  with the hero material applied
- **Signature move**: material_contrast — the softness of the velvet sells the
  hardness of the chrome, and vice versa

### Ghibli Intro — `showcase/ghibli_intro.py`

A tiny character pushing through grass that towers over them, mist soaking the
light into volumetric god-rays. 120 frames of slow dolly-in.

- **Output**: 120-frame PNG sequence (or single still with `--still`)
- **Render engine**: Cycles, 256 samples
- **Approx render time**: ~10-15 min/frame → ~20-30 hours full sequence
- **Meshy**: optional; generates a cel-shaded wanderer character
- **Signature move**: scale_distortion — 2mm-thick grass renders as meter-wide
  blades; the camera sits at ankle height
- **Tip**: always run `--still` first to check framing before committing to
  the full animation render

### Brutalist Cover — `showcase/brutalist_cover.py`

One concrete monolith, 70% of the frame deliberately empty, cool moonlight
raking in from camera-left. Case-study cover energy.

- **Output**: single still frame, 1920x1080
- **Render engine**: Cycles, 2048 samples (to resolve concrete microsurface)
- **Approx render time**: 60-90 seconds on a modern GPU
- **Meshy**: optional; generates a board-formed concrete block
- **Signature move**: negative_space — the emptiness is the composition

---

## Gotchas

- **HDRI download**: the first run of any demo fetches a Poly Haven HDRI via
  the Blender MCP `download_polyhaven_asset` tool. Make sure that tool is
  enabled in your MCP config. On CLI-only setups, the engine falls back to a
  bundled studio HDRI in `engine/assets/hdri/`.
- **Meshy credits**: `--use-meshy` costs ~18 credits per asset. Leave it off
  for free runs — the primitives look ~80% as good and render 10x faster.
  Set `MESHY_API_KEY` in your env before passing the flag.
- **Blender version**: tested on Blender 4.2+. The `hyperreal_chrome` mode
  uses a thin-film interference node that was added in 4.2; on older versions
  you'll see a pink "missing shader" material.
- **`execute_blender_code` timeout**: the MCP tool can stall on complex scenes.
  The engine prints a progress marker every ~10 emitted lines so you can see
  where a run hangs. If it does, re-run with the CLI instead of MCP — it has
  no timeout.
- **Render output paths**: Blender interprets `#` as a frame-number placeholder.
  For single frames use one `#` or leave it off; for animations use `####` so
  frame 42 becomes `ghibli_intro_0042.png`.
- **Thin-film on older GPUs**: the iridescent shader can OOM on GPUs with less
  than 6GB VRAM. Drop samples to 128 or switch to CPU render as a fallback.
