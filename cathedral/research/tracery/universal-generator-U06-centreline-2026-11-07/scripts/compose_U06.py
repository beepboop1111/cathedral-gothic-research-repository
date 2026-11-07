#!/usr/bin/env python3
"""compose_U06.py -- the single U06 review PNG: centreline windows vs Hillson's survey, Blender renders, QA.

usage: python3 -I compose_U06.py <out dir> <png>
"""
import json
import math
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402
from PIL import Image  # noqa: E402
from scipy.optimize import least_squares  # noqa: E402
from shapely import wkt  # noqa: E402

HERE = Path(__file__).resolve().parent
SURVEY = HERE.parent / "survey"
out, png = Path(sys.argv[1]), sys.argv[2]
PPM = 5905.5
NAMES = ["A1", "A2", "O", "L1", "L2", "L3", "L4"]
H = json.loads((SURVEY / "hypotheses.json").read_text())
geo = json.loads((out / "U01/geom_U01.json").read_text())
q1 = json.loads((out / "U01/QA_U01.json").read_text())
q2 = json.loads((out / "U02/QA_U02.json").read_text())["models"]
q3 = json.loads((out / "U03/QA_U03.json").read_text())["models"]
b1 = json.loads((out / "U01/blender_QA_U01.json").read_text())
b3 = json.loads((out / "U03/blender_QA_U01.json").read_text())
reg = json.loads((out / "regression_U06.json").read_text())


def survey(w):
    pts = json.loads((SURVEY / f"pts_{w}.json").read_text())
    fit = json.loads((SURVEY / f"fit_{w}.json").read_text())
    k = pts["px_per_m"] / PPM
    P = np.array([[1000 * p["x"] * k, 1000 * p["z"] * k] for p in pts["points"]])
    groups = {n: P[fit["features"][n]["idx"]] for n in NAMES}
    used = set(i for n in NAMES for i in fit["features"][n]["idx"])
    left_out = np.array([P[i] for i in range(len(P)) if i not in used])
    return groups, left_out


def circles(mid):
    c = json.loads((out / f"U01/{mid}_construction.json").read_text())["construction"]
    cl = c["centrelines"]
    O = c["circles"]["W.O"]
    return {"A1": cl["main"]["CL"], "A2": cl["main"]["CR"], "L1": cl["W.L1"]["CL"], "L2": cl["W.L1"]["CR"],
            "L3": cl["W.L2"]["CL"], "L4": cl["W.L2"]["CR"], "O": [O["centre"][0], O["centre"][1], O["centreline_r"]]}, cl


def rms(circ, groups, dx=0.0, dz=0.0):
    r = np.concatenate([np.hypot(g[:, 0] + dx - circ[n][0], g[:, 1] + dz - circ[n][1]) - circ[n][2]
                        for n, g in groups.items()])
    return float(np.sqrt(np.mean(r ** 2))), r


def draw(ax, mid, groups=None, left=None, dx=0.0, dz=0.0, title=""):
    stone = wkt.loads(geo[mid]["stone"])
    for pg in (list(stone.geoms) if hasattr(stone, "geoms") else [stone]):
        rings = [np.asarray(pg.exterior.coords)] + [np.asarray(r.coords) for r in pg.interiors]
        codes = np.concatenate([[MPath.MOVETO] + [MPath.LINETO] * (len(r) - 2) + [MPath.CLOSEPOLY] for r in rings])
        ax.add_patch(PathPatch(MPath(np.concatenate(rings), codes), facecolor="#d9d4cc", edgecolor="#8f897f", lw=0.6))
    circ, cl = circles(mid)
    for key, a in (("main", cl["main"]), ("W.L1", cl["W.L1"]), ("W.L2", cl["W.L2"])):
        for c, p0, p1 in ((a["CL"], a["spring_l"], a["apex"]), (a["CR"], a["apex"], a["spring_r"])):
            t0, t1 = math.atan2(p0[1] - c[1], p0[0] - c[0]), math.atan2(p1[1] - c[1], p1[0] - c[0])
            if t1 > t0 and c is a["CL"]:
                t1 -= 2 * math.pi
            if c is a["CR"] and t1 > t0:
                t1 -= 2 * math.pi
            t = np.linspace(t0, t1, 120)
            ax.plot(c[0] + c[2] * np.cos(t), c[1] + c[2] * np.sin(t), color="#1f5fbf", lw=1.3)
        for j, p in ((a["jambs"][0], a["spring_l"]), (a["jambs"][1], a["spring_r"])):
            ax.plot([p[0], p[0]], [p[1], -1500], color="#1f5fbf", lw=1.0, ls=(0, (4, 3)))
    o = circ["O"]
    t = np.linspace(0, 2 * np.pi, 300)
    ax.plot(o[0] + o[2] * np.cos(t), o[1] + o[2] * np.sin(t), color="#1f5fbf", lw=1.3, label="U06 centrelines (input)")
    if groups is not None:
        allp = np.concatenate(list(groups.values()))
        ax.plot(allp[:, 0] + dx, allp[:, 1] + dz, "o", ms=2.6, color="black", label="Hillson survey points")
        if left is not None and len(left):
            ax.plot(left[:, 0] + dx, left[:, 1] + dz, "x", ms=5, color="#777777", label="oculus-base points (left out)")
    ax.set_aspect("equal")
    ax.set_xlim(-1900, 1900)
    ax.set_ylim(-1800, 4750)
    ax.tick_params(labelsize=8)
    ax.set_title(title, fontsize=11, loc="left")
    ax.legend(fontsize=8, loc="upper right", framealpha=0.95)


fig = plt.figure(figsize=(24, 15.5), dpi=100, facecolor="white")
gs = fig.add_gridspec(2, 4, height_ratios=[1.0, 0.78], hspace=0.12, wspace=0.08, left=0.03, right=0.99, top=0.93, bottom=0.02)
fig.suptitle("U06 centreline mode — tracery laid out on interdos centrelines, bars added around them; U02 mouldings and "
             "U03 joints run on it  (EXPERIMENTAL, 2026-11-07)", fontsize=16, x=0.03, y=0.985, ha="left", weight="bold")

ax0 = 1000 * H["C1_e"]["hillson"]["values"]["axis"]
g, left = survey("C1_e")
g = {n: v - [ax0, 0] for n, v in g.items()}
left = left - [ax0, 0]
c_h, _ = circles("reims_c1e_hillson_fit")
c_s, _ = circles("reims_c1e_survey")
r_h, r_s = rms(c_h, g)[0], rms(c_s, g)[0]
draw(fig.add_subplot(gs[0, 0]), "reims_c1e_hillson_fit", g, left,
     title=f"(a) C1.e — Hillson's rule, 5 values\nsurvey RMS {r_h:.1f} mm")
draw(fig.add_subplot(gs[0, 1]), "reims_c1e_survey", g, left,
     title=f"(b) C1.e — surveyed centreline circles\nsurvey RMS {r_s:.1f} mm")
# Hillson's own figure numbers, placed on the N5.3.n survey by translation only
gn, leftn = survey("N5_3_n")
c_f, _ = circles("reims_n53n_hillson_figure")
fx = least_squares(lambda t: rms(c_f, gn, t[0], t[1])[1], [-1000 * H["N5_3_n"]["hillson"]["values"]["axis"], 140.0]).x
r_f = rms(c_f, gn, fx[0], fx[1])[0]
draw(fig.add_subplot(gs[0, 2]), "reims_n53n_hillson_figure", gn, leftn, fx[0], fx[1],
     title=f"(c) N5.3.n — Hillson's published figure numbers\nplaced by translation only: survey RMS {r_f:.1f} mm")

# renders
ax = fig.add_subplot(gs[0, 3])
im = Image.open(out / "U03/closeup_U02.png").convert("RGB")
ax.imshow(im)
ax.axis("off")
ax.set_title("(d) U02 mouldings + U03 joints on the C1.e oculus\n(Blender 5.2.3 render of the re-imported GLB)", fontsize=11,
             loc="left")
ax = fig.add_subplot(gs[1, 0:2])
im = Image.open(out / "U03/render_U02.png").convert("RGB")
w, h = im.size
ax.imshow(im.crop((int(0.12 * w), 0, int(0.88 * w), h)))
ax.axis("off")
ax.set_title("(e) The three U06 windows after U01 -> U02 -> U03 (stones, orders, mouldings), re-imported in Blender:"
             "  N5.3.n figure | C1.e Hillson rule | C1.e survey", fontsize=11, loc="left")

# QA + findings
ax = fig.add_subplot(gs[1, 2:4])
ax.axis("off")
ids = ["reims_n53n_hillson_figure", "reims_c1e_hillson_fit", "reims_c1e_survey"]
short = {"reims_n53n_hillson_figure": "N5.3.n figure", "reims_c1e_hillson_fit": "C1.e rule", "reims_c1e_survey": "C1.e survey"}
okc = lambda ch: f"{sum(c['ok'] for c in ch)}/{len(ch)}"
rows = [f"{'model':14}{'U01':>7}{'U02':>7}{'U03':>7}{'stones':>8}{'largest':>9}{'survey':>9}"]
rms_of = {"reims_n53n_hillson_figure": r_f, "reims_c1e_hillson_fit": r_h, "reims_c1e_survey": r_s}
for mid in ids:
    rows.append(f"{short[mid]:14}{okc(q1['models'][mid]['checks']):>7}{okc(q2[mid]['checks']):>7}{okc(q3[mid]['checks']):>7}"
                f"{q3[mid]['blocks']:>8}{q3[mid]['largest'] / 1000:>8.2f}m{rms_of[mid]:>7.1f}mm")
tot1 = sum(len(m["checks"]) for m in q1["models"].values())
ok1 = sum(sum(c["ok"] for c in m["checks"]) for m in q1["models"].values())
gaps = json.loads((out / "U01/reims_c1e_survey_construction.json").read_text())["construction"]["centrelines"]["gaps"]
txt = [
    "QA (all automated; same tests as U01-U05)",
    *rows,
    f"U01 first-pass fit of C1.e for comparison: 35.4 mm (bars 240/120).",
    "",
    "Validation",
    f"Technical : U01-U05 code unchanged on disk; run_U06 wraps the runners. All U01 checks {ok1}/{tot1};",
    f"            St-Leu regression {sum(t['ok'] for t in q1['regression']['tests'])}/{len(q1['regression']['tests'])};"
    f" bar_2light_sexfoil U02 and U03 {'IDENTICAL' if not reg['U02'] and not reg['U03'] else 'DIFFER'} to the archived results.",
    f"            Blender re-import: U01 stage {'clean' if b1.get('all_ok') else 'SEE QA'}, U03 stones {'clean' if b3.get('all_ok') else 'SEE QA'}"
    " (0 nonmanifold / degenerate / self-intersecting).",
    "Geometric : centrelines are the input, so the survey RMS is the construction's own fit (a)/(b)/(c).",
    "            Hillson rule checks exact: oculus tangent to lancets, forks at mullion and jambs, rise = H/4.",
    f"            Survey C1.e forks: mullion {gaps['mullion_fork']:.0f} mm, jambs {gaps['jamb_fork_left']:.0f} / "
    f"{gaps['jamb_fork_right']:.0f} mm, oculus-lancet {gaps['oculus_L2']:.0f} / {gaps['oculus_L3']:.0f} mm.",
    "Architect.: bars 220 / 180 / 180, depth 300, mouldings, joints, 1.5 m lights below the impost are TRIAL",
    "            (no Reims sections in the dataset). Joints: voussoir 360, keep-out 1.0 x bar (copied 520 / 1.6",
    "            left 3.1-3.4 m stones where forked bars merge).",
    f"Historical: Hillson's published numbers fit N5.3.n to {r_f:.1f} mm by translation alone (c);",
    "            refitting its 5 values gives 9.4 mm (first pass). Oculus cusps not in the survey: none drawn.",
    "Structural: not assessed.",
    "",
    "U06 additions: centreline arches (rules or circles), bars offset both ways, forks resolved by union,",
    "jamb strips of forked lights merged into the main jamb, tolerant jamb test (U01 rounding bug), and one",
    "U03 extension: the frame keeps its courses up to a stilted main arch's own springing.",
]
ax.text(0.0, 1.0, "\n".join(txt), fontsize=10.9, family="monospace", va="top")
fig.savefig(png, dpi=100, facecolor="white")
print(f"wrote {png}; survey RMS: C1.e rule {r_h:.2f} mm, C1.e survey {r_s:.2f} mm, N5.3.n figure {r_f:.2f} mm "
      f"(translation {fx[0]:.1f}, {fx[1]:.1f} mm)")
