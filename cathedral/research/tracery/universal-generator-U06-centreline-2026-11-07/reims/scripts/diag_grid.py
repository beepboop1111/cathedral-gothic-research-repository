import json, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
wins = open(sys.argv[1]).read().split(); out = sys.argv[2]
n = len(wins); cols = 6; rows = (n + cols - 1) // cols
fig, axs = plt.subplots(rows, cols, figsize=(cols * 3.6, rows * 4.4), dpi=80)
cl = plt.cm.tab10(np.arange(10))
for ax, w in zip(axs.flat, wins):
    pts = json.load(open(f"out/pts_{w}.json")); fit = json.load(open(f"out/fit_{w}.json"))
    P = np.array([[p["x"], p["z"]] for p in pts["points"]])
    ax.plot(P[:, 0], P[:, 1], "x", color="0.6", ms=3)
    for i, (nm, f) in enumerate(fit["features"].items()):
        Q = P[f["idx"]]; ax.plot(Q[:, 0], Q[:, 1], "o", ms=2.5, color=cl[i])
        t = np.linspace(0, 2 * np.pi, 300); ax.plot(f["cx"] + f["r"] * np.cos(t), f["cz"] + f["r"] * np.sin(t), lw=0.4, color=cl[i])
    ax.set_xlim(P[:, 0].min() - .3, P[:, 0].max() + .3); ax.set_ylim(P[:, 1].min() - .3, P[:, 1].max() + .3)
    ax.set_aspect("equal"); ax.set_title(f"{w}  un={fit['unassigned']}", fontsize=9); ax.tick_params(labelsize=6)
for ax in list(axs.flat)[n:]: ax.axis("off")
fig.tight_layout(); fig.savefig(out)
