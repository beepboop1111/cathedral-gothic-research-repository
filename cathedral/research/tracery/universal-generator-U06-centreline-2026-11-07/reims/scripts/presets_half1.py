import json, numpy as np
B = json.load(open("out/batch_half1.json"))
groups = {"chevet": ["C1_e","C1_ne","C1_se","N5_3_n","N4_3_e","N5_3_ne","N5_3_nw","S4_3_e","S4_3_se","S5_3_s","S5_3_sw"],
          "choir_aisle_blind_N6e": ["N6_e"], "choir_aisle_N6n": ["N6_n"], "choir_clerestory_C6n": ["C6_n"],
          "choir_clerestory_C7": ["C7_n","C7_s"], "choir_clerestory_C8": ["C8_n","C8_s"], "transept_aisle_S82s": ["S8_2_s"]}
H = {"chevet": [2.796,4.428,2.796,2.796,1.226,2.161,1.258], "choir_aisle_blind_N6e": [4.960,4.339,4.685,4.666,2.163,2.662,1.267],
     "choir_aisle_N6n": [3.421,4.512,3.421,3.421,1.565,2.428,1.323], "choir_clerestory_C6n": [4.748,6.523,4.748,4.748,2.003,3.406,1.971],
     "choir_clerestory_C7": [6.049,6.457,6.049,5.864,2.709,3.803,1.979], "choir_clerestory_C8": [7.419,6.474,7.133,None,2.971,3.803,1.943],
     "transept_aisle_S82s": [4.616,4.776,4.616,4.215,1.653,2.645,1.371]}
Q = ["span x0", "apex above springing", "main radius", "lights total", "lancet radius", "oculus centre above springing", "oculus radius"]
specs, comp = [], {}
sec = json.load(open("/home/claude/beepboop1111/cathedral-gothic-research-repository/cathedral/research/tracery/universal-generator-U06-centreline-2026-11-07/scripts/sections_U06.json"))["reims_c1e_hillson_fit"]
jts = json.load(open("/home/claude/beepboop1111/cathedral-gothic-research-repository/cathedral/research/tracery/universal-generator-U06-centreline-2026-11-07/scripts/joints_U06.json"))["reims_c1e_hillson_fit"]
for gname, ws in groups.items():
    G = [B[w]["gen"] for w in ws if B[w].get("complete") and "gen" in B[w]]
    med = {k: float(np.median([g[k] for g in G])) for k in G[0]}
    surv = [med["x0"], med["yA"] - med["s"], med["f"] * med["x0"], 2 * med["sL"] + med["g"], med["rL"], med["zO"] - med["s"],
            float(np.median([B[w]["gen_derived"]["rO"] for w in ws]))]
    comp[gname] = dict(windows=ws, survey=surv, hillson=H[gname], rms_gen=[B[w]["rms"]["gen"] for w in ws], rms_free=[B[w]["rms"]["free"] for w in ws])
    k = min(max(med["x0"] / 2.9, 1.0), 1.6)
    mm = lambda v: round(1000 * v, 1)
    specs.append(dict(id=f"reims_{gname}_U06", type="centreline",
        title=f"Reims {gname.replace('_', ' ')}: general rule, survey median of {', '.join(ws)} (Hillson ADS 2024)",
        units="mm from the trace's dashed line, axis at 0 (bars, sill, depth TRIAL)", tolerance=0.5,
        centrelines={"rule": "general", "params": {"axis": 0, "span": mm(med["x0"]), "apex": mm(med["yA"]), "f": round(med["f"], 5),
            "light_span": mm(med["sL"]), "mullion_gap": mm(med["g"]), "spring": mm(med["s"]), "lancet_r": mm(med["rL"]), "oculus_z": mm(med["zO"])}},
        bars={"main": round(220 * k), "light": round(180 * k), "oculus": round(180 * k)}, sill=-1500, sill_band=250,
        spandrels="pierced", fork_fill=30, section={"depth": 300, "chamfer": 40}, wall={"margin": 600, "depth": 900, "recess": 250},
        expect={"light": 2, "oculus": 1}))
    print(f"{gname:24} " + "  ".join(f"{q.split()[0][:6]} {s:.3f}/{h if h is None else round(h,3)}" for q, s, h in zip(Q, surv, H[gname])))
D = "/home/claude/beepboop1111/cathedral-gothic-research-repository/cathedral/research/tracery/universal-generator-U06-centreline-2026-11-07/scripts/"
json.dump(specs, open(D + "specs_U06_reims_half1.json", "w"), indent=1)
json.dump({s["id"]: sec for s in specs}, open(D + "sections_U06_reims_half1.json", "w"), indent=1)
json.dump({s["id"]: jts for s in specs}, open(D + "joints_U06_reims_half1.json", "w"), indent=1)
json.dump(dict(quantities=Q, groups=comp), open("out/hillson_vs_survey_half1.json", "w"), indent=1)
