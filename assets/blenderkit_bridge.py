"""BlenderKit asset bridge.

Emits Blender Python that searches BlenderKit's REST API, downloads a free
asset's .blend file, and appends its collections/objects into the current
scene. Designed to pipe through MCP `execute_blender_code`.

Why direct HTTP instead of the BlenderKit UI operators? The `view3d.blenderkit_search`
operator relies on Blender's event-loop timers to poll the Go Client sidecar
for async results. When invoked synchronously via MCP `execute_blender_code`,
the event loop doesn't tick, so results never populate. Direct HTTP against
`https://www.blenderkit.com/api/v1/search/` is synchronous and MCP-safe.

Login: the BlenderKit addon stores your `scene_uuid` (required for the
download endpoint) in `utils.get_scene_id()`. Free-tier works without login
for assets with `isFree=True` AND `canDownload=True`.
"""

from __future__ import annotations

ASSET_TYPES = ("model", "material", "scene", "hdr", "brush", "texture", "nodegroup")

_API_BASE = "https://www.blenderkit.com/api/v1"


def emit_blenderkit_probe() -> str:
    """Emit Python that reports BlenderKit availability + scene_uuid + API reachability."""
    return (
        "import sys, urllib.request, urllib.error\n"
        "_bk = sys.modules.get('bl_ext.blenderkit_com.blenderkit')\n"
        "_u = sys.modules.get('bl_ext.blenderkit_com.blenderkit.utils')\n"
        "if _bk is None:\n"
        "    print('BLENDERKIT_STATUS: missing - install and enable the addon')\n"
        "else:\n"
        "    _sid = _u.get_scene_id() if _u and hasattr(_u, 'get_scene_id') else None\n"
        "    try:\n"
        "        _r = urllib.request.urlopen('" + _API_BASE + "/search/?query=test&page_size=1', timeout=10)\n"
        "        _reachable = _r.status == 200\n"
        "    except Exception as _e:\n"
        "        _reachable = False\n"
        "    print('BLENDERKIT_STATUS: ready  scene_uuid=' + str(_sid) + '  api_reachable=' + str(_reachable))\n"
    )


def emit_blenderkit_fetch(
    keyword: str,
    asset_type: str = "model",
    free_only: bool = True,
    page_size: int = 20,
    timeout_search: int = 30,
    timeout_dl: int = 300,
    result_var: str = "DC_BK_RESULT",
    cache_dir: str | None = None,
) -> str:
    """Emit Python that searches, picks the first free result, downloads the .blend, and appends it.

    The emitted snippet sets `{result_var}` to the root object's name on success.
    Raises TimeoutError / RuntimeError on failure.
    """
    asset_type = asset_type.lower()
    if asset_type not in ASSET_TYPES:
        raise ValueError(f"asset_type must be one of {ASSET_TYPES}, got {asset_type!r}")
    kw_lit = repr(keyword)
    at_lit = repr(asset_type)
    free_lit = "True" if free_only else "False"
    api = repr(_API_BASE)
    page = int(page_size)
    ts = int(timeout_search)
    td = int(timeout_dl)
    cache = repr(cache_dir) if cache_dir else "None"

    lines = [
        "import bpy, sys, os, json, tempfile, urllib.parse, urllib.request",
        "",
        "_keyword = " + kw_lit,
        "_asset_type = " + at_lit,
        "_free_only = " + free_lit,
        "_api_base = " + api,
        "_page_size = " + str(page),
        "_timeout_search = " + str(ts),
        "_timeout_dl = " + str(td),
        "_cache_dir_override = " + cache,
        "",
        "# scene_uuid is required by BlenderKit download endpoint",
        "_u = sys.modules.get('bl_ext.blenderkit_com.blenderkit.utils')",
        "if _u is None or not hasattr(_u, 'get_scene_id'):",
        "    raise RuntimeError('BlenderKit addon not loaded; cannot get scene_uuid')",
        "_scene_uuid = _u.get_scene_id()",
        "",
        "_cache_dir = _cache_dir_override or os.path.join(tempfile.gettempdir(), 'dc_blenderkit')",
        "os.makedirs(_cache_dir, exist_ok=True)",
        "_ua = {'User-Agent': 'dimensional-chaos/0.1', 'Accept': '*/*'}",
        "",
        "# 1. Search BlenderKit REST API (synchronous)",
        "_qs = urllib.parse.urlencode({",
        "    'query': _keyword,",
        "    'asset_type': _asset_type,",
        "    'page_size': _page_size,",
        "})",
        "_search_url = _api_base + '/search/?' + _qs",
        "_req = urllib.request.Request(_search_url, headers=_ua)",
        "with urllib.request.urlopen(_req, timeout=_timeout_search) as _r:",
        "    _sdata = json.loads(_r.read().decode('utf-8'))",
        "_results = _sdata.get('results') or []",
        "if _free_only:",
        "    _pool = [r for r in _results if r.get('isFree') and r.get('canDownload', True)]",
        "else:",
        "    _pool = [r for r in _results if r.get('canDownload', True)]",
        "if not _pool:",
        "    raise RuntimeError('No downloadable results for ' + repr(_keyword))",
        "_target = _pool[0]",
        "_display = _target.get('displayName', _target.get('name', '?'))",
        "",
        "# 2. Find the .blend file in the asset's files list",
        "_files = _target.get('files') or []",
        "_blend = next((f for f in _files if f.get('fileType') == 'blend'), None)",
        "if _blend is None or not _blend.get('downloadUrl'):",
        "    raise RuntimeError('No .blend file available for asset: ' + str(_display))",
        "",
        "# 3. Resolve the real file URL via BlenderKit's download endpoint",
        "_dl_resp_url = _blend['downloadUrl'] + '?scene_uuid=' + _scene_uuid",
        "_req = urllib.request.Request(_dl_resp_url, headers=_ua)",
        "with urllib.request.urlopen(_req, timeout=_timeout_search) as _r:",
        "    _desc = json.loads(_r.read().decode('utf-8'))",
        "_file_url = _desc.get('filePath')",
        "if not _file_url:",
        "    raise RuntimeError('Download descriptor missing filePath for: ' + str(_display))",
        "",
        "# 4. Download the .blend (with disk cache)",
        "_file_uuid = _desc.get('uuid') or _blend.get('downloadUrl', '').rstrip('/').split('/')[-1]",
        "_local = os.path.join(_cache_dir, 'bk_' + str(_file_uuid) + '.blend')",
        "if not os.path.exists(_local):",
        "    _req = urllib.request.Request(_file_url, headers=_ua)",
        "    _total = 0",
        "    with urllib.request.urlopen(_req, timeout=_timeout_dl) as _r, open(_local, 'wb') as _fh:",
        "        while True:",
        "            _chunk = _r.read(65536)",
        "            if not _chunk: break",
        "            _fh.write(_chunk)",
        "            _total += len(_chunk)",
        "",
        "# 5. Append collections + objects from the .blend",
        "_objs_before = set(bpy.context.scene.objects.keys())",
        "with bpy.data.libraries.load(_local, link=False) as (_from, _to):",
        "    _to.collections = list(_from.collections) if _from.collections else []",
        "    _to.objects = list(_from.objects) if _from.objects else []",
        "",
        "# 6. Link into the active scene",
        "for _col in (_to.collections or []):",
        "    if _col is not None and _col.name not in bpy.context.scene.collection.children:",
        "        bpy.context.scene.collection.children.link(_col)",
        "for _obj in (_to.objects or []):",
        "    if _obj is not None and _obj.name not in bpy.context.scene.objects:",
        "        bpy.context.scene.collection.objects.link(_obj)",
        "",
        "_objs_after = set(bpy.context.scene.objects.keys())",
        "_new = _objs_after - _objs_before",
        "if not _new:",
        "    raise RuntimeError('Append finished but no new objects appeared: ' + str(_display))",
        "_roots = [n for n in _new if bpy.context.scene.objects[n].parent is None]",
        result_var + " = _roots[0] if _roots else next(iter(_new))",
        "print('BLENDERKIT_OK asset=' + repr(_display) + ' object=' + repr(" + result_var + ") + ' file=' + _local + ' new_count=' + str(len(_new)))",
    ]
    return "\n".join(lines) + "\n"


def emit_blenderkit_place(
    object_name_var: str,
    location: tuple = (0.0, 0.0, 0.0),
    rotation_euler: tuple = (0.0, 0.0, 0.0),
    scale: float | tuple = 1.0,
) -> str:
    """Emit Python that positions/rotates/scales the fetched asset's root."""
    loc_lit = repr(tuple(float(x) for x in location))
    rot_lit = repr(tuple(float(x) for x in rotation_euler))
    if isinstance(scale, (int, float)):
        scale_lit = repr((float(scale), float(scale), float(scale)))
    else:
        scale_lit = repr(tuple(float(x) for x in scale))
    lines = [
        "import bpy",
        "_obj = bpy.data.objects.get(" + object_name_var + ")",
        "if _obj is None:",
        "    raise RuntimeError('BlenderKit-placed object not found: ' + str(" + object_name_var + "))",
        "_obj.location = " + loc_lit,
        "_obj.rotation_euler = " + rot_lit,
        "_obj.scale = " + scale_lit,
        "print('BLENDERKIT_PLACED ' + str(" + object_name_var + "))",
    ]
    return "\n".join(lines) + "\n"


def recipe_to_search_query(recipe) -> str:
    """Turn a Dimensional Chaos Recipe into a BlenderKit search keyword string."""
    mode_hints = {
        "claymation_warmth": "clay sculpture",
        "studio_ghibli_nature": "tree foliage",
        "brutalist_sculpture": "concrete architecture",
        "plushcore_soft": "plush felt fabric",
        "hyperreal_chrome": "chrome metal product",
        "liminal_lowpoly": "lowpoly empty room",
        "isometric_diorama": "miniature tiny scene",
    }
    hint = mode_hints.get(getattr(recipe, "mode", ""), "")
    subject = getattr(recipe, "subject", "") or ""
    parts = [p for p in (subject, hint) if p]
    return " ".join(parts).strip() or subject or "scene"
