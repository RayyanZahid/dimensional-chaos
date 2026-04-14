"""Brutalist Case Study Cover: single concrete monolith, 70% empty frame.

Canonical Recipe #3 — "Brutalist Sculpture" mode with moonlit concrete palette.
Architectural wide voice pushes the camera back; negative space and
light-as-character forces do the heavy lifting. Still frame, cool moon from left.
"""
from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import Recipe, Scene

RECIPE = Recipe(
    mode="brutalist_sculpture",
    palette="moonlit_concrete",
    voice="architectural_wide",
    forces=["negative_space", "light_as_character"],
    subject="single concrete monolith, 70% empty frame, cool moon from left",
)


def build(use_meshy: bool = False, output_dir: str = "render") -> Path:
    """Assemble the brutalist cover scene and emit Blender Python."""
    scene = Scene(RECIPE)

    if use_meshy:
        from assets import MeshyBridge

        bridge = MeshyBridge()
        asset = bridge.generate_asset(
            "brutalist concrete monolith, weathered board-formed surface, "
            "subtle chamfered edges, architectural sculpture, neutral gray"
        )
        scene.recipe.extras["hero_glb"] = asset["glb_path"]

    python_code = scene.assemble()
    out = Path(output_dir) / "brutalist_cover.py"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(python_code)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--use-meshy",
        action="store_true",
        help="Generate the monolith via Meshy (costs ~18 credits)",
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
    print(f"[dimensional-chaos] Suggested render: Cycles 2048 samples, 1920x1080, ~60-90s")

    if args.print_code:
        print("\n=== BLENDER PYTHON ===\n")
        print(out_path.read_text())
