# Dimensional Chaos

**Controlled Chaos, one axis deeper.**

Dimensional Chaos is an AI-first design system for 3D scenes in Blender. Where AI-generated Blender scenes look like cube-on-a-plane, Dimensional Chaos bakes in taste: a four-axis aesthetic DNA — 7 modes × 8 palettes × 5 camera voices × 6 creative forces — that compiles into Blender Python via MCP.

---

## Table of Contents

- [Why This Exists](#why-this-exists)
- [Quickstart](#quickstart)
- [Installation](#installation)
- [Requirements](#requirements)
- [Agent Instructions](#agent-instructions)
- [Human Guide](#human-guide)
  - [Modes](#modes)
  - [Palettes](#palettes)
  - [Voices](#voices)
  - [Forces](#forces)
- [Example Recipes](#example-recipes)
- [Architecture](#architecture)
- [Integration Targets](#integration-targets)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Why This Exists

Blender MCP is just a Python-eval bus. It has no opinions on composition, lighting, or camera. Point an LLM at it and you get a grey cube on a white plane. Every time.

That is the gap. Dimensional Chaos is the taste engine that sits on top.

The grammar is simple:

```
1 Mode + 1 Palette + 1 Voice + 2–3 Forces = one scene recipe.
```

Modes are aesthetic DNA (claymation, ghibli, brutalist, plushcore, chrome, liminal, isometric). Palettes are color + light temperature. Voices are camera behavior. Forces are the tension the scene is actually about.

Pick four things. Get a scene.

---

## Quickstart

**Python API:**

```python
from engine import Recipe, Scene

recipe = Recipe(
    mode="hyperreal_chrome",
    palette="iridescent_candy",
    voice="intimate_macro",
    forces=["material_contrast", "light_as_character"],
    subject="a teapot",
)
code = Scene(recipe).assemble()
# code is a Blender Python string — pipe to MCP execute_blender_code
```

**CLI:**

```bash
python -m dimensional_chaos render \
    --mode hyperreal_chrome \
    --palette iridescent_candy \
    --voice intimate_macro \
    --forces material_contrast,light_as_character \
    --subject "a teapot"
```

**Claude skill:**

```
/dimensional make a hero shot of a chrome teapot, candy palette, macro lens
```

The skill parses intent, picks any unspecified axes, assembles the Blender Python, pipes it to `execute_blender_code` via Blender MCP, and renders a preview.

---

## Installation

```bash
git clone https://github.com/RayyanZahid/dimensional-chaos.git
cd dimensional-chaos
pip install -e .
```

Optional — install as a Claude skill:

```bash
cp -r . ~/.claude/skills/dimensional-chaos
```

The skill becomes available as `/dimensional` in any Claude Code session.

---

## Requirements

- **Python 3.10+**
- **Blender 4.x** (4.0 or newer; tested on 4.2)
- **blender-mcp addon** — either:
  - Community: [`ahujasid/blender-mcp`](https://github.com/ahujasid/blender-mcp)
  - Official: [`blender.org/lab/blender_mcp`](https://projects.blender.org/blender/blender-addons/src/branch/main)
- **Optional:** Meshy API key (for generative geometry via Nano Banana)
- **Optional:** Poly Haven access (HDRIs are fetched through MCP; no key needed if the addon is bridged)

---

## AGENT INSTRUCTIONS

This section is for Claude, Cursor, or any LLM driving the engine.

**When invoked, do this:**

1. **Parse the user's natural-language request** into the four axes:
   - `mode` — the aesthetic DNA
   - `palette` — the color + light story
   - `voice` — the camera's personality
   - `forces` — 2-3 tensions the scene is about
   - `subject` — the literal thing being rendered

2. **If any axis is unspecified**, pick the most apt. Warn the user which you picked and why. Example:
   > "You said 'chrome teapot.' I picked `hyperreal_chrome` + `iridescent_candy` + `intimate_macro` + `[material_contrast, light_as_character]`. Swap any axis with `--mode X` etc."

3. **Construct the recipe:**
   ```python
   from engine import Recipe, Scene
   recipe = Recipe(mode=..., palette=..., voice=..., forces=[...], subject=...)
   ```

4. **Assemble:**
   ```python
   code = Scene(recipe).assemble()
   ```
   This returns a Blender Python string. It resets the scene, sets the HDRI, builds the camera rig, applies materials, and adds the post-process pass.

5. **Execute via MCP:**
   Call the `execute_blender_code` tool with `code` as the argument. Wait for success.

6. **Render preview:**
   Call the `render_thumbnail` MCP tool. Return the image.

7. **Show the user:**
   - The full recipe (all four axes + subject)
   - The preview image
   - Two or three knobs they could turn to iterate

**Never skip the reset.** Every assembled scene starts with `bpy.ops.wm.read_factory_settings(use_empty=True)` so state doesn't leak between renders.

**Never pick two forces that collapse onto the same tension.** `negative_space` + `scale_distortion` is a great pairing. `hand_evidence` + `impossible_physics` fights itself.

**Always include the mode's `discord_ingredient`.** Every mode in `tokens/modes.yaml` declares one element that defies the aesthetic — the plushcore scene needs one sharp edge; the brutalist scene needs one living thing. Without it the render is a mood board, not a scene.

---

## HUMAN GUIDE

Four reference tables. Skim for vocabulary, then combine.

### Modes

| Key | Name | DNA | When to use | Reference |
|---|---|---|---|---|
| `claymation_warmth` | Claymation Warmth | Handmade, fingerprinted, fuzzy edges, warm key | Indie game hero, storybook cover, founder portrait | Aardman, Laika |
| `studio_ghibli_nature` | Studio Ghibli Nature | Soft gradients, wind, wet leaves, atmospheric perspective | Portfolio intro, essay header, nostalgia piece | Miyazaki, Yoshida |
| `brutalist_sculpture` | Brutalist Sculpture | Monolith geometry, raw concrete, long shadows, anti-gravity composition | Case study cover, B2B hero, architecture deck | Goldfinger, Tange |
| `plushcore_soft` | Plushcore Soft | Felt-wrapped props, subsurface scattering, round corners, pastel wash | Consumer product, kids brand, Gen Z launch | Jelly Cat, softcore TikTok |
| `hyperreal_chrome` | Hyperreal Chrome | Mirror metal, caustics, anisotropic highlights, studio rig | Tech launch, crypto brand, luxury render | Beeple, Ian Spriggs |
| `liminal_lowpoly` | Liminal Lowpoly | Untextured, flat-shaded, repeating rooms, no people | Backrooms loop, essay middle, ambient horror | Kane Pixels, PS1 era |
| `isometric_diorama` | Isometric Diorama | Orthographic 30-degree, cutaway walls, tiny people, chamfered edges | Explainer, onboarding flow, city-sim header | Monument Valley, Townscaper |

### Palettes

| Key | Name | Kelvin | Hues | HDRI slug |
|---|---|---|---|---|
| `golden_hour_valley` | Golden Hour Valley | 3200K key, 5600K fill | amber, peach, olive, dust | `venice_sunset` |
| `neon_nightmare` | Neon Nightmare | 2000K ambient, 9000K accent | magenta, cyan, violet, black | `neon_photostudio` |
| `fog_valley` | Fog Valley | 5000K diffuse | cold grey, sage, bone, mint | `rogland_clear_night` |
| `overcast_studio` | Overcast Studio | 6500K flat | bone, chalk, warm grey, cream | `studio_small_09` |
| `sodium_vapor_liminal` | Sodium Vapor Liminal | 2200K only | orange-yellow, carpet brown, fluoro green exit sign | `parking_garage` |
| `moonlit_concrete` | Moonlit Concrete | 4100K | slate, navy, cool white, graphite | `moonless_golf` |
| `iridescent_candy` | Iridescent Candy | 5600K key + rim | pink, mint, lavender, chrome | `studio_small_03` |
| `bruised_sunset` | Bruised Sunset | 2800K | plum, rust, coral, smoke | `kloppenheim_06` |

### Voices

| Key | Lens | Aperture | Framing | When to use |
|---|---|---|---|---|
| `intimate_macro` | 85mm | f/1.4 | Subject fills 60%, shallow DOF | Product, portrait, hero ingredient |
| `gods_eye_ortho` | Ortho | n/a | Top-down, parallel lines | Map, diagram, flat-lay |
| `architectural_wide` | 24mm | f/5.6 | Low horizon, subject small in frame | Environment, scale, brutalism |
| `dolly_cinematic` | 50mm | f/2.8 | Slight push-in, rule-of-thirds | Narrative intro, portfolio hero |
| `dutch_drama` | 35mm | f/2.0 | 8-12° tilt, off-axis | Tension, action, deliberate unease |

### Forces

| Key | Tension | Example hook | Compatible modes |
|---|---|---|---|
| `scale_distortion` | Small thing huge, huge thing small | Teacup the size of a building | ghibli, isometric, brutalist |
| `light_as_character` | The light arrives before the subject | A single shaft hits the object | all |
| `material_contrast` | Two materials that shouldn't touch | Chrome wrapped in felt | chrome, plushcore, claymation |
| `negative_space` | 70% of the frame is empty | Lonely object in vast field | brutalist, liminal, ghibli |
| `impossible_physics` | Something defies gravity, scale, or optics | Liquid holding its shape mid-air | chrome, plushcore, lowpoly |
| `hand_evidence` | A fingerprint, a seam, a smudge | Visible sculpt marks on the form | claymation, plushcore, liminal |

---

## Example Recipes

**SF Startup Hero**
```
mode:    hyperreal_chrome
palette: iridescent_candy
voice:   intimate_macro
forces:  [material_contrast, light_as_character]
subject: product render for a devtools launch
```

**Ghibli Portfolio Intro**
```
mode:    studio_ghibli_nature
palette: fog_valley
voice:   dolly_cinematic
forces:  [scale_distortion, light_as_character]
subject: a lone figure on a mossy hill, wind in grass
```

**Brutalist Case Study Cover**
```
mode:    brutalist_sculpture
palette: moonlit_concrete
voice:   architectural_wide
forces:  [negative_space, light_as_character]
subject: a single concrete monolith at dawn
```

**Liminal Backrooms Loop**
```
mode:    liminal_lowpoly
palette: sodium_vapor_liminal
voice:   architectural_wide
forces:  [negative_space, hand_evidence]
subject: an empty office hallway, yellow carpet
```

**Plushcore Product Card**
```
mode:    plushcore_soft
palette: overcast_studio
voice:   intimate_macro
forces:  [material_contrast, hand_evidence]
subject: a felt-wrapped phone on a soft pedestal
```

---

## Architecture

```
user intent → [recipe parser] → Recipe(mode, palette, voice, forces, subject)
                                    ↓
             [engine/assembler] ── reads tokens/*.yaml
                  ↓
             [rigs + cameras + materials + compositor]
                  ↓
             Blender Python string
                  ↓
             [MCP execute_blender_code] → Blender → render
```

The assembler is a pure function: recipe in, Blender Python out. No side effects. All state lives in the Blender instance the MCP call targets. That means every render is reproducible from a recipe dict alone.

---

## Integration Targets

- **Blender MCP** — both the community [`ahujasid/blender-mcp`](https://github.com/ahujasid/blender-mcp) and the official [`blender.org/lab/blender_mcp`](https://projects.blender.org/blender/blender-addons/src/branch/main) are supported. The assembler emits standard Blender Python (`bpy`), so any bridge that exposes `execute_blender_code` will work.
- **Meshy API** — generative geometry. When a recipe's subject can't be modeled from primitives, the assembler can call Meshy's text-to-3D and import the GLB.
- **Poly Haven** — HDRIs for every palette. Slugs are in `tokens/palettes.yaml`. The MCP addon fetches them at render time.
- **Nano Banana** — called through Meshy for stylized texture generation when a mode needs hand-painted surfaces (claymation, plushcore).

---

## Project Structure

```
dimensional-chaos/
├── README.md              # You are here
├── AXIOMS.md              # First principles
├── DESIGN.md              # Extended philosophy
├── CLAUDE.md              # Agent skill contract
├── LICENSE                # Creative commons
├── pyproject.toml         # Packaging
├── .gitignore
├── engine/                # Assembler, recipe parser, CLI
│   ├── __init__.py
│   ├── __main__.py        # CLI entry
│   ├── recipe.py
│   ├── scene.py
│   ├── rigs.py
│   ├── materials.py
│   └── compositor.py
├── tokens/                # YAML aesthetic data
│   ├── modes.yaml
│   ├── palettes.yaml
│   ├── voices.yaml
│   └── forces.yaml
├── assets/                # Reference images, texture samples
├── showcase/              # Example .blend files + renders
├── render/                # Output directory (gitignored)
└── docs/                  # Extended reference
```

---

## Contributing

### Adding a Mode

Modes live in `tokens/modes.yaml`. A new mode needs:

- `key` — snake_case identifier
- `name` — display name
- `dna` — 3-5 sentence aesthetic brief
- `blender_fingerprint` — the technical moves that make it this mode and not another
- `discord_ingredient` — the one element that defies the aesthetic
- `render_engine` — `CYCLES` or `BLENDER_EEVEE_NEXT`
- `references` — 2-3 artists or films

A mode is not a preset. It is a committed set of choices. If your proposed mode is within 10% of an existing one, don't add it — push the existing one harder.

### Adding a Palette

Palettes live in `tokens/palettes.yaml`. A new palette needs:

- `key`, `name`
- `kelvin` — the light temperature story (key + fill, or single-source)
- `hues` — 4 colors as hex, ordered: dominant, secondary, accent, pitblack
- `hdri_slug` — a real Poly Haven asset
- `mood_reference` — one film or photographer

No palette is allowed to be "moody blue." Name the mood.

### Adding a Voice

Voices live in `tokens/voices.yaml`. A new voice needs:

- `key`, `name`
- `lens_mm` (or `ortho: true`)
- `aperture`
- `framing_rule` — a sentence about where the subject sits
- `movement` — static, push-in, dolly, tilt
- `when_to_use` — the 1-sentence pitch

Five voices is enough. Propose a sixth only if it covers a framing the current five cannot.

### Adding a Force

Forces live in `tokens/forces.yaml`. A new force needs:

- `key`, `name`
- `tension` — the single sentence naming what the force does
- `blender_hook` — the technical move (modifier, light setup, geometry trick)
- `overuse_failure_mode` — what the render looks like when the force is cranked past 100%
- `compatible_modes` — the modes this force lives inside without collapsing

A force that is compatible with all modes is probably a rule, not a force. Push back.

---

## License

Creative commons. Build fearlessly. The scene is not a stage.
