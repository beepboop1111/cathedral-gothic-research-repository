#!/usr/bin/env python3
"""blender_U01.py -- re-import every U01 GLB into Blender, check it as a structure, render one review image.

  python3 -I blender_U01.py <out_dir> <render_ids comma list> <all_ids comma list>

Checks per mesh object: nonmanifold edges/verts, degenerate faces, self-intersecting face pairs
(BVH overlap, faces sharing a vertex excluded), vertex/face counts and bounds versus the exporter.
"""
import json
import math
import sys
from pathlib import Path

import bpy  # must precede bmesh/mathutils when bpy is a module
import bmesh
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils.bvhtree import BVHTree

# works as a bpy module (python3 script.py ARGS) or inside Blender (blender -b --python script.py -- ARGS)
argv = [sys.argv[0]] + (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
out = Path(argv[1])
render_ids, all_ids = argv[2].split(","), argv[3].split(",")
pre = json.loads((out / "QA_U01.json").read_text())["models"]

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
res = {"blender": bpy.app.version_string, "models": {}, "labels": []}
groups = {}

for mid in all_ids:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(out / f"{mid}.glb"))
    new = [o for o in bpy.data.objects if o not in before]
    bpy.context.view_layer.update()
    mres, ok_all = {}, True
    for o in [o for o in new if o.type == "MESH"]:
        part = o.name.split("__")[-1].split(".")[0]
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.transform(o.matrix_world)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        xs = [v.co for v in bm.verts]
        lo = [min(c[i] for c in xs) for i in range(3)]
        hi = [max(c[i] for c in xs) for i in range(3)]
        size = max(h - l for h, l in zip(hi, lo))
        tree = BVHTree.FromBMesh(bm, epsilon=0.0)
        pairs = tree.overlap(tree)
        inter = 0
        for i, j in pairs:
            if i == j:
                continue
            if {v.index for v in bm.faces[i].verts} & {v.index for v in bm.faces[j].verts}:
                continue
            inter += 1
        r = dict(verts=len(bm.verts), faces=len(bm.faces),
                 nonmanifold_edges=sum(1 for e in bm.edges if not e.is_manifold),
                 nonmanifold_verts=sum(1 for v in bm.verts if not v.is_manifold),
                 degenerate_faces=sum(1 for f in bm.faces if f.calc_area() < 1e-12 * size * size),
                 self_intersecting_pairs=inter // 2, bounds=[lo, hi])
        bm.free()
        exp = pre[mid]["parts"][part]
        bb = exp["bounds_blender"]
        r["counts_match"] = r["verts"] == exp["vertices"] and r["faces"] == exp["faces"]
        r["bounds_match"] = all(abs(a - b) <= 1e-5 * max(size, 1e-9) for a, b in zip(lo + hi, bb[0] + bb[1]))
        solid_ok = part == "glass" or (r["nonmanifold_edges"] == 0 and r["nonmanifold_verts"] == 0)
        r["ok"] = bool(solid_ok and r["degenerate_faces"] == 0 and r["self_intersecting_pairs"] == 0
                       and r["counts_match"] and r["bounds_match"])
        ok_all &= r["ok"]
        mres[part] = r
    res["models"][mid] = dict(parts=mres, ok=bool(ok_all and len(mres) == len(pre[mid]["parts"])))
    grp = bpy.data.objects.new(f"GRP_{mid}", None)
    scene.collection.objects.link(grp)
    for o in new:
        if o.parent is None:
            o.parent = grp
    groups[mid] = (grp, [o for o in new if o.type == "MESH"])

res["all_ok"] = all(m["ok"] for m in res["models"].values())

# ---- layout: render set in a row at equal display height; others hidden
H, gap, x = 10.0, 1.2, 0.0
centres = {}
for mid, (grp, objs) in groups.items():
    if mid not in render_ids:
        for o in objs:
            o.hide_render = True
            o.hide_set(True)
        grp.location = (0, 0, -1000)
        continue
    b = res["models"][mid]["parts"]["wall"]["bounds"] if "wall" in res["models"][mid]["parts"] else \
        res["models"][mid]["parts"]["stone"]["bounds"]
    s = H / (b[1][2] - b[0][2])
    w = (b[1][0] - b[0][0]) * s
    grp.scale = (s, s, s)
    grp.location = (x - b[0][0] * s, 0, -b[0][2] * s)
    centres[mid] = Vector((x + w / 2, 0, H / 2))
    x += w + gap
bpy.context.view_layer.update()

# ---- materials tweak (imported PBR kept), world, light, camera
world = bpy.data.worlds.new("W")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.86, 0.86, 0.87, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.55
scene.world = world
sun = bpy.data.lights.new("sun", "SUN")
sun.energy, sun.angle = 3.2, math.radians(2.0)
so = bpy.data.objects.new("sun", sun)
scene.collection.objects.link(so)
so.rotation_euler = Vector((0.55, 0.8, -0.55)).to_track_quat("-Z", "Y").to_euler()

cam_d = bpy.data.cameras.new("cam")
cam_d.type = "ORTHO"
cam = bpy.data.objects.new("cam", cam_d)
scene.collection.objects.link(cam)
scene.camera = cam
target = Vector((x / 2, 0, H / 2))
az, el, dist = math.radians(22), math.radians(9), 200.0
cam.location = target + Vector((dist * math.sin(az) * math.cos(el), -dist * math.cos(az) * math.cos(el), dist * math.sin(el)))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
cam_d.clip_start, cam_d.clip_end = 0.01, 1000.0
bpy.context.view_layer.update()
inv = cam.matrix_world.inverted()
pts = []
for mid in render_ids:
    for o in groups[mid][1]:
        pts += [inv @ (o.matrix_world @ Vector(c)) for c in o.bound_box]
xs, ys = [p.x for p in pts], [p.y for p in pts]
cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
cam.location = cam.matrix_world @ Vector((cx, cy, 0))
scene.render.resolution_x, scene.render.resolution_y = 2400, 1000
aspect = scene.render.resolution_x / scene.render.resolution_y
cam_d.ortho_scale = max(max(xs) - min(xs), (max(ys) - min(ys)) * aspect) * 1.03
bpy.context.view_layer.update()
for mid in render_ids:
    u = world_to_camera_view(scene, cam, centres[mid])
    res["labels"].append(dict(id=mid, u=float(u.x), v=float(u.y)))

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 40
scene.cycles.use_denoising = True
try:
    scene.cycles.denoiser = "OPENIMAGEDENOISE"
except Exception:
    pass
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(out / "render_U01.png")
bpy.ops.render.render(write_still=True)

# ---- viewport preferences for the saved review scene
for scr in bpy.data.screens:
    for area in scr.areas:
        if area.type == "VIEW_3D":
            for sp in area.spaces:
                if sp.type == "VIEW_3D":
                    sp.lens, sp.clip_start, sp.clip_end = 9.3, 0.01, 1e11
bpy.ops.wm.save_as_mainfile(filepath=str(out / "U01_review.blend"))
(out / "blender_QA_U01.json").write_text(json.dumps(res, indent=1))
print("BLENDER", res["blender"], "all_ok", res["all_ok"])
for mid, m in res["models"].items():
    print(mid, m["ok"], {p: {k: v for k, v in r.items() if k not in ("bounds",)} for p, r in m["parts"].items()})
