"""Hero shot: chrome teapot on velvet cube. Peter Tarka DNA.

Canonical Recipe #1 — the "SF Startup Hero Scene".
Demonstrates hyperreal chrome material contrast against plush velvet,
lit like a character rather than an environment. Still frame.
"""
from pathlib import Path
import argparse
import sys

# ensure repo root on path so `from engine import ...` works when running
# this file directly (e.g. `python showcase/sf_chrome_hero.py`)
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import Recipe, Scene

RECIPE = Recipe(
    mode="hyperreal_chrome",
    palette="iridescent_candy",
    voice="intimate_macro",
    forces=["material_contrast", "light_as_character"],
    subject="chrome teapot on velvet cube",
)


def build(use_meshy: bool = False, output_dir: str = "render") -> Path:
    """Assemble the scene and write the emitted Blender Python to disk.

    Returns the path of the written script.
    """
    scene = Scene(RECIPE)

    if use_meshy:
        # Opt-in: spend ~18 Meshy credits to replace the primitive teapot
        # with a high-fidelity generated GLB. The engine will detect
        # `extras["hero_glb"]` and import it instead of using bpy.ops primitives.
        from assets import MeshyBridge

        bridge = MeshyBridge()
        asset = bridge.generate_asset(
            "photorealistic chrome teapot on magenta velvet cube, "
            "iridescent thin film, studio product photography, 85mm f/2.8"
        )
        scene.recipe.extras["hero_glb"] = asset["glb_path"]

    python_code = scene.assemble()
    out = Path(output_dir) / "sf_chrome_hero.py"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(python_code)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--use-meshy",
        action="store_true",
        help="Generate hero teapot via Meshy (costs ~18 credits)",
    )
    ap.add_argument("--output-dir", default="render")
    ap.add_argument(
        "--print-code",
        action="store_true",
        help="Echo the emitted Blender Python to stdout after writing",
    )
    args = ap.parse_args()

    out_path = build(use_meshy=args.use_meshy, output_dir=args.output_dir)
    scene = Scene(RECIPE)

    print(f"[dimensional-chaos] Recipe: {RECIPE}")
    print(f"[dimensional-chaos] Plan: {scene.preview_plan()}")
    print(f"[dimensional-chaos] Emitted Blender script: {out_path}")
    print(f"[dimensional-chaos] Run in Blender: blender --background --python {out_path}")
    print(f"[dimensional-chaos] Or via Blender MCP: paste contents into execute_blender_code")

    if args.print_code:
        print("\n=== BLENDER PYTHON ===\n")
        print(out_path.read_text())
