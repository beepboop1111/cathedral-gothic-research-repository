#!/usr/bin/env python3
"""run_U04.py -- compose the single review PNG for the rose window (build with run_U03.py).

  python3 -I run_U03.py build --specs specs_U04.json --sections sections_U04.json --joints joints_U04.json --out out_U04
  python3 -I blender_U02.py out_U04 rose_12_cusped,bar_4light_recursive rose_12_cusped,bar_4light_recursive rose_12_cusped
  python3 -I run_U04.py out_U04
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

import tracery_rose_U04 as R  # noqa: E402
import tracery_section_U02 as U  # noqa: E402
import tracery_universal_U01 as T  # noqa: E402

out = Path(sys.argv[1] if len(sys.argv) > 1 else "out_U04")
qa = json.loads((out / "QA_U03.json").read_text())
bq = json.loads((out / "blender_QA_U01.json").read_text())
G = json.loads((out / "geom_U03.json").read_text())
spec = json.loads(Path("specs_U04.json").read_text())[0]
m = R.RoseModel(spec)


def patch(g, **kw):
    g = swkt.loads(g) if isinstance(g, str) else g
    verts, codes = [], []
    for p in T.polys(g):
        for r in [p.exterior, *p.interiors]:
            c = np.asarray(r.coords)
            verts += c.tolist()
            codes += [MPath.MOVETO] + [MPath.LINETO] * (len(c) - 2) + [MPath.CLOSEPOLY]
    return PathPatch(MPath(verts, codes), **kw)


fig = plt.figure(figsize=(24, 15), dpi=100, facecolor="white")
fig.text(0.01, 0.99, "U04 rose / wheel window (EXPERIMENTAL): cusped hub, 12 radiating bars, pointed heads, cusped circles "
         "- same orders, mouldings, jointing and QA as the windows", fontsize=16, weight="bold", va="top")
ax0 = fig.add_axes([0.0, 0.53, 0.62, 0.43])
img = plt.imread(out / "render_U02.png")
ax0.imshow(img)
ax0.axis("off")
H, W = img.shape[:2]
for lab in bq["labels"]:
    r = qa["models"][lab["id"]]
    ax0.text(lab["u"] * W, 0.975 * H, f"{lab['id']}  ({r['blocks']} stones)", ha="center", va="bottom", fontsize=11,
             weight="bold", bbox=dict(fc="white", ec="none", alpha=0.85, pad=2))
ax1 = fig.add_axes([0.62, 0.43, 0.375, 0.53])
ax1.imshow(plt.imread(out / "closeup_U02.png"))
ax1.axis("off")
ax1.set_title("(a) rose, raking light: bars with roll/hollow mouldings, heads, cusped circles; 6 mm open joints",
              fontsize=10.5, loc="left")
# (b) construction: members by order in the 2D depth-study palette, solved centres
ax2 = fig.add_axes([0.01, 0.03, 0.30, 0.47])
for x in m.members:
    ax2.add_patch(patch(x["poly"], fc=U.DEPTH_PALETTE[U.member_order(x)], ec="black", lw=0.2, alpha=0.9))
cx, cz = m.c0
for nm, c in m.con["circles"].items():
    ax2.plot(*c["centre"], "+", color="#c0392b", ms=5)
for nm, c in m.con["cells"].items():
    for C in (c["CL"], c["CR"]):
        ax2.plot(C[0], C[1], ".", color="#1f618d", ms=2.5)
    ax2.plot([cx, c["apex"][0]], [cz, c["apex"][1]], color="#7f8c8d", lw=0.4, ls=(0, (3, 3)))
ax2.set_aspect("equal")
ax2.set_xlim(cx - 3100, cx + 3100)
ax2.set_ylim(cz - 3100, cz + 3100)
ax2.axis("off")
ax2.set_title("(b) construction by order (depth-study palette: o0 frame, o1 hub ring/bars/heads, o2 cusps/circles, o3 circle cusps)"
              "\n+ circle centres solved tangent to frame and heads; . head centres", fontsize=9.5, loc="left")
# (c) joint layout
ax3 = fig.add_axes([0.33, 0.03, 0.30, 0.47])
pal = ["#d9c9a3", "#c9b48a", "#e4d8bb", "#bfa77a", "#d2bf95"]
g = G["rose_12_cusped"]
for i, b in enumerate(g["blocks"]):
    ax3.add_patch(patch(b["wkt"], fc=("#b7a98f" if b["region"] == "frame" else pal[i % len(pal)]), ec="#5b4a2f", lw=0.35))
for z in g["zones"]:
    ax3.add_patch(patch(z, fc="none", ec="#c0392b", lw=0.5, ls=(0, (2, 2))))
ax3.set_aspect("equal")
ax3.set_xlim(cx - 3100, cx + 3100)
ax3.set_ylim(cz - 3100, cz + 3100)
ax3.axis("off")
r = qa["models"]["rose_12_cusped"]
ax3.set_title(f"(c) {r['blocks']} stones: frame voussoirs radial to the rose centre, bed joints across the bars,\n"
              "head voussoirs radial to their own centres, rings cut at lobe centres (red dashed = junction keep-out)",
              fontsize=9.5, loc="left")
# (d) QA
ax4 = fig.add_axes([0.65, 0.02, 0.34, 0.39])
ax4.axis("off")
rows = [f"{'model':22s} {'geom':>7s} {'arch':>6s} {'tech':>6s} Blender stones"]
for k, v in qa["models"].items():
    cs = v["checks"]
    f = lambda kind: f"{sum(c['ok'] for c in cs if c['kind'] == kind)}/{sum(c['kind'] == kind for c in cs)}"
    rows.append(f"{k[:22]:22s} {f('geometric'):>7s} {f('architectural'):>6s} {f('technical'):>6s} "
                f"{'ok' if bq['models'][k]['ok'] else 'FAIL':7s} {v['blocks']:>4d}")
rows += ["",
         "Technical : GLB export/reload; bit-identical rebuilds; the four",
         "            earlier windows rebuild byte-identical (regression)",
         "Geometric : 12-fold symmetry exact; spoke circles solved tangent",
         "            (residual < 1e-9); every stone watertight, one body,",
         "            genus = holes; Blender 0 nonmanifold / degenerate /",
         "            self-intersecting faces, bounds match",
         "Architect.: junctions inside single stones; stones <= 2.5 m;",
         "            depths, profiles, joints are TRIAL values",
         "Historical: Rayonnant-type composition (radiating bars, cusped",
         "            circles); not a survey of any rose",
         "Structural: not assessed (iron armature not modelled)"]
ax4.text(0.0, 1.0, "\n".join(rows), fontsize=10, family="monospace", va="top")
ax4.set_title("(d) Automated QA", fontsize=11, loc="left")
fig.savefig(out / "U04_rose.png", dpi=100, facecolor="white")
print("wrote", out / "U04_rose.png")
