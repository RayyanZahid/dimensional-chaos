"""Meshy bridge — text -> Nano Banana image -> image-to-3D -> GLB.

Self-contained client for the Meshy REST API. The flow we care about:
    prompt -> /v1/text-to-image (nano-banana, 3 credits)
           -> /v1/image-to-3d (15 credits, should_texture + enable_pbr)
           -> poll -> download GLB

Cache lives at ./cache/meshy/{sha256(prompt)}/ so repeated prompts return
instantly. Set MESHY_API_KEY in the environment before use.
"""

import hashlib
import json
import os
import time
from pathlib import Path

import requests

BASE_URL = "https://api.meshy.ai/openapi"
TIMEOUT = 60
CACHE_ROOT = Path("./cache/meshy")

# Meshy pricing (subject to change — keep in sync with meshy.ai/pricing)
CREDIT_COSTS = {"text-to-image": 3, "image-to-3d": 15}


class MeshyBridge:
    """Meshy API bridge: text -> image -> textured GLB."""

    def __init__(self, api_key: str = None):
        """Reads MESHY_API_KEY from env if api_key not passed."""
        self.api_key = api_key or os.environ.get("MESHY_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "MESHY_API_KEY not set. See https://www.meshy.ai for API access."
            )
        CACHE_ROOT.mkdir(parents=True, exist_ok=True)

    def _headers(self) -> dict:
        """Authorization + JSON content-type headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _post(self, endpoint: str, payload: dict) -> dict:
        """POST JSON with 60s timeout and one retry (2x backoff)."""
        url = f"{BASE_URL}{endpoint}"
        for attempt in range(2):
            try:
                resp = requests.post(url, headers=self._headers(), json=payload, timeout=TIMEOUT)
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as err:
                if attempt == 0:
                    time.sleep(2.0)
                    continue
                raise RuntimeError(f"Meshy POST {endpoint} failed: {err}") from err

    def _get(self, endpoint: str) -> dict:
        """GET with 60s timeout and one retry (2x backoff)."""
        url = f"{BASE_URL}{endpoint}"
        for attempt in range(2):
            try:
                resp = requests.get(url, headers=self._headers(), timeout=TIMEOUT)
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as err:
                if attempt == 0:
                    time.sleep(2.0)
                    continue
                raise RuntimeError(f"Meshy GET {endpoint} failed: {err}") from err

    def balance(self) -> int:
        """Return current Meshy credit balance."""
        return int(self._get("/v1/balance").get("balance", 0))

    def generate_image(self, prompt: str, aspect_ratio: str = "1:1") -> list:
        """Generate image via Nano Banana text-to-image, return list of image URLs."""
        if len(prompt) > 600:
            raise ValueError("Meshy prompt max is 600 chars")
        print("[Meshy] generating image...")
        t0 = time.time()
        payload = {"prompt": prompt, "ai_model": "nano-banana", "aspect_ratio": aspect_ratio}
        created = self._post("/v1/text-to-image", payload)
        task_id = created.get("result")
        if not task_id:
            raise RuntimeError(f"Meshy text-to-image: no task id in response: {created}")
        task = self.wait_for_task("/v1/text-to-image", task_id)
        urls = task.get("image_urls") or []
        if not urls:
            raise RuntimeError(f"Meshy text-to-image: no image_urls in task {task_id}")
        print(f"[Meshy] image ready in {int(time.time() - t0)}s ({len(urls)} variant(s))")
        return urls

    def image_to_3d(
        self,
        image_url: str,
        should_texture: bool = True,
        enable_pbr: bool = True,
    ) -> dict:
        """Submit image-to-3D, wait, return full task dict with model_urls/texture_urls."""
        print("[Meshy] building 3D...")
        payload = {
            "image_url": image_url,
            "ai_model": "latest",
            "should_texture": should_texture,
            "enable_pbr": enable_pbr,
            "target_formats": ["glb"],
        }
        created = self._post("/v1/image-to-3d", payload)
        task_id = created.get("result")
        if not task_id:
            raise RuntimeError(f"Meshy image-to-3d: no task id in response: {created}")
        task = self.wait_for_task("/v1/image-to-3d", task_id)
        return task

    def wait_for_task(
        self,
        endpoint: str,
        task_id: str,
        poll_interval: float = 5.0,
        timeout: int = 600,
    ) -> dict:
        """Poll GET {endpoint}/{task_id} until SUCCEEDED or raise on FAILED/timeout."""
        start = time.time()
        while True:
            task = self._get(f"{endpoint}/{task_id}")
            status = task.get("status", "UNKNOWN")
            if status == "SUCCEEDED":
                return task
            if status in ("FAILED", "CANCELED"):
                err = (task.get("task_error") or {}).get("message", status)
                raise RuntimeError(f"Meshy task {task_id} {status}: {err}")
            if time.time() - start > timeout:
                raise TimeoutError(f"Meshy task {task_id} timed out after {timeout}s (status={status})")
            time.sleep(poll_interval)

    def download_model(self, url: str, output_path: str) -> str:
        """Stream-download a file to output_path, return the path."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(url, stream=True, timeout=TIMEOUT) as resp:
            resp.raise_for_status()
            with open(path, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        fh.write(chunk)
        return str(path)

    def _cache_dir(self, prompt: str) -> Path:
        """Stable cache dir per prompt (sha256 of the prompt text)."""
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        return CACHE_ROOT / digest

    def generate_asset(self, prompt: str, aspect_ratio: str = "1:1") -> dict:
        """Full pipeline: prompt -> image -> textured GLB, with on-disk caching."""
        cdir = self._cache_dir(prompt)
        manifest = cdir / "manifest.json"
        if manifest.exists():
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                glb = data.get("glb_path")
                if glb and Path(glb).exists():
                    print(f"[Meshy] cache hit -> {glb}")
                    return data
            except json.JSONDecodeError:
                pass

        cdir.mkdir(parents=True, exist_ok=True)

        # Step 1: text -> image (Nano Banana)
        image_urls = self.generate_image(prompt, aspect_ratio=aspect_ratio)
        chosen_image = image_urls[0]

        # Step 2: image -> 3D (textured, PBR)
        task = self.image_to_3d(chosen_image, should_texture=True, enable_pbr=True)
        glb_url = (task.get("model_urls") or {}).get("glb")
        if not glb_url:
            raise RuntimeError("Meshy image-to-3d returned no glb url")
        texture_urls = task.get("texture_urls") or []

        # Step 3: download GLB
        glb_path = str(cdir / "model.glb")
        self.download_model(glb_url, glb_path)
        print(f"[Meshy] GLB ready at {glb_path}")

        # Download textures alongside the GLB (best-effort, does not block success)
        local_textures: list = []
        for idx, tex in enumerate(texture_urls):
            try:
                if isinstance(tex, dict):
                    for kind, url in tex.items():
                        if not isinstance(url, str) or not url.startswith("http"):
                            continue
                        ext = url.split("?")[0].rsplit(".", 1)[-1][:5] or "png"
                        tpath = str(cdir / f"texture_{idx}_{kind}.{ext}")
                        self.download_model(url, tpath)
                        local_textures.append(tpath)
                elif isinstance(tex, str) and tex.startswith("http"):
                    ext = tex.split("?")[0].rsplit(".", 1)[-1][:5] or "png"
                    tpath = str(cdir / f"texture_{idx}.{ext}")
                    self.download_model(tex, tpath)
                    local_textures.append(tpath)
            except Exception as err:
                print(f"[Meshy] texture {idx} skipped: {err}")

        result = {
            "glb_path": glb_path,
            "textures": local_textures,
            "meshy_task_id": task.get("id") or task.get("_id") or "",
            "prompt": prompt,
            "credits_used": CREDIT_COSTS["text-to-image"] + CREDIT_COSTS["image-to-3d"],
        }
        manifest.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result


if __name__ == "__main__":
    bridge = MeshyBridge()
    print(f"[Meshy] balance: {bridge.balance()} credits")
    demo_prompt = "chrome teapot on velvet cube, product photography, iridescent thin film"
    result = bridge.generate_asset(demo_prompt)
    print(json.dumps(result, indent=2))
