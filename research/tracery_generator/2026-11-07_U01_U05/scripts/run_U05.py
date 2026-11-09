#!/usr/bin/env python3
"""run_U05.py -- review PNG for U05 (tracery layer as its own masonry). Build with run_U03.py:

  python3 -I run_U03.py build --specs specs_U05.json --sections sections_U05.json --joints joints_U05.json --out out_U05
  python3 -I blender_U02.py out_U05 bar_2light_sexfoil,bar_4light_recursive,rose_12_chassis <all ids> bar_2light_sexfoil render 0.60 1.05
  python3 -I run_U05.py out_U05
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402
from shapely import wkt as swkt  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

import tracery_universal_U01 as T  # noqa: E402

out = Path(sys.argv[1] if len(sys.argv) > 1 else "out_U05")
qa = json.loads((out / "QA_U03.json").read_text())
bq = json.loads((out / "blender_QA_U01.json").read_text())
G = json.loads((out / "geom_U03.json").read_text())
jw = 6.0


def patch(g, **kw):
    g = swkt.loads(g) if isinstance(g, str) else g
    verts, codes = [], []
    for p in T.polys(g):
        for r in [p.exterior, *p.interiors]:
            c = np.asarray(r.coords)
            verts += c.tolist()
            codes += [MPath.MOVETO] + [MPath.LINETO] * (len(c) - 2) + [MPath.CLOSEPOLY]
    return PathPatch(MPath(verts, codes), **kw)


def layer_panel(ax, mid, xl, yl, title):
    g = G[mid]
    fr = [swkt.loads(b["wkt"]) for b in g["blocks"] if b["region"] == "frame"]
    tr = [swkt.loads(b["wkt"]) for b in g["blocks"] if b["region"] == "tracery"]
    for p in fr:
        ax.add_patch(patch(p, fc="#a8997c", ec="#4a3c24", lw=0.35))
    for i, p in enumerate(tr):
        ax.add_patch(patch(p, fc=("#ece2c8", "#e2d4b0")[i % 2], ec="#6b5a39", lw=0.35))
    Tu = unary_union(tr).buffer(2 * jw).buffer(-2 * jw)
    Fu = unary_union(fr).buffer(2 * jw).buffer(-2 * jw)
    edge = Tu.boundary.intersection(Fu.buffer(4 * jw))
    for ln in getattr(edge, "geoms", [edge]):
        if hasattr(ln, "coords") and len(ln.coords) > 1:
            c = np.asarray(ln.coords)
            ax.plot(c[:, 0], c[:, 1], color="#1db954", lw=1.6)
    ax.set_aspect("equal")
    ax.set_xlim(*xl)
    ax.set_ylim(*yl)
    ax.axis("off")
    ax.set_title(title, fontsize=10, loc="left")


fig = plt.figure(figsize=(24, 15), dpi=100, facecolor="white")
fig.text(0.01, 0.99, "U05 (EXPERIMENTAL): the tracery is its own layer of masonry - an open joint separates it from the wall "
         "frame, and its moulded bands run unbroken from the sill up into the small arches", fontsize=15.5, weight="bold",
         va="top")
ax0 = fig.add_axes([0.0, 0.50, 0.60, 0.46])
img = plt.imread(out / "render_U02.png")
ax0.imshow(img)
ax0.axis("off")
H, W = img.shape[:2]
for lab in bq["labels"]:
    r = qa["models"][lab["id"]]
    ax0.text(lab["u"] * W, 0.975 * H, f"{lab['id']}  ({r['blocks']} stones)", ha="center", va="bottom", fontsize=11,
             weight="bold", bbox=dict(fc="white", ec="none", alpha=0.85, pad=2))
ax1 = fig.add_axes([0.60, 0.39, 0.395, 0.57])
ax1.imshow(plt.imread(out / "closeup_U02.png"))
ax1.axis("off")
ax1.set_title("(a) bar_2light at the springing: wall jamb (coursed) | open joint | tracery band running down the jamb "
              "and mullion, its own longer stones", fontsize=9.5, loc="left")
layer_panel(fig.add_axes([0.01, 0.03, 0.16, 0.44]), "bar_2light_sexfoil", (-1500, 1500), (-250, 6000),
            "(b) bar_2light: wall frame (dark)\n| tracery layer (light), green = its edge")
layer_panel(fig.add_axes([0.18, 0.03, 0.20, 0.44]), "bar_4light_recursive", (-2700, 2700), (-300, 9300),
            "(c) bar_4light")
layer_panel(fig.add_axes([0.385, 0.05, 0.22, 0.40]), "rose_12_chassis", (-3100, 3100), (500, 6700),
            "(d) rose: new tracery ring inside the\nwall frame (heads and circles spring from it)")
ax4 = fig.add_axes([0.62, 0.02, 0.37, 0.34])
ax4.axis("off")
rows = [f"{'model':22s} {'geom':>7s} {'arch':>6s} {'tech':>6s} Blender stones (wall frame)"]
for k, v in qa["models"].items():
    cs = v["checks"]
    f = lambda kind: f"{sum(c['ok'] for c in cs if c['kind'] == kind)}/{sum(c['kind'] == kind for c in cs)}"
    rows.append(f"{k[:22]:22s} {f('geometric'):>7s} {f('architectural'):>6s} {f('technical'):>6s} "
                f"{'ok' if bq['models'][k]['ok'] else 'FAIL':7s} {v['blocks']:>4d} ({v['frame_blocks']})")
rows += ["",
         "Changes: open 6 mm joint wherever tracery meets the wall frame;",
         "  tracery uprights cut in ~900 mm pieces, beds staggered from the",
         "  ~420 mm wall courses; rose gets its own 70 mm tracery ring",
         "Technical : GLB reload, identical rebuilds; U03 fixtures unchanged",
         "Geometric : every stone watertight, one body, genus = holes;",
         "            Blender 0 nonmanifold / degenerate / self-intersecting",
         "Architect.: junctions inside single stones; sizes are TRIAL",
         "Historical: follows the documented separate stone frame jointed",
         "            onto mullion and cut-back jambs; no building surveyed",
         "Structural: not assessed"]
ax4.text(0.0, 1.0, "\n".join(rows), fontsize=10, family="monospace", va="top")
fig.savefig(out / "U05_tracery_layer.png", dpi=100, facecolor="white")
print("wrote", out / "U05_tracery_layer.png")
