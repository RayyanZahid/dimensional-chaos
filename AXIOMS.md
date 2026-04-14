# Axioms

Three axioms. Five corollaries. Everything else is preference.

---

## Axiom I — Light does the acting.

Geometry is the stage. Light is the actor.

An untextured sphere lit by a single raking 2200K sodium lamp is more interesting than a hero-modeled car under flat HDRI. The reason is not aesthetic — it is narrative. Light tells you where to look, how to feel, and whether the scene is safe. Geometry only tells you what is there.

AI-generated Blender scenes fail here first. The LLM spends its budget on modeling — subdivide, bevel, loop-cut — and then lights with a single default lamp at (0, 0, 10). The result is a technical object, not a scene. Nothing is acting.

**In practice:**
- Start every scene with a three-point rig, even if you remove two lights later.
- Name your lights: `key`, `fill`, `rim`, `practical_1`. Unnamed lights become ghosts.
- If the scene has only one light, that light must arrive from a specific direction with a specific color temperature. Not from "above."
- The HDRI is a light, not a backdrop. Pick it before you pick the subject.

---

## Axiom II — Every scene is a tension, not a composition.

Composition is the grammar. Tension is the sentence.

A well-composed scene with no tension is a product shot. A poorly composed scene with tension is a meme. The first is forgotten. The second is shared.

Dimensional Chaos names six tensions as Forces: `scale_distortion`, `light_as_character`, `material_contrast`, `negative_space`, `impossible_physics`, `hand_evidence`. Every recipe picks 2-3. Never zero. Never all six.

If you cannot name the force a scene is built around, the scene is decoration. Decoration is allowed. But don't ship it as design.

**In practice:**
- Before rendering, write the force name in the filename: `chrome_teapot_material_contrast.png`.
- If two forces collapse onto the same idea (e.g. `impossible_physics` + `hand_evidence` both saying "human defied reality"), pick one and make it louder.
- A scene with 3 forces and no dominant one is a committee. Rank them. Commit.
- If the force is "this is a chrome teapot," that is not a force. That is a subject.

---

## Axiom III — Imperfection is the 2026 signature.

Hand-evidence beats AI polish.

In 2024 the signal was photoreal. In 2025 the signal was stylized. In 2026 the signal is human. A scene that shows a fingerprint, a seam, a misaligned edge, a sculpt mark, a fabric pucker — reads as made. A scene that hides all of those reads as generated.

This is not a trend. It is a second-order effect of generation getting cheap. When the baseline is flawless, flaws become the proof of intention. The seam is the signature.

**In practice:**
- Every mode in `tokens/modes.yaml` declares one `discord_ingredient` — the element that breaks the aesthetic. Ship it.
- Subsurface scattering, subtle bump noise, and a very slight camera roll (1-3°) all register as hand-evidence without looking sloppy.
- Render at an unusual resolution. `1728x1080` reads as hand-cropped; `1920x1080` reads as default.
- Noise is not a finish. Noise is the start. 1-3 stops of grain is plenty. Above that you're hiding.

---

## Corollary 1 — HDRI before solid.

Solid-color world backgrounds are a skill-floor tell. They read as "I did not know about HDRIs."

An HDRI does two things a solid can't: it reflects into every specular surface (so chrome and gloss know what they are near) and it lights with direction and hue, not a flat fill. Even for a matte product on a white backdrop, the HDRI behind the camera changes the mood of the front-facing speculars.

**In practice:** Poly Haven slugs are pre-mapped in every palette. Use them. If the HDRI disagrees with the palette, change the palette, not the HDRI.

---

## Corollary 2 — Three-point before one lamp.

Flat lighting is a bug. A single-lamp render reads as WIP or as deliberately stylized — and deliberate stylization requires Axiom I work: the lamp must have character.

Start with key + fill + rim. If the scene looks better with only the key, delete the other two intentionally — but do the three-point first so you know what you're subtracting.

**In practice:** Rim lights at 2x the key's intensity are fine. That is the single move that separates product renders from portrait renders.

---

## Corollary 3 — Rule-of-thirds before center.

Center-framing is for logos, not scenes. A subject dead-center reads as either "logo" or "no decision was made." Both are bad unless you are rendering a logo.

Thirds, golden ratio, or deliberate off-axis (dutch) all beat center. The voice axis encodes this: `intimate_macro` and `dolly_cinematic` push the subject to 1/3; `dutch_drama` tilts the whole frame; only `gods_eye_ortho` allows centering, because ortho is a flat-lay convention.

**In practice:** Move the camera, not the subject. Scenes built subject-first tend to drift toward center. Scenes built camera-first stay off-axis.

---

## Corollary 4 — PBR before Diffuse.

Albedo without metallic and roughness is not a material. It is a swatch. The modern Principled BSDF is the floor, not the ceiling — every surface you ship should declare at least three of: metallic, roughness, subsurface, anisotropic, clearcoat.

Diffuse-only materials are a 2012 convention. They still render. They also still look like 2012.

**In practice:** If the subject is chrome, metallic=1.0 and roughness<0.1 is the start; anisotropic brush direction is what makes it not a mirror ball. If the subject is plush, subsurface radius matters more than color. If the subject is concrete, bump scale matters more than base color.

---

## Corollary 5 — Discord is mandatory.

One element must defy the mode, or the scene is dead.

A brutalist scene with no organic element is a CAD render. A ghibli scene with no sharp edge is a screensaver. A plushcore scene with no glass is a pillow commercial. The discord is what proves the mode was a choice, not a default.

**In practice:** Every mode in `tokens/modes.yaml` has a `discord_ingredient` field. It is not optional. The assembler includes it by default; you must actively delete it to skip.

---

## Closing

The render engine is not the artist. The artist is the one who chose the tension.
