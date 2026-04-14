# Design

Extended philosophy. Read this after AXIOMS.md.

---

## Why 3D. Why Now. Why Blender. Why MCP.

**Why 3D.** The web has moved past flat. Cargo templates have 3D heroes. Awwwards SOTD winners are 60% 3D in 2026. The default expectation for a landing page hero is that it is spatial. Figma-first brands read as dated.

**Why now.** Generation is cheap. Models are ubiquitous. The bottleneck is no longer "can I make a 3D asset" — the bottleneck is taste. Everything downstream of a prompt looks the same until someone decides. Dimensional Chaos is the decision layer.

**Why Blender.** It is free, it is the default, it has Cycles and EEVEE Next in one binary, and its Python API is the most powerful scripting surface of any DCC tool. Maya has bigger studios. Blender has bigger reach.

**Why MCP.** `execute_blender_code` is a Python-eval bus. That is its strength and its weakness. The weakness is that the model can emit any Python — including Python that makes cube-on-a-plane. The strength is that the model can emit any Python — including Python compiled by a taste engine. Dimensional Chaos emits the second kind.

---

## Mode: `claymation_warmth`

**Aesthetic origin.** Aardman (Wallace & Gromit), Laika (Kubo, Coraline), the fingerprinted stop-motion tradition. The dominant quality is warmth — both thermal (3200K keys, amber fill) and tactile (fuzzy silhouettes, bumpy surfaces). Every character feels like it could be picked up.

**Blender fingerprint.**
1. Displace modifier at low noise scale on every organic surface — so edges catch light irregularly.
2. Subsurface scattering with warm radius (skin-tone even on non-skin).
3. Key light at 3200K, fill at 4500K, rim at 5600K — the temperature ladder warms the scene from shadow to highlight.
4. Shutter angle at 360° if animated — motion blur is part of the handmade look.
5. Slight camera wobble: a 0.5-1° sine perturbation on roll.

**What it's FOR.** Indie game heroes. Founder portraits where the founder wants to read as approachable, not titanic. Storybook covers. Essay headers where the tone is "come sit down."

**What it's NOT.** Luxury. B2B enterprise. Anything that needs to feel expensive. Claymation reads as small-studio and warm — it cannot carry a $50K/seat SaaS brand.

**Example recipe pairing.**
```
claymation_warmth + golden_hour_valley + intimate_macro + [hand_evidence, light_as_character]
```

---

## Mode: `studio_ghibli_nature`

**Aesthetic origin.** Miyazaki's backgrounds (Nausicaä, Totoro, Mononoke), Kazuo Oga's atmospheric perspective, Makoto Shinkai's wet grass. The quality is humidity — the air has weight, the light has to travel through it.

**Blender fingerprint.**
1. Volumetric scattering in the world with low density — adds the "god rays through branches" without explicit beams.
2. Principled Volume for fog at the horizon, falling off with distance.
3. Wind-simulated grass (Geometry Nodes procedural or cached alembic).
4. Two suns: one warm sun at horizon altitude, one cool bounce sun behind camera.
5. Compositor glare (fog glow, low threshold) — Ghibli highlights always bloom.

**What it's FOR.** Portfolio intros. Essay headers with nostalgic or reflective tone. Soft brand launches — wellness, travel, slow-food.

**What it's NOT.** Urgent. Transactional. If the goal is "click here now," ghibli will slow the viewer down instead. That is a feature, not a bug — use it when you want the viewer to slow down.

**Example recipe pairing.**
```
studio_ghibli_nature + fog_valley + dolly_cinematic + [scale_distortion, light_as_character]
```

---

## Mode: `brutalist_sculpture`

**Aesthetic origin.** Goldfinger, Kenzo Tange, Paul Rudolph, the heroic-concrete movement of the 1960s-70s; and, downstream, the brutalist-web revival that started around 2024. The quality is weight — objects read as immovable, shadows as chiseled.

**Blender fingerprint.**
1. Geometry built from very large primitives — no fillets, hard 90° edges, chamfers measured in centimeters on meter-scale objects.
2. Concrete shader: high-frequency bump, low specular, subtle dust layer.
3. Single directional sun at 15° altitude — casts shadows 3-4x the subject's height.
4. Sky with zero cloud — clear HDRI or procedural gradient.
5. Camera low, subject tall. Architectural wide voice is the default pairing.

**What it's FOR.** Case study covers. B2B hero images for infrastructure companies. Architecture firm decks. Anything that needs to say "serious and permanent."

**What it's NOT.** Consumer-friendly. Playful. Brutalism read as stern at minimum and hostile at maximum — if you want warmth, don't pick it.

**Example recipe pairing.**
```
brutalist_sculpture + moonlit_concrete + architectural_wide + [negative_space, light_as_character]
```

---

## Mode: `plushcore_soft`

**Aesthetic origin.** Jellycat, mushy-TikTok, the "everything should be held" wave of 2024-2025 Gen Z consumer branding. Max subsurface, zero sharp edges, pastel wash.

**Blender fingerprint.**
1. Every object put through a Bevel modifier with large segment count — no corners sharper than 10mm radius.
2. Felt shader: subsurface color = base color at 80% saturation, radius large (1.5mm+), fiber normal map.
3. Softbox key light, no direct sun — overcast studio HDRI only.
4. Very shallow DOF — f/1.4 on 85mm intimate macro voice.
5. Subtle bump to simulate fabric weave; hair particles for lint at silhouette edges.

**What it's FOR.** Consumer product renders where the product should read as huggable. Kids brands. Wellness. Gen Z launches. A surprising amount of fintech now uses this (Monzo's "money should feel soft").

**What it's NOT.** Industrial. Premium-luxury (plushcore reads as affordable-premium, not luxury). Technical demos.

**Example recipe pairing.**
```
plushcore_soft + overcast_studio + intimate_macro + [material_contrast, hand_evidence]
```

---

## Mode: `hyperreal_chrome`

**Aesthetic origin.** Beeple's daily renders, Ian Spriggs' portrait work, the crypto-art-meets-product-viz intersection of 2021-2024, still active in 2026 as the "tech launch" default. The quality is specularity — the subject exists primarily as a thing that reflects.

**Blender fingerprint.**
1. Principled BSDF with metallic=1.0, roughness<0.15, anisotropic 0.2-0.4 with brushed direction.
2. HDRI chosen for its reflection story, not its lighting story — studio_small HDRIs with visible softbox shapes are ideal.
3. Cycles renderer, 4000+ samples, caustics enabled.
4. Post-process chromatic aberration, subtle bloom, lens distortion.
5. Camera with f/1.4 shallow DOF and a 1-2° dutch tilt to break product-shot convention.

**What it's FOR.** Tech launches. Crypto brand assets. Luxury product renders. DevTools hero shots where the product is an abstract idea (API, protocol) rendered as a physical object.

**What it's NOT.** Warm. Human. Chrome reads as inevitable and manufactured — it has no hand-evidence by default. If you want warmth, do not pick this mode.

**Example recipe pairing.**
```
hyperreal_chrome + iridescent_candy + intimate_macro + [material_contrast, light_as_character]
```

---

## Mode: `liminal_lowpoly`

**Aesthetic origin.** Kane Pixels' Backrooms, PS1-era texture budgets, the "no-one is here" genre that exploded on TikTok 2023-2025. The quality is absence — the scene is built so you notice what is missing (people, time of day, exit).

**Blender fingerprint.**
1. Untextured or low-res textured surfaces — flat shading, no subdivision.
2. Repeating architectural modules (hallway, room, hallway) at integer scale.
3. Single flickering fluorescent or sodium lamp — the light is the only animate thing.
4. EEVEE Next renderer with deliberately crunchy shadow maps — the jaggies are the point.
5. Slight VHS grain in post; 4:3 aspect if you can get away with it.

**What it's FOR.** Ambient horror. Essay middles (where you want the reader to pause and feel). Portfolio interstitials. Video loop backgrounds.

**What it's NOT.** Commercial. Selling. Liminal spaces are about the absence of action — if your scene has a CTA, do not pick this.

**Example recipe pairing.**
```
liminal_lowpoly + sodium_vapor_liminal + architectural_wide + [negative_space, hand_evidence]
```

---

## Mode: `isometric_diorama`

**Aesthetic origin.** Monument Valley, Townscaper, SimCity cutaway art, the isometric revival of 2020-2026 illustration. The quality is miniature — the scene reads as a toy world you could pick up.

**Blender fingerprint.**
1. Orthographic camera at 30° elevation, 45° rotation.
2. All geometry built with chamfered edges (Bevel, 2-3 segments, small width) — the miniature look.
3. Material palette limited to 5-8 colors total for the whole scene.
4. Soft shadows from a sun light tilted to match camera azimuth.
5. Optional: cutaway walls using boolean, showing interior.

**What it's FOR.** Explainer graphics. Onboarding flows. City-sim aesthetic. B2B product walkthroughs where the product is a system.

**What it's NOT.** Dramatic. Emotional. Isometric is a diagram convention — it is best at showing how things fit together, not what they feel like.

**Example recipe pairing.**
```
isometric_diorama + overcast_studio + gods_eye_ortho + [scale_distortion, material_contrast]
```

---

## Force: `scale_distortion`

**The tension.** Small thing huge, huge thing small. The viewer's sense of "how big is that?" is deliberately broken.

**How it shows up.** A teacup the size of a building. A person at ankle height of a plush pig. A mountain rendered at desk-object scale. The force works when the viewer's first glance says "wait, what am I looking at?"

**Blender hooks.** Real-world camera settings (36mm sensor, 24mm lens) combined with objects at impossible scale. Or: correct object scale combined with a wide lens (14mm) that exaggerates perspective distortion. Either route works. The key is that the distortion is legible — the viewer notices.

**Overuse failure mode.** If every object in the scene is off-scale, the viewer's brain resets to "this is a surreal world" and the tension collapses. Keep at least one familiar-scale object in frame as an anchor.

**When to combine.** Pairs beautifully with `negative_space` (a tiny thing in a huge empty field doubles the tension) and with `light_as_character` (the light confirms the distortion by casting correctly-scaled shadows).

---

## Force: `light_as_character`

**The tension.** The light arrives before the subject. You feel the beam before you read the object.

**How it shows up.** A single shaft of god-ray cutting across the composition. A rim light so bright the silhouette is defined by absence. A volumetric spotlight in a foggy room where the beam is more present than what it hits.

**Blender hooks.** Volumetric scattering in world or object volume. Spotlight with a gobo. Rim light at 3-5x key intensity. Low-altitude sun cutting through window geometry.

**Overuse failure mode.** If every scene has a visible beam, the device becomes a trope and stops being a force. Use it where the scene is otherwise calm.

**When to combine.** Works with every mode. Especially strong with `brutalist_sculpture` (hard geometry + volumetric beam = heroic composition) and `liminal_lowpoly` (the fluorescent flicker IS the force).

---

## Force: `material_contrast`

**The tension.** Two materials that shouldn't touch. Chrome wrapped in felt. Concrete with a velvet ribbon. Glass against rust.

**How it shows up.** The contact surface between the two materials is where the viewer's eye lands. Where chrome meets plush, the specular falloff is the story.

**Blender hooks.** Two Principled BSDFs with radically different roughness, metallic, and subsurface. Subsurface-to-metallic is the canonical high-contrast pairing. Bump-scale mismatch (smooth + very rough) also works.

**Overuse failure mode.** If every object has three materials, the scene becomes noise. Limit to 2-3 materials in the frame; make the contrast count.

**When to combine.** Natural with `plushcore_soft` (plush against anything non-plush) and `hyperreal_chrome` (chrome against anything non-chrome). Less effective with `liminal_lowpoly`, which is about the absence of material detail.

---

## Force: `negative_space`

**The tension.** 70% of the frame is empty. The subject earns its place.

**How it shows up.** A single object, small in frame, against a vast field (sky, fog, empty hallway, blank wall). The emptiness is not lazy — it is deliberate. The viewer reads the subject as chosen.

**Blender hooks.** Composition-first camera placement — subject at rule-of-thirds intersection, 15-25% of frame area. World background simple (HDRI with minimal detail). No secondary subjects.

**Overuse failure mode.** If the empty space has no texture at all, the scene reads as a product shot on a white backdrop. The emptiness needs atmosphere — fog, gradient, HDRI presence — to be a force rather than a crop.

**When to combine.** Defines `brutalist_sculpture` and `liminal_lowpoly`. Friction with `hyperreal_chrome`, which wants the frame filled with reflection opportunities — use carefully.

---

## Force: `impossible_physics`

**The tension.** Something defies gravity, scale, or optics — but only one thing.

**How it shows up.** Liquid holding a shape mid-air. An object casting a shadow from a light that isn't there. A rope that doesn't sag. A reflection that doesn't match the scene.

**Blender hooks.** Rigid body turned off on one object. Light that only affects specific collections. Shader tricks — refraction that bends wrong, normals that lie. Or: cached simulation paused at the impossible moment.

**Overuse failure mode.** If multiple objects defy physics, the scene becomes cartoon. The force is strongest when one thing breaks the rules and everything else follows them.

**When to combine.** Strong with `hyperreal_chrome` (a chrome ball floating mid-air; the highlights anchor the reality) and `plushcore_soft` (a plush object behaving like liquid). Weak with `liminal_lowpoly`, which already feels physics-adjacent.

---

## Force: `hand_evidence`

**The tension.** A fingerprint, a seam, a smudge. Proof that a human decided.

**How it shows up.** Visible sculpt marks on an otherwise smooth form. A slightly misaligned seam on a fabric object. Dust in the exact right place. A camera tilt that is not computer-generated — it is a wobble.

**Blender hooks.** Dyntopo sculpt stroke at low resolution left unsmoothed. Noise modifier on object transform. Hand-painted normal maps. Shutter wobble (see claymation).

**Overuse failure mode.** If every surface shows hand-evidence, the render reads as unfinished. One deliberate imperfection per scene. Two if both are small.

**When to combine.** Defines `claymation_warmth`. Supports `plushcore_soft` (pucker in fabric). Adversarial with `hyperreal_chrome` by default — but that adversarial combo is the most interesting pairing in the whole system when it works.

---

## Closing

Dimensional Chaos is not a renderer. It is an opinion engine. The render is just proof.
