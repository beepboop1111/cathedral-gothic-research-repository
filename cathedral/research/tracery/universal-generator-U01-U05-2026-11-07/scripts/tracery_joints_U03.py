#!/usr/bin/env python3
"""tracery_joints_U03.py -- EXPERIMENTAL masonry jointing (U03) for U02 sectioned tracery.

Reuses the buttress generator's coursing rule (equal course heights, constant-angle voussoirs,
explicit open joint) and applies it to tracery:
  * frame (bar mode): jambs coursed with horizontal beds, sill split under principal mullions if
    too long, arch cut in voussoirs radial to its own centres (crown joint where free);
  * tracery: mullions coursed on the same beds; every sub-arch band cut by joints radial to its
    centre; oculus rings cut at lobe centres (each cusp stays in one stone with its ring segment);
    intersecting arcs cut radially; no joint inside a keep-out zone around junctions (springers,
    tangencies, crossings), so junctions stay inside single stones;
  * plate mode: coursed jambs/mullion + joints radiating from the foil centre that reach the outline
    without crossing another opening.
Each stone spans every order present at its location: orders become stepped surfaces inside one
block (height-field mesh with vertical risers), not separate stones. All sizes are TRIAL values.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
import triangle as tri_lib
import trimesh
from scipy.spatial import cKDTree
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

import tracery_section_U02 as U
import tracery_universal_U01 as T

VERSION = "U03-experimental"


def _clean_piece(p, tol):
    d = 0.02 * tol
    o = p.buffer(-d, join_style="mitre", mitre_limit=2.0).buffer(d, join_style="mitre", mitre_limit=2.0).intersection(p)
    return [U._clean(g, tol) for g in T.polys(o)]


def block_mesh(B, cons, isos, label_fn, orders, voids_u, zg, size, tol):
    """Closed solid over block B. Triangles carry an order label; each order has its own height
    field (half-depth minus moulding drop); vertical risers join different orders and the outer
    walls close the block. Columns of vertices at shared 2D points keep everything conforming."""
    q = max(1e-9 * size, 1e-3 * tol)
    key = lambda x, y: (round(x / q), round(y / q))
    Bin = B.buffer(-0.05 * tol, join_style="mitre", mitre_limit=2.0)
    lines, level = list(shapely.get_parts(B.boundary)), {}

    def add(g):
        if g.is_empty:
            return []
        g = shapely.line_merge(g) if g.geom_type in ("MultiLineString",) else g
        return [p for p in shapely.get_parts(g) if p.geom_type in ("LineString", "LinearRing") and p.length > 0]

    nb = len(lines)
    iso_lines = []
    for k, lst in isos.items():
        level[k] = {}
        for d, g in lst:
            for p in add(g.intersection(Bin)) if not Bin.is_empty else []:
                for x, y in p.coords:
                    level[k][key(x, y)] = d
                iso_lines.append(p)
    lines = lines + iso_lines
    if cons is not None and not Bin.is_empty:  # keep only outline segments that separate two different orders
        segs_ = []
        for g in add(cons.intersection(Bin)):
            c = np.asarray(g.coords)
            if len(c) < 2:
                continue
            mid = 0.5 * (c[1:] + c[:-1])
            dv = c[1:] - c[:-1]
            nrm = np.c_[-dv[:, 1], dv[:, 0]] / np.maximum(np.linalg.norm(dv, axis=1), 1e-30)[:, None]
            dlt = 0.2 * tol
            la = label_fn(mid[:, 0] + dlt * nrm[:, 0], mid[:, 1] + dlt * nrm[:, 1])
            lb = label_fn(mid[:, 0] - dlt * nrm[:, 0], mid[:, 1] - dlt * nrm[:, 1])
            segs_ += [LineString([c[i], c[i + 1]]) for i in np.where(la != lb)[0]]
        if segs_:
            lines += add(shapely.line_merge(unary_union(segs_)))
    simp = lambda L_: L_[:nb] + [g.simplify(0.05 * tol) for g in L_[nb:]]

    def away(L_):  # interior constraints kept >= tol/2 from the stone edge (exact coincidences break Triangle)
        keep_ = L_[:nb]
        Bd = B.boundary
        for g in L_[nb:]:
            c = np.asarray(g.coords)
            ok = shapely.distance(shapely.points(c), Bd) >= 0.5 * tol
            run = []
            for xy, f in zip(c, ok):
                if f:
                    run.append(xy)
                else:
                    if len(run) >= 2:
                        keep_.append(LineString(run))
                    run = []
            if len(run) >= 2:
                keep_.append(LineString(run))
        return keep_

    tries = [(lines, False), (lines, True), (simp(lines), True), (away(simp(lines)), True),
             (lines[:nb] + iso_lines, False), (lines[:nb], False)]
    for attempt, (ln, renode) in enumerate(tries):  # 0-3 full order linework, 4 no member outlines, 5 boundary only
        try:
            for _ in range(4):  # interior constraint vertices that only make slivers are removed, then retried
                out = _tri_block(B, ln, level, key, label_fn, orders, voids_u, zg, size, tol, q,
                                 fallback=0 if attempt <= 3 else attempt - 3, renode=renode)
                if not out[2]["sliver_keys"]:
                    break
                bad = out[2]["sliver_keys"]
                kept = ln[:nb]
                for g in ln[nb:]:
                    c = [xy for xy in np.asarray(g.coords) if key(*xy) not in bad]
                    if len(c) >= 2:
                        kept.append(LineString(c))
                ln = kept
            out[2].pop("sliver_keys")
            return out
        except RuntimeError:
            continue
    raise RuntimeError("block triangulation failed")


def _tri_block(B, lines, level, key, label_fn, orders, voids_u, zg, size, tol, q, fallback, renode=False):
    lines = [g for g in shapely.get_parts(unary_union(lines)) if g.length > 0]  # node crossings exactly
    vid, V2, segs = {}, [], []
    for g in lines:
        ids = []
        for x, y in np.asarray(g.coords):
            k = key(x, y)
            if k not in vid:
                vid[k] = len(V2)
                V2.append((x, y))
            ids.append(vid[k])
        segs += [(a, b) for a, b in zip(ids[:-1], ids[1:]) if a != b]
    V2 = np.asarray(V2)
    rep = np.arange(len(V2))

    def root(i):
        while rep[i] != i:
            rep[i] = rep[rep[i]]
            i = rep[i]
        return i

    for i, j in sorted(cKDTree(V2).query_pairs(0.02 * tol)):
        ri, rj = root(i), root(j)
        if ri != rj:
            rep[max(ri, rj)] = min(ri, rj)
    rep = np.array([root(i) for i in range(len(V2))])
    keep = np.unique(rep)
    remap = -np.ones(len(V2), np.int64)
    remap[keep] = np.arange(len(keep))
    for k in level:
        add_ = {}
        for i in range(len(V2)):
            kk = key(*V2[i])
            if kk in level[k]:
                add_.setdefault(key(*V2[rep[i]]), level[k][kk])
        level[k].update(add_)
    segs = sorted({tuple(sorted((int(remap[rep[a]]), int(remap[rep[b]])))) for a, b in segs})
    segs = [s for s in segs if s[0] != s[1]]
    V2 = V2[keep]
    if renode:  # merging can make segments cross or overlap again: split them at every crossing once more
        net = unary_union([LineString([V2[a_], V2[b_]]) for a_, b_ in segs])
        vid2, V3, segs = {}, [], []
        for g in shapely.get_parts(net):
            ids = []
            for x, y in np.asarray(g.coords):
                k = (x, y)
                if k not in vid2:
                    vid2[k] = len(V3)
                    V3.append((x, y))
                ids.append(vid2[k])
            segs += [(a_, b_) for a_, b_ in zip(ids[:-1], ids[1:]) if a_ != b_]
        V2 = np.asarray(V3)
    inp = dict(vertices=V2, segments=np.asarray(segs, np.int64))
    if B.interiors:
        inp["holes"] = np.asarray([Polygon(r).representative_point().coords[0] for r in B.interiors])
    res = tri_lib.triangulate(inp, "pQ")
    Vt, F = np.asarray(res["vertices"]), np.asarray(res["triangles"], np.int64)
    if len(Vt) > len(V2):  # Steiner points can land on existing vertices: merge and drop collapsed triangles
        rp = np.arange(len(Vt))
        for i, j in sorted(cKDTree(Vt).query_pairs(q)):
            rp[max(i, j)] = rp[min(i, j)]
        F = rp[F]
        F = F[(F[:, 0] != F[:, 1]) & (F[:, 1] != F[:, 2]) & (F[:, 0] != F[:, 2])]
    a = Vt[F]
    s = (a[:, 1, 0] - a[:, 0, 0]) * (a[:, 2, 1] - a[:, 0, 1]) - (a[:, 1, 1] - a[:, 0, 1]) * (a[:, 2, 0] - a[:, 0, 0])
    F[s < 0] = F[s < 0][:, ::-1]
    bkeys = {key(x, y) for g in shapely.get_parts(B.boundary) for x, y in np.asarray(g.coords)}
    sliver_keys = {key(*Vt[v]) for t in F[np.abs(s) < 1e-10 * size * size] for v in t} - bkeys
    cen = Vt[F].mean(1)
    lab = label_fn(cen[:, 0], cen[:, 1])
    eu = shapely.distance(shapely.points(Vt), voids_u)
    verts, cf, cb, col = [], {}, {}, {}

    def h_of(v, k):
        o = orders[k]
        d = level.get(k, {}).get(key(*Vt[v]), eu[v])
        return o["H"] - float(np.interp(d, o["prof"][:, 0], o["prof"][:, 1], right=0.0))

    def copy(v, z):
        kk = (v, round(z / q))
        cv = col.setdefault(v, {})
        if kk not in cv:
            near = [i for i in cv.values() if abs(verts[i][2] - z) <= q]  # same height within q -> same vertex
            if near:
                cv[kk] = near[0]
                return near[0]
            cv[kk] = len(verts)
            verts.append((Vt[v][0], Vt[v][1], z))
        return cv[kk]

    for t, k in zip(F, lab):
        for v in t:
            if (v, k) not in cf:
                h = h_of(v, k)
                cf[(v, k)] = copy(v, zg + h)
                cb[(v, k)] = copy(v, zg - h)
    Z = lambda i: verts[i][2]
    faces = [[cf[(v, k)] for v in t] for t, k in zip(F, lab)]
    faces += [[cb[(t[0], k)], cb[(t[2], k)], cb[(t[1], k)]] for t, k in zip(F, lab)]
    edges = {}
    for t, k in zip(F, lab):
        for u_, w_ in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            edges.setdefault((min(u_, w_), max(u_, w_)), []).append((u_, w_, k))
    eps = 1e-7 * size

    def chain(v, lo, hi):
        pts = sorted(((Z(i), i) for i in set(col[v].values()) if lo - eps <= Z(i) <= hi + eps), reverse=True)
        return pts

    def wall(u_, w_, iu, iw):
        cu, cw = chain(u_, *iu), chain(w_, *iw)
        i = j = 0
        while i < len(cu) - 1 or j < len(cw) - 1:
            adv_u = j >= len(cw) - 1 or (i < len(cu) - 1 and cu[i + 1][0] >= cw[j + 1][0])
            if adv_u:
                faces.append([cu[i][1], cu[i + 1][1], cw[j][1]])
                i += 1
            else:
                faces.append([cw[j][1], cu[i][1], cw[j + 1][1]])
                j += 1

    violations = 0
    for ent in edges.values():
        if len(ent) == 1:
            u_, w_, k = ent[0]
            wall(u_, w_, (Z(cb[(u_, k)]), Z(cf[(u_, k)])), (Z(cb[(w_, k)]), Z(cf[(w_, k)])))
        elif len(ent) == 2:
            for (u_, w_, ka), (_, _, kb) in ((ent[0], ent[1]), (ent[1], ent[0])):
                if ka == kb:
                    continue
                du = Z(cf[(u_, ka)]) - Z(cf[(u_, kb)])
                dw = Z(cf[(w_, ka)]) - Z(cf[(w_, kb)])
                if du >= -eps and dw >= -eps and max(du, dw) > eps:
                    wall(u_, w_, (Z(cf[(u_, kb)]), Z(cf[(u_, ka)])), (Z(cf[(w_, kb)]), Z(cf[(w_, ka)])))
                    wall(u_, w_, (Z(cb[(u_, ka)]), Z(cb[(u_, kb)])), (Z(cb[(w_, ka)]), Z(cb[(w_, kb)])))
                elif (du < -eps and dw > eps) or (du > eps and dw < -eps):
                    violations += 1
        else:
            violations += 1
    areas = {}
    for sv, k in zip(np.abs(s) / 2, lab):
        areas[int(k)] = areas.get(int(k), 0.0) + float(sv)
    return np.asarray(verts), np.asarray(faces, np.int64), dict(violations=violations, label_areas=areas,
                                                                steiner=len(Vt) - len(V2), fallback=fallback,
                                                                sliver_keys=sliver_keys)


class Jointed:
    simplify_factor = 0.0
    def __init__(self, spec, section, joints, scale=1.0, model_cls=None):
        self.u = U.Sectioned(spec, section, scale, model_cls=model_cls)
        self.m = m = self.u.m
        L = lambda v: float(v) * scale
        self.js = joints
        self.jw, self.keep = L(joints["joint_width"]), L(joints["keepout"])
        self.kf = float(joints.get("keepout_factor", 1.6))  # junction keep-out radius / narrower member width
        self.course, self.vous, self.lmin = L(joints["course"]), L(joints["voussoir"]), L(joints["min_block"])
        self.sill_max = L(joints.get("sill_max", 1e18))
        self.max_block = L(joints.get("max_block", 1e18))
        self.e = 2 * self.jw + 0.5 * m.tol
        self.checks, self.joints, self.notes = [], [], []
        self.mem = {x["name"]: x for x in m.members}
        self.zones = self._zones()
        self._make_joints()
        self._blocks()
        self._mesh()

    def check(self, name, ok, kind="geometric", detail=""):
        self.checks.append(dict(kind=kind, name=name, ok=bool(ok), detail=detail))

    # ---------------- joint layout
    def _zones(self):
        m = self.m
        if m.mode != "bar":
            return []
        out = []
        for a, b, t in m.junctions:
            A, B = self.mem[a], self.mem[b]
            if "foil_cusps" in (A["kind"], B["kind"]):
                continue
            I = A["poly"].intersection(B["poly"])
            wid = lambda P: 2 * P.area / P.length  # strip width of a band/ring/frame member
            r = self.kf * min(wid(A["poly"]), wid(B["poly"]))
            if t == "overlap":
                out.append(I.buffer(r))
            else:
                c = shapely.get_coordinates(I)
                if len(c):
                    top = c[np.argmax(c[:, 1])]
                    if top[1] > m.sill + m.tol:
                        out.append(Point(top).buffer(r))
        return out

    def _free_in(self, seg, member_buf, zones):
        return seg.within(member_buf) and not any(z.intersects(seg) for z in zones)

    def _free(self, seg, member_buf):
        return seg.within(member_buf) and not any(z.intersects(seg) for z in self.zones)

    def _radial(self, c, ri, ro, th):
        u = np.array([math.cos(th), math.sin(th)])
        p = np.array([c.x, c.z])
        return LineString([p + (ri - self.e) * u, p + (ro + self.e) * u])

    def _arch_joints(self, name, left, right, crown, member, region, zones=None):
        """Voussoir joints: greedy along the left half (springing -> apex), mirrored by fraction on
        the right half; crown joint if free. left/right = (circle, r_in, r_out, th_from, th_to)."""
        buf = member.buffer(1.5 * self.e)
        zs = self.zones if zones is None else zones  # U06 opt-in: frame arch may ignore junction keep-outs
        cL, ri, ro, a0, a1 = left
        rm, n = 0.5 * (ri + ro), 600
        stot = abs(a1 - a0) * rm
        last, ts = 0.0, []
        for th in np.linspace(a0, a1, n)[1:-1]:
            sv = abs(th - a0) * rm
            if sv - last >= 0.9 * self.vous and stot - sv >= self.lmin and self._free_in(self._radial(cL, ri, ro, th), buf, zs):
                ts.append((th - a0) / (a1 - a0))
                last = sv
        cR, rri, rro, b0, b1 = right
        blocked = False
        for t in ts:
            self._add(region, "voussoir", name, self._radial(cL, ri, ro, a0 + t * (a1 - a0)), cL)
            th = b1 + t * (b0 - b1)
            sg = self._radial(cR, rri, rro, th)
            if self._free_in(sg, buf, zs):
                self._add(region, "voussoir", name, sg, cR)
            else:
                blocked = True
                self.notes.append(f"{name}: mirrored joint blocked (asymmetric)")
        if self.js.get("free_right") and (blocked or not ts):  # U06 opt-in: own greedy pass on the right half
            self.joints = [j for j in self.joints if not (j["member"] == name and j["kind"] == "voussoir"
                                                          and j["centre"] == (cR.x, cR.z) and cR is not cL)]
            rmR = 0.5 * (rri + rro)
            stR, lastR = abs(b0 - b1) * rmR, 0.0
            for th in np.linspace(b1, b0, n)[1:-1]:
                sv = abs(th - b1) * rmR
                sg = self._radial(cR, rri, rro, th)
                if sv - lastR >= 0.9 * self.vous and stR - sv >= self.lmin and self._free_in(sg, buf, zs):
                    self._add(region, "voussoir", name, sg, cR)
                    lastR = sv
        if crown is not None and self._free_in(crown, buf, zs) and (stot - (ts[-1] * stot if ts else 0)) >= self.lmin:
            self._add(region, "crown", name, crown, None)

    def _add(self, region, kind, name, seg, centre):
        self.joints.append(dict(region=region, kind=kind, member=name, seg=seg,
                                centre=None if centre is None else (centre.x, centre.z)))

    def _make_joints(self):
        m, e = self.m, self.e
        b0 = m.outline.bounds
        recs = m.con["arches"]
        springs = [min(r["spring_l"][1], r["spring_r"][1]) for nm, r in recs.items() if nm != "outline"]
        if m.mode == "bar":
            z0 = m.sill
        else:
            z0 = min(float(v["sill"]) * m.k for v in m.spec["voids"] if "sill" in v)
        ztop = min(springs) - self.keep
        n = max(1, math.ceil((ztop - z0) / self.course))
        tc = self.js.get("tracery_course")
        for i in range(n + 1):  # equal courses, buttress-style
            z = z0 + i * (ztop - z0) / n
            sg = LineString([(b0[0] - e, z), (b0[2] + e, z)])
            regs = ("plate",) if m.mode != "bar" else (("frame",) if tc else ("frame", "tracery"))
            for region in regs:
                self._add(region, "bed", "course", sg, None)
        if tc and m.mode == "bar":  # tracery uprights: their own longer pieces, beds staggered from the wall courses
            nt = max(1, math.ceil((ztop - z0) / (tc * m.k)))
            for i in range(nt + 1):
                z = z0 + i * (ztop - z0) / nt
                self._add("tracery", "bed", "upright", LineString([(b0[0] - e, z), (b0[2] + e, z)]), None)
        if m.mode == "bar":
            W, O = m.W, m.O
            frame = self.mem["frame"]["poly"]
            self._arch_joints("frame", (W.CL, W.CL.r, O.CL.r, math.atan2(W.sl[1] - W.CL.z, W.sl[0] - W.CL.x),
                                        math.atan2(W.apex[1] - W.CL.z, W.apex[0] - W.CL.x)),
                              (W.CR, W.CR.r, O.CR.r, math.atan2(W.apex[1] - W.CR.z, W.apex[0] - W.CR.x),
                               math.atan2(W.sr[1] - W.CR.z, W.sr[0] - W.CR.x)),
                              LineString([(W.apex[0], W.apex[1] - e), (O.apex[0], O.apex[1] + e)]), frame, "frame",
                              zones=[] if self.js.get("frame_zone_joints") else None)
            if b0[2] - b0[0] > self.sill_max:
                fill = m.spec["fill"]
                nn = int(fill["n"])
                if self.js.get("sill_split"):
                    nn = max(nn, math.ceil((b0[2] - b0[0]) / self.sill_max))
                for k in range(1, nn):
                    x = W.xl + k * (W.xr - W.xl) / nn
                    self._add("frame", "sill", "sill", LineString([(x, b0[1] - e), (x, m.sill + e)]), None)
            for nm, r in recs.items():
                if nm in ("W", "outline") or "band" not in r:
                    continue
                E = T.Arch(r["jambs"][0], r["jambs"][1], T.Circle(*r["CL"]), T.Circle(*r["CR"]))
                b = r["band"]
                I = E.off(-b)
                ang = lambda c, p: math.atan2(p[1] - c.z, p[0] - c.x)
                self._arch_joints(nm, (E.CL, E.CL.r - b, E.CL.r, ang(E.CL, E.sl), ang(E.CL, E.apex)),
                                  (E.CR, E.CR.r - b, E.CR.r, ang(E.CR, E.apex), ang(E.CR, E.sr)),
                                  LineString([(E.apex[0], I.apex[1] - e), (E.apex[0], E.apex[1] + e)]),
                                  self.mem[nm + ".band"]["poly"], "tracery")
            for nm, c in m.con["circles"].items():
                if "r_outer" in c:  # oculus ring: joints at lobe centres
                    cx, cz = c["centre"]
                    rho, b = c["r_outer"], c["band"]
                    if "foil" in c:
                        angs = [math.atan2(l[1] - cz, l[0] - cx) for l in c["foil"]["lobes"]]
                    else:
                        nr = 16 if not self.js.get("ring_dense") else 8 * max(16, math.ceil(2 * math.pi * rho / self.vous))
                        angs = list(np.linspace(0, 2 * math.pi, nr, endpoint=False))
                    buf = self.mem[nm + ".ring"]["poly"].buffer(1.5 * e)
                    if self.js.get("ring_zone_joints"):  # U06 opt-in: ring clipped where it runs along the frame
                        buf = self.mem[nm + ".ring"]["poly"].union(self.mem["frame"]["poly"]).buffer(1.5 * e)
                    acc = []
                    rz = self.js.get("ring_zone_joints")
                    def rseg(th):
                        sg = self._radial(T.Circle(cx, cz, rho), rho - b, rho, th)
                        if not rz:
                            return sg
                        lg = self._radial(T.Circle(cx, cz, rho), rho - b, rho + 4 * b, th).intersection(buf)
                        parts = [p for p in getattr(lg, "geoms", [lg]) if p.geom_type == "LineString" and not p.is_empty]
                        return min(parts, key=lambda p: p.distance(sg)) if parts else sg
                    for th in sorted(a % (2 * math.pi) for a in angs):
                        sg = rseg(th)
                        gap = self.lmin if not (self.js.get("ring_dense") and "foil" not in c) else 0.9 * self.vous
                        if self._free_in(sg, buf, [] if self.js.get("ring_zone_joints") else self.zones) and (not acc or (th - acc[-1]) * (rho - b / 2) >= gap):
                            acc.append(th)
                    if len(acc) > 1 and (acc[0] + 2 * math.pi - acc[-1]) * (rho - b / 2) < self.lmin:
                        acc.pop()
                    for th in acc:
                        sg = rseg(th)
                        self._add("tracery", "ring", nm, sg, T.Circle(cx, cz, rho))
                        if rz and sg.length > b + 3 * e:  # cut the fused frame strip too
                            self._add("frame", "voussoir", "frame", sg, T.Circle(cx, cz, rho))
                elif "centre_line" in c:  # intersecting arc: radial joints from its foot upward
                    cc = T.Circle(*c["centre_line"])
                    b = c["band"]
                    buf = self.mem[nm]["poly"].buffer(1.5 * e)
                    ths = np.linspace(math.pi, 0, 800) if nm.endswith("r") else np.linspace(0, math.pi, 800)
                    valid = [self._radial(cc, cc.r - b, cc.r + b, th).within(buf) for th in ths]
                    if not any(valid):
                        continue
                    last_i = max(i for i, v in enumerate(valid) if v)
                    s = np.abs(ths - ths[0]) * cc.r
                    last = 0.0
                    for i, th in enumerate(ths[:last_i]):
                        sg = self._radial(cc, cc.r - b, cc.r + b, th)
                        if valid[i] and s[i] - last >= 0.9 * self.vous and s[last_i] - s[i] >= self.lmin \
                                and self._free(sg, buf):
                            self._add("tracery", "voussoir", nm, sg, cc)
                            last = s[i]
        else:  # plate: joints radiating from each foil centre that reach the outline unobstructed
            for v in m.spec["voids"]:
                if v["role"] != "foil":
                    continue
                if "circles" in v:
                    cs = [T.Circle(*[x * m.k for x in c]) for c in v["circles"]]
                    ctr, lobes = cs[0], cs[1:]
                else:
                    g = v["regular"]
                    ctr = T.Circle(g["centre"][0] * m.k, g["centre"][1] * m.k, 0)
                    lobes = [T.Circle(ctr.x + math.cos(math.radians(g.get("phase_deg", 0)) + 2 * math.pi * j / g["n"]),
                                      ctr.z + math.sin(math.radians(g.get("phase_deg", 0)) + 2 * math.pi * j / g["n"]), 0)
                             for j in range(g["n"])]
                others = unary_union([x["poly"] for x in m.voids if x["id"] != v.get("name")])
                for lb in lobes:
                    th = math.atan2(lb.z - ctr.z, lb.x - ctr.x)
                    sg = LineString([(ctr.x, ctr.z), (ctr.x + 2 * m.size * math.cos(th), ctr.z + 2 * m.size * math.sin(th))])
                    if not sg.intersects(others):
                        self._add("plate", "ray", v.get("name"), sg, ctr)

    # ---------------- blocks
    def _split(self, region_poly, lines):
        strips = []
        reg_buf = region_poly.buffer(self.e)
        for ln in lines:
            g = ln.intersection(reg_buf)
            if not g.is_empty:
                strips.append(g.buffer(self.jw / 2, cap_style="flat", join_style="mitre"))
        strip = unary_union(strips) if strips else Polygon()
        cut = region_poly.difference(strip)
        min_area = max((10 * self.m.tol) ** 2, 1e-7 * self.m.outline.area)
        out, dropped = [], 0.0
        for p in T.polys(cut):
            for g in _clean_piece(p, self.m.tol):
                if self.simplify_factor > 0:  # drop near-collinear boundary points (sliver-free caps)
                    g2 = g.simplify(self.simplify_factor * self.m.tol, preserve_topology=True)
                    g = g2 if g2.is_valid and abs(g2.area - g.area) <= 1e-6 * g.area else g
                if g.area >= min_area:
                    out.append(g)
                else:
                    dropped += g.area
        return out, strip.intersection(region_poly).area, dropped

    def _blocks(self):
        m = self.m
        S = m.stone
        fix = lambda g: g if g.geom_type in ("Polygon", "MultiPolygon") else unary_union(T.polys(g))
        if m.mode == "bar":
            regions = {"frame": fix(S.difference(m.Wp)), "tracery": fix(S.intersection(m.Wp))}
        else:
            regions = {"plate": S}
        self.blocks, self.mortar, self.dropped = [], 0.0, 0.0
        if self.js.get("chassis_joint") and m.mode == "bar":  # open joint where the tracery layer meets the wall frame
            F, Tr = regions["frame"], regions["tracery"]
            iface = F.boundary.intersection(Tr.boundary)
            iface = unary_union([g for g in shapely.get_parts(iface) if g.length > 0])
            if not iface.is_empty:
                cut = iface.buffer(self.jw / 2, cap_style="flat", join_style="mitre")
                for rn in ("frame", "tracery"):
                    before = regions[rn].area
                    regions[rn] = fix(regions[rn].difference(cut))
                    self.mortar += before - regions[rn].area
                self.chassis_len = iface.length
        for rn, rp in regions.items():
            pcs, mort, drop = self._split(rp, [j["seg"] for j in self.joints if j["region"] == rn])
            self.mortar += mort
            self.dropped += drop
            q = 1e-6 * m.size
            pcs.sort(key=lambda g: (-round(g.centroid.y / q), round(g.centroid.x / q)))
            for i, g in enumerate(pcs):
                self.blocks.append(dict(region=rn, poly=g, name=f"stone_{rn[0].upper()}{i + 1:03d}"))
        tot = sum(b["poly"].area for b in self.blocks)
        gap = S.area - tot - self.mortar - self.dropped
        self.check(f"blocks + open joints account for the U02 stone (residual {gap:.3g}, slivers {self.dropped:.3g})",
                   abs(gap) <= 1e-6 * S.area and self.dropped <= 1e-6 * S.area)
        # joint QA
        rad = [j for j in self.joints if j["centre"] is not None]
        def off(j):  # perpendicular distance from the centre to the joint's infinite line
            (x0, y0), (x1, y1) = list(j["seg"].coords)[0], list(j["seg"].coords)[-1]
            cx, cy = j["centre"]
            return abs((x1 - x0) * (cy - y0) - (y1 - y0) * (cx - x0)) / math.hypot(x1 - x0, y1 - y0)
        err = max((off(j) for j in rad), default=0.0)
        self.check(f"{len(rad)} radial joints pass through their arc centres (max offset {err:.2g})", err <= 1e-6 * m.size)
        hits = sum(1 for j in self.joints for z in self.zones if j["kind"] not in ("bed", "sill")
                   and j["seg"].intersection(S).intersects(z))
        self.check(f"no voussoir/ring joint inside a junction keep-out zone ({hits})", hits == 0, "architectural")
        sizes = []
        for b in self.blocks:
            r = b["poly"].minimum_rotated_rectangle
            c = np.asarray(r.exterior.coords)
            d = sorted({round(float(np.linalg.norm(c[i + 1] - c[i])), 6) for i in range(4)})
            b["long"], b["short"] = max(d), min(d)
            sizes.append(b["long"])
        self.check(f"largest block {max(sizes):.4g} <= max stone length {self.max_block:.4g}", max(sizes) <= self.max_block,
                   "architectural")

    # ---------------- meshes
    def _mesh(self):
        m, u = self.m, self.u
        voids_u = unary_union([v["poly"] for v in m.voids])
        orders = {k: u.order_of(k) for k in range(len(u.orders) + 4)}
        regs = {k: unary_union(ps) for k, ps in u.regions.items()}
        isos = {}
        for k, R in regs.items():
            o = orders[k]
            isos[k] = [(d, voids_u.buffer(d, join_style="mitre", mitre_limit=2.0).boundary.intersection(R))
                       for d in o["prof"][1:, 0]]
        tm = [(U.member_order(x), x["poly"]) for x in m.members if x["kind"] != "frame"]
        cons = unary_union([p.boundary for k, p in tm]) if tm else None

        def lab_tracery(xs, ys):
            lab = np.full(len(xs), 10 ** 6)
            for k, p in tm:
                inside = shapely.contains_xy(p, xs, ys)
                lab[inside] = np.minimum(lab[inside], k)
            miss = lab == 10 ** 6
            if miss.any():
                pts = shapely.points(np.c_[xs[miss], ys[miss]])
                dist = np.array([shapely.distance(pts, p) for k, p in tm])
                lab[miss] = np.array([k for k, p in tm])[np.argmin(dist, axis=0)]
            return lab

        zero = lambda xs, ys: np.zeros(len(xs), int)
        self.parts, self.meta = [], {}
        rng_base = np.array([0.80, 0.76, 0.68])
        viol = 0
        for i, b in enumerate(self.blocks):
            tr = b["region"] == "tracery"
            iso_b = {k: v for k, v in isos.items() if (k >= 1) == tr or m.mode == "plate"}
            V, F, info = block_mesh(b["poly"], cons if tr else None, iso_b, lab_tracery if tr else zero, orders,
                                    voids_u, u.zg, m.size, m.tol)
            viol += info["violations"]
            mesh = trimesh.Trimesh(V, F, process=False)
            tint = np.random.default_rng(i + 7).uniform(-0.035, 0.035)
            rgba = tuple(np.clip(rng_base * (1 + tint), 0, 1)) + (1.0,)
            self.parts.append((b["name"], mesh, rgba, 0.85))
            self.meta[b["name"]] = dict(region=b["region"], holes=len(b["poly"].interiors), area=b["poly"].area,
                                        long=b["long"], short=b["short"], label_areas=info["label_areas"],
                                        steiner=info["steiner"], violations=info["violations"],
                                        fallback=info["fallback"])
        fb = sum(1 for x in self.meta.values() if x["fallback"])
        self.check(f"every stone triangulated with full order/moulding linework ({fb} fallbacks)", fb == 0)
        self.check(f"risers consistent: order surfaces never cross along a step ({viol} violations)", viol == 0)
        for nm, mesh, rgba, rough in u.parts:
            if nm in ("wall", "glass"):
                self.parts.append((nm, mesh, rgba, rough))

    def export_glb(self, path):
        sc = trimesh.Scene()
        for nm, mesh, rgba, rough in self.parts:
            mm = trimesh.Trimesh(mesh.vertices.copy(), mesh.faces.copy(), process=False)
            mm.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
                name=f"{nm}_mat", baseColorFactor=list(rgba), metallicFactor=0.0, roughnessFactor=rough))
            sc.add_geometry(mm, node_name=f"{self.m.id}__{nm}", geom_name=f"{self.m.id}__{nm}")
        data = sc.export(file_type="glb", include_normals=False)
        open(path, "wb").write(data)
        return data
