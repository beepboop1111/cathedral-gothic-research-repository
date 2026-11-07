import json, numpy as np
I = json.load(open("out/nave/icp.json")); I.update(json.load(open("out/odd3_icp.json")))
groups = {"nave_aisle_N11": ["N11_n"], "nave_aisle_N12_N15": ["N12_n","N13_n","N14_n","N15_n"], "nave_aisle_N16_N17": ["N16_n","N17_n"],
  "nave_aisle_N18": ["N18_n"], "nave_aisle_N19": ["N19_n"], "nave_clerestory_C10": ["C10_n","C10_s"],
  "nave_clerestory_C11n_C15n": ["C11_n","C12_n","C13_n","C14_n","C15_n"], "nave_clerestory_C11s_C15s": ["C11_s","C12_s","C13_s","C14_s","C15_s"],
  "nave_clerestory_C16n_C17n": ["C16_n","C17_n"], "nave_clerestory_C16s_C17s": ["C16_s","C17_s"], "nave_clerestory_C18n": ["C18_n"],
  "nave_clerestory_C18s": ["C18_s"], "nave_clerestory_C19n": ["C19_n"], "nave_clerestory_C19s": ["C19_s"],
  "transept_aisle_N10_2_w": ["N10_2_w"], "transept_aisle_S10_2_w": ["S10_2_w"], "transept_aisle_S10_2_s": ["S10_2_s"]}
# Hillson (ADS 2024 design drawings): x0, apex above dashed line, main r, lights total, lancet r, oculus centre, oculus r
H = {"nave_aisle_N11": [4.334,4.334,4.334,4.042,1.799,2.523,1.299], "nave_aisle_N12_N15": [4.685,4.685,4.685,4.468,1.925,2.721,1.408],
  "nave_aisle_N16_N17": [4.609,4.774,4.609,4.324,1.925,2.834,1.339], "nave_aisle_N18": [5.168,4.589,4.589,4.740,1.995,2.693,1.356],
  "nave_aisle_N19": [4.764,4.704,4.685,4.431,1.925,2.773,1.343], "nave_clerestory_C10": None,
  "nave_clerestory_C11n_C15n": [6.058,6.568,6.058,5.668,2.527,3.803,1.943], "nave_clerestory_C11s_C15s": None,
  "nave_clerestory_C16n_C17n": [6.026,6.739,6.547,5.816,2.781,3.803,1.977], "nave_clerestory_C16s_C17s": [5.714,6.474,6.474,None,2.706,3.803,1.961],
  "nave_clerestory_C18n": [5.834,6.737,5.834,None,2.675,3.981,2.121], "nave_clerestory_C18s": [6.176,6.890,5.834,5.678,2.554,3.803,2.121],
  "nave_clerestory_C19n": [6.664,6.908,6.196,None,2.603,4.296,2.135], "nave_clerestory_C19s": [6.641,6.928,6.206,None,2.618,4.296,2.136],
  "transept_aisle_N10_2_w": None, "transept_aisle_S10_2_w": None, "transept_aisle_S10_2_s": [4.812,4.640,4.640,4.488,1.995,2.742,1.395]}
D = "/home/claude/beepboop1111/cathedral-gothic-research-repository/cathedral/research/tracery/universal-generator-U06-centreline-2026-11-07/scripts/"
sec = next(iter(json.load(open(D + "sections_U06_reims_half1.json")).values()))
jt = dict(next(iter(json.load(open(D + "joints_U06_reims_half1.json")).values())), keepout_factor=0.0, frame_zone_joints=False)
jt["note"] = "TRIAL; half-2: keep-out factor 0, frame_zone_joints only where the strict setting leaves stones > 2.5 m"
specs, comp = [], {}
for gname, ws in groups.items():
    use = [w for w in ws if I[w].get("ok")] or [w for w in ws if "gen" in I[w]]
    med = {k: float(np.median([I[w]["gen"][k] for w in use])) for k in I[use[0]]["gen"]}
    rO = float(np.median([I[w]["rO"] for w in use]))
    surv = [med["x0"], med["yA"] - med["s"], med["f"] * med["x0"], 2 * med["sL"] + med["g"], med["rL"], med["zO"] - med["s"], rO]
    comp[gname] = dict(windows=ws, used=use, survey=surv, hillson=H[gname], rms=[round(I[w]["rms_mm"], 1) for w in ws])
    k = min(max(med["x0"] / 2.9, 1.0), 1.6); mm = lambda v: round(1000 * v, 1)
    bars = {"main": round(220 * k), "light": round(180 * k), "oculus": round(180 * k)}
    if med["g"] > 0.2: bars["mullion"] = round(1000 * med["g"] + bars["light"])
    note = " Outer order arch not modelled." if gname.endswith("_w") else ""
    specs.append(dict(id=f"reims_{gname}_U06", type="centreline",
        title=f"Reims {gname.replace('_', ' ')}: general rule, survey median of {', '.join(use)} (Hillson ADS 2024).{note}",
        units="mm from the trace's dashed line, axis at 0 (bars, sill, depth TRIAL)", tolerance=0.5,
        centrelines={"rule": "general", "params": {"axis": 0, "span": mm(med["x0"]), "apex": mm(med["yA"]), "f": round(med["f"], 5),
            "light_span": mm(med["sL"]), "mullion_gap": mm(med["g"]), "spring": mm(med["s"]), "lancet_r": mm(med["rL"]), "oculus_z": mm(med["zO"])}},
        bars=bars, sill=-1500, sill_band=250, spandrels="pierced", fork_fill=30, section={"depth": 300, "chamfer": 40},
        wall={"margin": 600, "depth": 900, "recess": 250}, expect={"light": 2, "oculus": 1}))
    h = H[gname]
    print(f"{gname:27} n={len(use)} " + "  ".join(f"{s:.2f}/{'-' if not h or h[i] is None else f'{h[i]:.2f}'}" for i, s in enumerate(surv)))
json.dump(specs, open(D + "specs_U06_reims_half2.json", "w"), indent=1)
json.dump({s["id"]: sec for s in specs}, open(D + "sections_U06_reims_half2.json", "w"), indent=1)
json.dump({s["id"]: jt for s in specs}, open(D + "joints_U06_reims_half2.json", "w"), indent=1)
json.dump(dict(quantities=["span x0","apex above springing","main radius","lights total","lancet radius","oculus centre above springing","oculus radius"], groups=comp), open("out/hillson_vs_survey_half2.json", "w"), indent=1)
