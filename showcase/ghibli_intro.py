"""Ghibli Portfolio Intro: tiny character walking through giant grass blades.

Canonical Recipe #2 — "Studio Ghibli Nature" mode with fog-valley palette.
Dolly cinematic voice drives a 120-frame push-in animation; scale distortion
and light-as-character forces sell the "ant's-eye view of a meadow" feel.

Note: this scene is ANIMATED. Render time is proportional to frame count.
On Cycles 256 samples at 1920x1080 expect ~10-15 minutes per frame.
Use --still to emit a single-frame version for previewing.
"""
from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import Recipe, Scene

RECIPE = Recipe(
    mode="studio_ghibli_nature",
    palette="fog_valley",
    voice="dolly_cinematic",
    forces=["scale_distortion", "light_as_character"],
    subject="tiny character walking through giant grass blades, god-rays through mist",
)

# Animation spec: dolly_cinematic voice implies a 120-frame push-in.
# The engine reads these from recipe.extras to emit the correct timeline.
FRAME_START = 1
FRAME_END = 120


def build(
    use_meshy: bool = False,
    output_dir: str = "render",
    still: bool = False,
) -> Path:
    """Assemble the Ghibli intro scene.

    When `still` is True, emits a single-frame scene (faster to preview).
    Otherwise emits the full 120-frame animation timeline.
    """
    scene = Scene(RECIPE)

    # Hand animation window to the engine so it can set scene.frame_start /
    # scene.frame_end and wire up any keyframed dolly moves.
    scene.recipe.extras["frame_start"] = FRAME_START
    scene.recipe.extras["frame_end"] = FRAME_START if still else FRAME_END
    scene.recipe.extras["animated"] = not still

    if use_meshy:
        from assets import MeshyBridge

        bridge = MeshyBridge()
        asset = bridge.generate_asset(
            "tiny whimsical Ghibli-style wanderer character, backpack, "
            "soft cel-shaded fabric, 15cm tall, ready for 3D scene"
        )
        scene.recipe.extras["hero_glb"] = asset["glb_path"]

    python_code = scene.assemble()
    out = Path(output_dir) / "ghibli_intro.py"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(python_code)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--use-meshy",
        action="store_true",
        help="Generate the wanderer character via Meshy (costs ~18 credits)",
    )
    ap.add_argument("--output-dir", default="render")
    ap.add_argument(
        "--still",
        action="store_true",
        help="Emit a single frame instead of the full 120-frame animation",
    )
    ap.add_argument(
        "--print-code",
        action="store_true",
        help="Echo the emitted Blender Python to stdout after writing",
    )
    args = ap.parse_args()

    out_path = build(
        use_meshy=args.use_meshy,
        output_dir=args.output_dir,
        still=args.still,
    )
    scene = Scene(RECIPE)

    frame_count = 1 if args.still else (FRAME_END - FRAME_START + 1)

    print(f"[dimensional-chaos] Recipe: {RECIPE}")
    print(f"[dimensional-chaos] Plan: {scene.preview_plan()}")
    print(f"[dimensional-chaos] Emitted Blender script: {out_path}")
    print(f"[dimensional-chaos] Frames: {frame_count} "
          f"({'still preview' if args.still else f'{FRAME_START}-{FRAME_END}'})")
    if not args.still:
        print(f"[dimensional-chaos] Render sequence hint:")
        print(f"    blender --background --python {out_path} \\")
        print(f"        -o render/ghibli_intro_#### -F PNG -x 1 \\")
        print(f"        -s {FRAME_START} -e {FRAME_END} -a")
        print(f"[dimensional-chaos] Warning: full animation is ~20-30 hours on Cycles.")
        print(f"[dimensional-chaos] Tip: use --still to preview a single frame first.")
    else:
        print(f"[dimensional-chaos] Run in Blender: blender --background --python {out_path}")

    print(f"[dimensional-chaos] Or via Blender MCP: paste contents into execute_blender_code")

    if args.print_code:
        print("\n=== BLENDER PYTHON ===\n")
        print(out_path.read_text())
