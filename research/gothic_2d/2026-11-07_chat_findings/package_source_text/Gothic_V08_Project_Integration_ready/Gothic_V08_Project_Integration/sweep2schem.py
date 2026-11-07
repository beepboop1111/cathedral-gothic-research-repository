#!/usr/bin/env python3
"""
sweep2schem.py - profile image straight to Minecraft schematic, one command.

Takes a moulding-section PNG, sweeps it (revolve into an arch, or extrude into a
straight run), voxelises the result directly, and writes a Sponge .schem.

No mesh, no STL round trip, no FreeCAD, no external libraries beyond numpy+Pillow.
Only the solid blocks are held in memory and the big files are written in
pieces, so a cathedral-size rib needs about as much memory as a small one.

Plain round arch (quarter circle by default):

    python3 sweep2schem.py section.png --radius 72

Arch or straight run placed between two named piers (yaw worked out for you):

    python3 sweep2schem.py section.png --start-pier R0_80 --end-pier R1_100 \
        --radius 72
    python3 sweep2schem.py section.png --mode extrude \
        --start-pier R0_80 --end-pier R1_100 --fit-span

Pointed (two-centred Gothic) rib between two named piers:

    python3 sweep2schem.py section.png --start-pier R0_80 --end-pier R1_100 \
        --gothic --rise 1296

Check the numbers without building anything:

    python3 sweep2schem.py --start-pier R0_80 --end-pier R1_100 \
        --gothic --rise 1296 --geometry-only

Run with --help for the full option list.
"""

import argparse
import copy
from concurrent.futures import ProcessPoolExecutor
import gzip
import json
import math
import os
import struct
import zlib
import sys

import numpy as np
from PIL import Image

# ----------------------------------------------------------------------------
# Minecraft data versions (for the DataVersion tag in the .schem)
# ----------------------------------------------------------------------------
DATA_VERSIONS = {
    "1.20.1": 3465,
    "1.21": 3953,
    "1.21.1": 3955,
    "1.21.4": 4189,
    "1.21.5": 4325,
    "1.21.6": 4435,
    "1.21.7": 4438,
    "1.21.8": 4440,
    "1.21.9": 4554,
    "1.21.10": 4556,
    "1.21.11": 4671,
}
DEFAULT_MC = "1.21.11"


# ----------------------------------------------------------------------------
# Minimal NBT writer (only the tags a Sponge v2 schematic needs)
# ----------------------------------------------------------------------------
def _str(s):
    b = s.encode("utf-8")
    return struct.pack(">H", len(b)) + b


def _named(tag_id, name, payload):
    return struct.pack(">B", tag_id) + _str(name) + payload


def t_byte(name, v):
    return _named(1, name, struct.pack(">b", v))


def t_short(name, v):
    return _named(2, name, struct.pack(">h", v))


def t_int(name, v):
    return _named(3, name, struct.pack(">i", v))


def t_string(name, v):
    return _named(8, name, _str(v))


def t_bytearray(name, data):
    return _named(7, name, struct.pack(">i", len(data)) + bytes(data))


def t_intarray(name, values):
    return _named(11, name, struct.pack(">i", len(values))
                  + b"".join(struct.pack(">i", v) for v in values))


def t_list_intarray(name, arrays):
    payload = struct.pack(">Bi", 11, len(arrays))
    parts = [payload]
    for a in arrays:
        parts.append(struct.pack(">i", len(a)))
        parts.append(np.asarray(a, dtype=">i4").tobytes())
    return _named(9, name, b"".join(parts))


def t_compound(name, body):
    return _named(10, name, body + b"\x00")


def varint(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


# ----------------------------------------------------------------------------
# Sparse voxels: only the solid blocks are kept in memory
# ----------------------------------------------------------------------------
class Voxels:
    """The solid blocks of a sweep. Each block is one int64 key (its
    [x, y, z] index in C order, kept sorted) plus its palette id
    (1 = blocks[0]). Memory grows with the number of solid blocks, not with
    the bounding box, so a thin rib running diagonally through a huge box
    costs next to nothing. Air is never stored."""

    def __init__(self, shape, keys, ids):
        self.shape = tuple(int(v) for v in shape)
        self.keys = keys
        self.ids = ids

    @classmethod
    def from_xyz(cls, shape, x, y, z, ids):
        nx, ny, nz = (int(v) for v in shape)
        keys = ((np.asarray(x, np.int64) * ny + np.asarray(y, np.int64)) * nz
                + np.asarray(z, np.int64))
        ids = np.broadcast_to(np.asarray(ids, np.uint8), keys.shape)
        order = np.argsort(keys, kind="stable")
        return cls(shape, keys[order], np.ascontiguousarray(ids[order]))

    @classmethod
    def from_dense(cls, grid):
        x, y, z = np.nonzero(grid)
        return cls.from_xyz(grid.shape, x, y, z, grid[x, y, z])

    @property
    def count(self):
        return int(self.keys.size)

    def xyz(self):
        nx, ny, nz = self.shape
        x, r = np.divmod(self.keys, ny * nz)
        y, z = np.divmod(r, nz)
        return x, y, z

    def dense(self):
        """The full [x, y, z] uint8 grid (only for small pieces/tests)."""
        grid = np.zeros(self.shape, np.uint8)
        grid.reshape(-1)[self.keys] = self.ids
        return grid

    def used_ids(self):
        return set(np.unique(self.ids).tolist())

    def select(self, keep):
        return Voxels(self.shape, self.keys[keep], self.ids[keep])

    def padded_keys(self):
        """Keys in a box one block bigger on every side (so a neighbour key
        never wraps round to the far side), plus the key steps to the
        neighbours along x, y and z. Same order as self.keys."""
        nx, ny, nz = self.shape
        x, y, z = self.xyz()
        keys = ((x + 1) * (ny + 2) + (y + 1)) * (nz + 2) + (z + 1)
        return keys, ((ny + 2) * (nz + 2), nz + 2, 1)

    def hollow(self, thickness):
        """Keep only a shell `thickness` blocks deep. Members thinner than
        2*thickness stay solid on their own. (Six-neighbour erosion, with
        everything outside the box counted as air.)"""
        keys, steps = self.padded_keys()
        inner = keys
        for _ in range(int(thickness)):
            if inner.size == 0:
                break
            keep = np.ones(inner.size, bool)
            for s in steps:
                keep &= _member(inner + s, inner)
                keep &= _member(inner - s, inner)
            inner = inner[keep]
        return self.select(~_member(keys, inner))

    def crop(self, lo):
        """Shrink the box to the solid blocks -> (voxels, new origin)."""
        if self.count == 0:
            return self, lo
        x, y, z = self.xyz()
        mins = [int(a.min()) for a in (x, y, z)]
        maxs = [int(a.max()) for a in (x, y, z)]
        shape = [maxs[i] - mins[i] + 1 for i in range(3)]
        new_lo = np.array([lo[i] + mins[i] for i in range(3)], dtype=float)
        return (Voxels.from_xyz(shape, x - mins[0], y - mins[1], z - mins[2],
                                self.ids), new_lo)


def _member(query, sorted_keys):
    """Which of the query keys are present in sorted_keys."""
    n = sorted_keys.size
    if n == 0:
        return np.zeros(np.shape(query), bool)
    i = np.minimum(np.searchsorted(sorted_keys, query), n - 1)
    return sorted_keys[i] == query


def _as_voxels(grid):
    """Writers accept Voxels or (for small jobs) a dense [x, y, z] grid."""
    return grid if isinstance(grid, Voxels) else Voxels.from_dense(np.asarray(grid))


def _varint_bytes(buf):
    """uint8 palette indices -> Sponge VarInt bytes (two bytes from 128 up)."""
    hi = buf >= 128
    if not hi.any():
        return buf.tobytes()
    out = np.empty(buf.size + int(hi.sum()), np.uint8)
    pos = np.arange(buf.size) + np.concatenate(([0], np.cumsum(hi)[:-1]))
    out[pos] = np.where(hi, (buf & 0x7F) | 0x80, buf)
    out[pos[hi] + 1] = buf[hi] >> 7
    return out.tobytes()


SCHEM_MAX_BYTES = 2 ** 31 - 1      # an NBT byte array's length is an int32


def write_schem(path, grid, blocks, data_version, offset=(0, 0, 0)):
    """grid: Voxels (or a dense uint8 [x, y, z] grid), 0 = air,
    n = blocks[n-1]. Writes a gzipped Sponge v2 .schem.

    A .schem has to spell out every block in the box, air included, so the
    block data is generated and compressed a slab of layers at a time
    instead of being built in memory all at once."""
    vox = _as_voxels(grid)
    nx, ny, nz = vox.shape
    palette = {"minecraft:air": 0}
    for i, b in enumerate(blocks):
        palette[b] = i + 1

    # Sponge v2 stores palette indices as VarInts: one byte below 128, two
    # from 128 up (indices never pass 255 here)
    if max(nx, ny, nz) > 32767:
        raise ValueError(
            f"the box is {nx} x {ny} x {nz}; a .schem side can be at most 32,767 "
            f"blocks. Use --bp or --lt/--lt-struct (with --no-schem), or split the run")
    n_bytes = nx * ny * nz + int((vox.ids >= 128).sum())
    if n_bytes > SCHEM_MAX_BYTES:
        raise ValueError(
            f"the box is {nx} x {ny} x {nz} = {nx * ny * nz:,} blocks, but a .schem "
            f"can hold at most {SCHEM_MAX_BYTES:,}. Use --bp or --lt/--lt-struct "
            f"(with --no-schem), or raise --ppb")

    pal_body = b"".join(t_int(k, v) for k, v in palette.items())
    meta = b"".join([
        t_int("WEOffsetX", int(offset[0])),
        t_int("WEOffsetY", int(offset[1])),
        t_int("WEOffsetZ", int(offset[2])),
    ])
    head = b"".join([
        t_int("Version", 2),
        t_int("DataVersion", int(data_version)),
        t_compound("Metadata", meta),
        t_short("Width", nx),
        t_short("Height", ny),
        t_short("Length", nz),
        t_intarray("Offset", [int(offset[0]), int(offset[1]), int(offset[2])]),
        t_int("PaletteMax", len(palette)),
        t_compound("Palette", pal_body),
    ])
    # the root compound, everything before the block bytes, then the
    # BlockData tag header with its length
    prefix = (struct.pack(">B", 10) + _str("Schematic") + head
              + struct.pack(">B", 7) + _str("BlockData")
              + struct.pack(">i", n_bytes))

    # Sponge block order is YZX: re-key the solid blocks that way
    x, y, z = vox.xyz()
    yzx = (y * nz + z) * nx + x
    del x, y, z
    order = np.argsort(yzx, kind="stable")
    yzx = yzx[order]
    ids = vox.ids[order]
    del order

    layer = nx * nz
    per = max(1, (16 << 20) // max(layer, 1))        # about 16 MB per write
    with gzip.open(path, "wb") as f:
        f.write(prefix)
        for y0 in range(0, ny, per):
            y1 = min(ny, y0 + per)
            a, b = np.searchsorted(yzx, [y0 * layer, y1 * layer])
            buf = np.zeros((y1 - y0) * layer, np.uint8)
            buf[yzx[a:b] - y0 * layer] = ids[a:b]
            f.write(_varint_bytes(buf))
        f.write(b"\x00")                             # end of the root compound


# ----------------------------------------------------------------------------
# Binary STL writer (exposed block faces only - an exact preview of the schem)
# ----------------------------------------------------------------------------
def write_stl(path, grid, scale=1.0):
    vox = _as_voxels(grid)
    keys, steps = vox.padded_keys()
    x, y, z = vox.xyz()
    base_all = np.stack([x, y, z], axis=1).astype(np.float32)
    del x, y, z
    tris = []

    # (axis, direction) -> the four corners of that face on a unit cube
    faces = {
        (0, +1): [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)],
        (0, -1): [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)],
        (1, +1): [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)],
        (1, -1): [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],
        (2, +1): [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],
        (2, -1): [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)],
    }

    for (axis, direction), corners in faces.items():
        # a face is exposed when the neighbour on that side is air
        exposed = ~_member(keys + direction * steps[axis], keys)
        if not exposed.any():
            continue
        base = base_all[exposed]
        c = [base + np.array(k, dtype=np.float32) for k in corners]
        tris.append(np.stack([c[0], c[1], c[2]], axis=1))
        tris.append(np.stack([c[0], c[2], c[3]], axis=1))

    if not tris:
        return 0
    tris = np.concatenate(tris, axis=0) * float(scale)

    # 50-byte records: normal (left zero), three vertices, attribute count
    n = len(tris)
    rec = np.zeros(n, dtype=[("v", "<f4", (12,)), ("attr", "<u2")])
    rec["v"][:, 3:] = tris.reshape(n, 9)
    with open(path, "wb") as f:
        f.write(b"sweep2schem" + b"\x00" * 69)
        f.write(struct.pack("<I", n))
        f.write(rec.tobytes())
    return n


# ----------------------------------------------------------------------------
# Axiom .bp output - same layout as schem_to_bp.py (magic, sized header NBT,
# PNG thumbnail, gzipped BlockRegion list of 16^3 regions)
# ----------------------------------------------------------------------------
BP_MAGIC = 0x0AE5BB36
VOID = "minecraft:structure_void"


def _bp_str(s):
    b = s.encode("utf-8")
    return struct.pack(">H", len(b)) + b


def _bp_palette_tag(block):
    """One TAG_Compound payload per palette entry, properties included."""
    if "[" in block and block.endswith("]"):
        nm, rest = block.split("[", 1)
        out = struct.pack(">B", 8) + _bp_str("Name") + _bp_str(nm)
        props = b""
        for prop in rest[:-1].split(","):
            if prop:
                k, v = prop.split("=", 1)
                props += struct.pack(">B", 8) + _bp_str(k) + _bp_str(v)
        return out + struct.pack(">B", 10) + _bp_str("Properties") + props + b"\x00" + b"\x00"
    return struct.pack(">B", 8) + _bp_str("Name") + _bp_str(block) + b"\x00"


def _bp_states(ids, names):
    """BlockStates payload for one region.
    ids: 4096 uint8 palette indices in y,z,x order (0 = first seen)."""
    uniq, inv = np.unique(ids, return_inverse=True)
    order = np.argsort([np.argmax(ids == u) for u in uniq])   # first-seen order
    remap = np.empty(uniq.size, np.int64)
    remap[order] = np.arange(uniq.size)
    vals = remap[inv]
    palette = [names[uniq[i]] for i in order]

    bits = max(4, (len(palette) - 1).bit_length())
    vpl = 64 // bits
    n_longs = -(-4096 // vpl)
    data = np.zeros(n_longs, dtype=np.uint64)
    v = np.zeros(n_longs * vpl, dtype=np.uint64)
    v[:4096] = vals.astype(np.uint64)
    v = v.reshape(n_longs, vpl)
    for j in range(vpl):
        data |= v[:, j] << np.uint64(j * bits)

    pal = b"".join(_bp_palette_tag(p) for p in palette)
    return (struct.pack(">B", 9) + _bp_str("palette")
            + struct.pack(">Bi", 10, len(palette)) + pal
            + struct.pack(">B", 12) + _bp_str("data")
            + struct.pack(">i", n_longs) + data.astype(">u8").tobytes()
            + b"\x00")


def _bp_region(ids, rx, ry, rz, names, states=None):
    """One BlockRegion entry; pass `states` to reuse an already built
    BlockStates payload (empty regions are all alike)."""
    if states is None:
        states = _bp_states(ids, names)
    return (struct.pack(">B", 3) + _bp_str("X") + struct.pack(">i", rx)
            + struct.pack(">B", 3) + _bp_str("Y") + struct.pack(">i", ry)
            + struct.pack(">B", 3) + _bp_str("Z") + struct.pack(">i", rz)
            + struct.pack(">B", 10) + _bp_str("BlockStates") + states
            + b"\x00")


def _bp_thumbnail(size=16, rgb=(94, 129, 172)):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))
    row = bytes(bytearray([0] + list(rgb) * size))
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(row * size, 9)) + chunk(b"IEND", b""))


def write_bp(path, grid, blocks, name, author="schem_to_bp.py",
             thumbnail=None):
    """grid: Voxels (or a dense uint8 [x, y, z] grid). The 16^3 regions are
    built one at a time and fed straight into the compressor, and empty
    regions reuse one prebuilt payload, so a huge, mostly empty box costs
    little memory."""
    vox = _as_voxels(grid)
    nx, ny, nz = vox.shape
    # ids 0..n-1 are the materials, then air inside the bounds, then void in
    # the padding out to the 16-block region grid
    names = list(blocks) + ["minecraft:air", VOID]
    air_id, void_id = len(blocks), len(blocks) + 1
    nrx, nry, nrz = -(-nx // 16), -(-ny // 16), -(-nz // 16)

    # sort the solid blocks by region, in the order the regions are written
    x, y, z = vox.xyz()
    rkey = ((x >> 4) * nry + (y >> 4)) * nrz + (z >> 4)
    order = np.argsort(rkey, kind="stable")
    rkey = rkey[order]
    lx, ly, lz = x[order] & 15, y[order] & 15, z[order] & 15
    mat = vox.ids[order].astype(np.uint8) - 1
    del x, y, z, order
    occupied, starts = np.unique(rkey, return_index=True)
    ends = np.append(starts[1:], rkey.size)
    del rkey

    def blank(gx, gy, gz):
        cell = np.full((16, 16, 16), void_id, np.uint8)
        cell[:gx, :gy, :gz] = air_id
        return cell

    # same bytes as gzip.compress(..., mtime=0), produced piece by piece
    comp = zlib.compressobj(9, zlib.DEFLATED, 31)
    out = []

    def feed(b):
        c = comp.compress(b)
        if c:
            out.append(c)

    feed(struct.pack(">B", 10) + _bp_str("")
         + struct.pack(">B", 9) + _bp_str("BlockRegion")
         + struct.pack(">Bi", 10, nrx * nry * nrz))
    empty = {}
    j = 0
    for rx in range(nrx):
        gx = min(16, nx - rx * 16)
        for ry in range(nry):
            gy = min(16, ny - ry * 16)
            for rz in range(nrz):
                gz = min(16, nz - rz * 16)
                k = (rx * nry + ry) * nrz + rz
                if j < occupied.size and occupied[j] == k:
                    cell = blank(gx, gy, gz)
                    s = slice(starts[j], ends[j])
                    cell[lx[s], ly[s], lz[s]] = mat[s]
                    j += 1
                    # region cells are ordered y, then z, then x
                    states = _bp_states(np.transpose(cell, (1, 2, 0)).ravel(), names)
                else:
                    states = empty.get((gx, gy, gz))
                    if states is None:
                        states = _bp_states(
                            np.transpose(blank(gx, gy, gz), (1, 2, 0)).ravel(), names)
                        empty[(gx, gy, gz)] = states
                feed(_bp_region(None, rx, ry, rz, names, states))
    feed(struct.pack(">B", 9) + _bp_str("BlockEntities")
         + struct.pack(">Bi", 10, 0)
         + b"\x00")
    data = b"".join(out) + comp.flush()
    out.clear()
    # gzip header: zero mtime, OS byte 255 (what gzip.compress writes)
    block_data = data[:4] + struct.pack("<LBB", 0, data[8], 255) + data[10:]
    del data

    header = (struct.pack(">B", 5) + _bp_str("ThumbnailYaw") + struct.pack(">f", 0.0)
              + struct.pack(">B", 5) + _bp_str("ThumbnailPitch") + struct.pack(">f", 45.0)
              + struct.pack(">B", 1) + _bp_str("ContainsAir") + struct.pack(">b", 0)
              + struct.pack(">B", 1) + _bp_str("LockedThumbnail") + struct.pack(">b", 0)
              + struct.pack(">B", 4) + _bp_str("Version") + struct.pack(">Q", 1)
              + struct.pack(">B", 8) + _bp_str("Author") + _bp_str(author)
              + struct.pack(">B", 8) + _bp_str("Name") + _bp_str(name)
              + struct.pack(">B", 9) + _bp_str("Tags") + struct.pack(">Bi", 0, 0)
              + struct.pack(">B", 3) + _bp_str("BlockCount")
              + struct.pack(">i", vox.count)
              + b"\x00")
    header = struct.pack(">B", 10) + _bp_str("") + header

    thumb = open(thumbnail, "rb").read() if thumbnail else _bp_thumbnail()
    with open(path, "wb") as f:
        f.write(struct.pack(">ii", BP_MAGIC, len(header)) + header)
        f.write(struct.pack(">i", len(thumb)) + thumb)
        f.write(struct.pack(">i", len(block_data)) + block_data)


# ----------------------------------------------------------------------------
# LittleTiles output: greedy box merge, then the pre223 export schema
# (x-runs -> z-plates -> y-boxes, matching littletiles_generator.merge_cells)
# ----------------------------------------------------------------------------
def _merge_runs(keys, v):
    n = v.size
    if n == 0:
        return np.zeros(0, np.int64), np.zeros(0, np.int64), np.zeros(0, np.int64)
    same = np.ones(n, bool)
    same[0] = False
    if keys.shape[1]:
        same[1:] = np.all(keys[1:] == keys[:-1], axis=1) & (v[1:] == v[:-1] + 1)
    else:
        same[1:] = v[1:] == v[:-1] + 1
    starts = np.nonzero(~same)[0]
    lasts = np.append(starts[1:] - 1, n - 1)
    return starts, v[starts], v[lasts] + 1


def merge_boxes(grid):
    """grid: bool [x, y, z] array, or Voxels (every solid block counts) ->
    (N, 6) array of (x0,y0,z0,x1,y1,z1), max exclusive."""
    if isinstance(grid, Voxels):
        x, y, z = grid.xyz()
    else:
        x, y, z = np.nonzero(grid)
    if x.size == 0:
        return np.zeros((0, 6), np.int64)

    # x-runs: consecutive x inside each (y, z) row
    order = np.lexsort((x, z, y))
    x, y, z = x[order], y[order], z[order]
    new = np.ones(x.size, bool)
    new[1:] = (y[1:] != y[:-1]) | (z[1:] != z[:-1]) | (x[1:] != x[:-1] + 1)
    first = np.nonzero(new)[0]
    last = np.append(first[1:] - 1, x.size - 1)
    sy, sz, x0, x1 = y[first], z[first], x[first], x[last] + 1

    order = np.lexsort((sz, x1, x0, sy))
    y_, z_, a_, b_ = sy[order], sz[order], x0[order], x1[order]
    starts, z0, z1 = _merge_runs(np.stack([y_, a_, b_], axis=1), z_)
    py, pa, pb = y_[starts], a_[starts], b_[starts]

    order = np.lexsort((py, z1, z0, pb, pa))
    a_, b_, c_, e_, y_ = pa[order], pb[order], z0[order], z1[order], py[order]
    starts, y0, y1 = _merge_runs(np.stack([a_, b_, c_, e_], axis=1), y_)

    boxes = np.stack([a_[starts], y0, c_[starts],
                      b_[starts], y1, e_[starts]], axis=1)
    return boxes[np.lexsort((boxes[:, 0], boxes[:, 2], boxes[:, 1]))]


def lt_grid_density(boxes, grid):
    """How many tiles touch each Minecraft block, against LittleTiles'
    maxAllowedDensity. One source block = one grid unit, so a block holds
    `grid` units per axis."""
    counts = {}
    for b in boxes:
        x0, y0, z0, x1, y1, z1 = (int(v) for v in b)
        for bx in range(x0 // grid, (x1 - 1) // grid + 1):
            for by in range(y0 // grid, (y1 - 1) // grid + 1):
                for bz in range(z0 // grid, (z1 - 1) // grid + 1):
                    k = (bx, by, bz)
                    counts[k] = counts.get(k, 0) + 1
    if not counts:
        return 0, 0, 0
    vals = list(counts.values())
    return len(counts), max(vals), sum(vals) / len(vals)


def _lt_extent(per_state):
    mx = my = mz = 0
    for boxes in per_state.values():
        mx = max(mx, int(boxes[:, 3].max()))
        my = max(my, int(boxes[:, 4].max()))
        mz = max(mz, int(boxes[:, 5].max()))
    return mx, my, mz


def lt_snbt(per_state, grid=16):
    """The import string LittleTiles' blueprint text box accepts.
    per_state: {block id -> (N,6) box array}, already normalised to (0,0,0)."""
    mx, my, mz = _lt_extent(per_state)
    total = sum(len(b) for b in per_state.values())
    chunks = []
    for state in sorted(per_state):
        box_txt = ",".join("[I;%d,%d,%d,%d,%d,%d]" % tuple(int(v) for v in b)
                           for b in per_state[state])
        chunks.append('"%s":[[I;-1],%s]' % (state, box_txt))
    # the grid key is omitted at the default of 16, matching LittleTiles' own
    # export
    g = "" if grid == 16 else "grid:%d," % grid
    return ("{boxes:%d,%smin:[I;0,0,0],size:[I;%d,%d,%d],t:{%s},tiles:%d}"
            % (total, g, mx, my, mz, ",".join(chunks), len(per_state)))


def write_ltstruct(path, per_state, grid=16):
    """Gzipped NBT holding the same structure node the blueprint item carries,
    ready for littletiles_batch.py inject to pick out of its cache folder."""
    mx, my, mz = _lt_extent(per_state)
    total = sum(len(b) for b in per_state.values())
    tbody = b"".join(
        t_list_intarray(st, [[-1]] + [b for b in per_state[st]])
        for st in sorted(per_state))
    parts = [
        t_int("boxes", total),
        t_int("tiles", len(per_state)),
        t_intarray("min", [0, 0, 0]),
        t_intarray("size", [mx, my, mz]),
        t_compound("t", tbody),
    ]
    if grid != 16:
        parts.insert(1, t_int("grid", grid))
    body = b"".join(parts)
    with open(path, "wb") as f:
        f.write(gzip.compress(t_compound("", body)))


# ----------------------------------------------------------------------------
# Image -> mask
# ----------------------------------------------------------------------------
def load_mask(path, threshold, invert, transpose, flip_x, flip_y):
    img = Image.open(path).convert("L")
    a = np.asarray(img, dtype=np.float32) / 255.0
    mask = a < threshold          # dark pixels are stone by default
    if invert:
        mask = ~mask
    if transpose:
        mask = mask.T
    if flip_x:
        mask = mask[:, ::-1]
    if flip_y:
        mask = mask[::-1, :]
    return np.ascontiguousarray(mask)


def load_paint(path, args, nsteps):
    """Returns (solid mask, tone index array). Air is transparent if the image
    has an alpha channel, otherwise anything lighter than --air-level.
    The remaining grey levels index the ramp: black -> darkest, white ->
    lightest."""
    img = Image.open(path)
    has_alpha = img.mode in ("RGBA", "LA") or "transparency" in img.info
    lum = np.asarray(img.convert("L"), dtype=np.float32) / 255.0
    if has_alpha:
        alpha = np.asarray(img.convert("RGBA"), dtype=np.float32)[..., 3] / 255.0
        # Many editors save an RGB image as RGBA while leaving alpha fully
        # opaque. In that case alpha carries no mask information, so fall back
        # to --air-level instead of turning the white background into stone.
        if np.any(alpha < 0.999):
            solid = alpha >= 0.5
        else:
            solid = lum < args.air_level
    else:
        solid = lum < args.air_level
    if args.invert:
        solid = ~solid
        lum = 1.0 - lum
    tone = np.clip(np.rint(lum * (nsteps - 1)), 0, nsteps - 1).astype(np.uint8)
    if args.transpose:
        solid, tone = solid.T, tone.T
    if args.flip_x:
        solid, tone = solid[:, ::-1], tone[:, ::-1]
    if args.flip_y:
        solid, tone = solid[::-1, :], tone[::-1, :]
    return np.ascontiguousarray(solid), np.ascontiguousarray(tone)


def trim(mask, extra=None):
    """Crop blank border so --radius means 'axis to the first solid pixel'."""
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    if not rows.any():
        return mask, extra
    r0, r1 = np.nonzero(rows)[0][[0, -1]]
    c0, c1 = np.nonzero(cols)[0][[0, -1]]
    s = (slice(r0, r1 + 1), slice(c0, c1 + 1))
    return mask[s], (None if extra is None else extra[s])


# ----------------------------------------------------------------------------
# Voxelisation
# ----------------------------------------------------------------------------
def bounds_revolve(r_in, r_out, angle_deg):
    a = np.linspace(0.0, math.radians(angle_deg), 2048)
    xs = np.concatenate([r_in * np.cos(a), r_out * np.cos(a)])
    ys = np.concatenate([r_in * np.sin(a), r_out * np.sin(a)])
    return xs.min(), xs.max(), ys.min(), ys.max()


def voxelise(mask, args, paint=None):
    h_px, w_px = mask.shape
    ppb = float(args.ppb)
    w_bl = w_px / ppb          # profile width in blocks
    h_bl = h_px / ppb          # profile height in blocks

    gothic = bool(getattr(args, "gothic", False)) and args.mode == "revolve"
    part = getattr(args, "gothic_part", "full")
    crown_x = None

    if args.mode == "revolve":
        r_in = float(args.radius)
        r_out = r_in + w_bl
        if gothic:
            # Two-centred pointed arch. The first half is the circle of radius
            # r_in round the local origin, springing at x = +r_in; the second
            # half is its mirror image in the vertical crown plane x = crown_x,
            # so the two inner edges spring exactly one span apart. Each half
            # runs right up to the crown plane, so the halves meet flush and
            # the top of the rib comes to a closed point instead of a V notch.
            crown_x = r_in - float(args.gothic_span) / 2.0
            if crown_x > 0:
                apex = math.sqrt(max(r_out * r_out - crown_x * crown_x, 0.0))
            else:
                apex = r_out
            if part == "left":
                x0, x1 = crown_x, r_out
            elif part == "right":
                x0, x1 = 2.0 * crown_x - r_out, crown_x
            else:
                x0, x1 = 2.0 * crown_x - r_out, r_out
            y0, y1 = 0.0, apex
        else:
            x0, x1, y0, y1 = bounds_revolve(r_in, r_out, args.angle)
        lo = np.array([math.floor(x0), math.floor(y0), 0.0])
        hi = np.array([math.ceil(x1), math.ceil(y1), math.ceil(h_bl)])
    else:
        lo = np.array([0.0, 0.0, 0.0])
        hi = np.array([math.ceil(w_bl), math.ceil(h_bl), math.ceil(args.length)])

    yaw = math.radians(args.yaw)
    cy_, sy_ = math.cos(yaw), math.sin(yaw)
    if args.yaw:
        # rotate the local bounding box into world space and re-box it
        cx, cz = [], []
        for lx in (lo[0], hi[0]):
            for lz in (lo[2], hi[2]):
                cx.append(lx * cy_ + lz * sy_)
                cz.append(-lx * sy_ + lz * cy_)
        lo = np.array([math.floor(min(cx)), lo[1], math.floor(min(cz))])
        hi = np.array([math.ceil(max(cx)), hi[1], math.ceil(max(cz))])

    dims = (hi - lo).astype(int)
    nx, ny, nz = [max(1, int(d)) for d in dims]

    total = nx * ny * nz
    if total > args.max_voxels:
        size = "span/rise" if gothic else "--radius/--length"
        raise SystemExit(
            f"    ABORT: the bounding box is {total:,} voxels, over --max-voxels "
            f"{args.max_voxels:,}.\n"
            f"    Raise --ppb (fewer blocks per profile), use a smaller {size}, "
            f"or raise --max-voxels (memory use follows the number of solid "
            f"blocks, not the box; above {SCHEM_MAX_BYTES:,} only --bp/--lt "
            f"can be written).")

    S = int(args.samples)
    sub = (np.arange(S) + 0.5) / S
    ang = math.radians(args.angle)

    # A voxel centre is at most sqrt(3)/2 blocks from any point in the voxel
    TOL = 0.87

    def to_local(wx, wy, wz):
        if args.yaw:
            wx, wz = (wx * cy_ - wz * sy_), (wx * sy_ + wz * cy_)
        return wx, wy, wz

    def gothic_fold(wx, tol):
        """Gothic: fold points from the mirrored half onto the first half
        through the crown plane. -> (folded x, on-the-wanted-side flag)."""
        if part == "left":
            return wx, wx >= crown_x - tol
        if part == "right":
            return 2.0 * crown_x - wx, wx <= crown_x + tol
        return (np.where(wx >= crown_x, wx, 2.0 * crown_x - wx),
                np.ones(np.shape(wx), dtype=bool))

    def lookup(wx, wy, wz):
        """-> (col index, row index, in-sweep flag) for sample points."""
        wx, wy, wz = to_local(wx, wy, wz)
        if gothic:
            qx, inside = gothic_fold(wx, 1e-9)
            inside = inside & (wy >= -1e-9)
            col = (np.hypot(qx, wy) - args.radius) * ppb
            row = h_px - wz * ppb
        elif args.mode == "revolve":
            r = np.hypot(wx, wy)
            a = np.arctan2(wy, wx) % (2 * math.pi)
            inside = a <= ang + 1e-9
            col = (r - args.radius) * ppb
            row = h_px - wz * ppb
        else:
            inside = (wz >= -1e-9) & (wz <= args.length + 1e-9)
            col = wx * ppb
            row = h_px - wy * ppb
        ci = np.floor(col).astype(np.int32)
        ri = np.floor(row).astype(np.int32)
        ok = inside & (ci >= 0) & (ci < w_px) & (ri >= 0) & (ri < h_px)
        np.clip(ci, 0, w_px - 1, out=ci)
        np.clip(ri, 0, h_px - 1, out=ri)
        return ci, ri, ok

    def candidates(wx, wy, wz):
        """Cheap conservative test on voxel centres: could this voxel touch
        the swept solid at all? Skips the empty air around the sweep."""
        wx, wy, wz = to_local(wx, wy, wz)
        if gothic:
            qx, near = gothic_fold(wx, TOL)
            r = np.hypot(qx, wy)
            near &= (r >= args.radius - TOL) & (r <= args.radius + w_bl + TOL)
            near &= wy >= -TOL
            near &= (wz >= -TOL) & (wz <= h_bl + TOL)
        elif args.mode == "revolve":
            r = np.hypot(wx, wy)
            near = (r >= args.radius - TOL) & (r <= args.radius + w_bl + TOL)
            slack = TOL / np.maximum(r, 1e-6)
            a = np.arctan2(wy, wx) % (2 * math.pi)
            if ang < 2 * math.pi - 1e-9:
                near &= (a <= ang + slack) | (a >= 2 * math.pi - slack)
            near &= (wz >= -TOL) & (wz <= h_bl + TOL)
        else:
            near = (wx >= -TOL) & (wx <= w_bl + TOL)
            near &= (wy >= -TOL) & (wy <= h_bl + TOL)
            near &= (wz >= -TOL) & (wz <= args.length + TOL)
        return near

    # sub-sample offsets, flattened to one axis of length S**3
    oy, ox, oz = [o.ravel() for o in np.meshgrid(sub, sub, sub, indexing="ij")]
    ns = S ** 3

    # Everything the sweep can touch lies in a thin vertical slab: the
    # profile's depth for a revolve or Gothic rib (local z), its width for an
    # extrude (local x). Under a yaw that slab cuts diagonally through the
    # bounding box, so instead of testing every voxel of the (mostly empty)
    # box, only the strip of it around the slab is scanned, one tile of
    # columns at a time. The strip is a generous superset of what
    # candidates() accepts, so the result is exactly the same.
    if args.mode == "revolve":
        ca, cb, s_lo, s_hi = sy_, cy_, -TOL, h_bl + TOL     # local z = x*sin + z*cos
    else:
        ca, cb, s_lo, s_hi = cy_, -sy_, -TOL, w_bl + TOL    # local x = x*cos - z*sin
    TILE = 16

    def strip(c0, n_other, lo_other, a, b, t0, t1):
        """Index range along the other axis that the slab can reach, for
        the tile of columns t0..t1-1 (world coordinate c0 + index + 0.5)."""
        w = c0 + np.array([t0, t1 - 1], dtype=float) + 0.5
        ends = np.concatenate([(s_lo - a * w) / b, (s_hi - a * w) / b]) - lo_other - 0.5
        return (max(0, int(math.floor(ends.min())) - 1),
                min(n_other, int(math.ceil(ends.max())) + 2))

    def tiles():
        if abs(cb) >= abs(ca):          # tiles across x, strip along z
            for xa in range(0, nx, TILE):
                xb = min(nx, xa + TILE)
                za, zb = strip(lo[0], nz, lo[2], ca, cb, xa, xb)
                if za < zb:
                    yield np.arange(xa, xb), np.arange(za, zb)
        else:                           # tiles across z, strip along x
            for za in range(0, nz, TILE):
                zb = min(nz, za + TILE)
                xa, xb = strip(lo[2], nx, lo[0], cb, ca, za, zb)
                if xa < xb:
                    yield np.arange(xa, xb), np.arange(za, zb)

    hx, hy, hz, hid = [], [], [], []
    tested = 0
    step = max(1, int(3_000_000 / ns))
    for xi, zi in tiles():
        chunk = max(1, min(ny, int(4_000_000 / max(xi.size * zi.size, 1))))
        cx0 = (lo[0] + xi + 0.5)[None, :, None]
        cz0 = (lo[2] + zi + 0.5)[None, None, :]
        for y0i in range(0, ny, chunk):
            yi = np.arange(y0i, min(ny, y0i + chunk))

            # pass 1: one point per voxel centre
            cy0 = (lo[1] + yi + 0.5)[:, None, None]
            near = candidates(*np.broadcast_arrays(cx0, cy0, cz0))
            if not near.any():
                continue
            sel = np.nonzero(near)
            tested += sel[0].size

            # pass 2: full supersample, but only on the surviving voxels
            for b0 in range(0, sel[0].size, step):
                b = slice(b0, b0 + step)
                vy, vx, vz = yi[sel[0][b]], xi[sel[1][b]], zi[sel[2][b]]
                py = (lo[1] + vy)[:, None] + oy[None, :]
                px = (lo[0] + vx)[:, None] + ox[None, :]
                pz = (lo[2] + vz)[:, None] + oz[None, :]
                ci, ri, ok = lookup(px, py, pz)
                sol = mask[ri, ci] & ok
                n_solid = sol.sum(axis=1)
                hit = n_solid > args.air_weight * (ns - n_solid)
                if not hit.any():
                    continue
                if paint is None:
                    ids = np.ones(int(hit.sum()), np.uint8)
                else:
                    # average the painted tone over the samples that landed
                    # in solid material, so band edges anti-alias instead of
                    # jitter
                    tone = np.where(sol[hit], paint[ri[hit], ci[hit]], 0).sum(axis=1)
                    tone = tone / np.maximum(n_solid[hit], 1)
                    ids = np.rint(tone).astype(np.uint8) + 1
                hx.append(vx[hit])
                hy.append(vy[hit])
                hz.append(vz[hit])
                hid.append(ids)

    if hx:
        vox = Voxels.from_xyz((nx, ny, nz), np.concatenate(hx), np.concatenate(hy),
                              np.concatenate(hz), np.concatenate(hid))
    else:
        vox = Voxels((nx, ny, nz), np.zeros(0, np.int64), np.zeros(0, np.uint8))

    note = (f"    grid {nx} x {ny} x {nz} = {total:,} voxels, "
            f"supersampled {tested:,} of them "
            f"({100 * tested / max(total, 1):.1f}%)")
    return vox, lo, note


def write_preview(path, grid, nmat=1):
    """Front elevation. With painted materials, shows the tone."""
    vox = _as_voxels(grid)
    nx, ny, nz = vox.shape
    x, y, _ = vox.xyz()
    front = np.zeros((nx, ny), bool)                 # look down Z
    front[x, y] = True
    if nmat > 1:
        # keys run x, then y, then z, so each (x, y) column is one run:
        # take the highest palette id in each
        col = x * ny + y
        first = np.flatnonzero(np.r_[True, col[1:] != col[:-1]])
        tone = np.zeros(nx * ny, np.float32)
        tone[col[first]] = np.maximum.reduceat(vox.ids, first)
        tone = tone.reshape(nx, ny)
        shade = 30 + 200 * (tone - 1) / max(nmat - 1, 1)
        img = np.where(front, shade, 245)
    else:
        img = np.where(front, 30, 245)
    img = img.T[::-1].astype(np.uint8)
    Image.fromarray(img, mode="L").resize(
        (img.shape[1] * 2, img.shape[0] * 2), Image.NEAREST).save(path)


# ----------------------------------------------------------------------------
def load_profile(path, args, blocks):
    if args.paint:
        mask, tone = load_paint(path, args, len(blocks))
    else:
        mask = load_mask(path, args.threshold, args.invert,
                         args.transpose, args.flip_x, args.flip_y)
        tone = None
    if not args.no_trim:
        mask, tone = trim(mask, tone)
    if not mask.any():
        return None, None
    return mask, tone


def process(mask, name, job, tone=None):
    log = [f"  [{name}]"]
    blocks = job.blocks
    try:
        vox, lo, note = voxelise(mask, job, tone)
    except SystemExit as e:
        return False, log + [str(e)]
    log.append(note)
    solid = vox.count
    if solid == 0:
        log.append("    skipped: swept to nothing (profile smaller than one block?)")
        return False, log

    if job.hollow:
        vox = vox.hollow(job.hollow)
        kept = vox.count
        log.append(f"    hollowed to a {job.hollow}-block shell: "
                   f"{solid:,} -> {kept:,} blocks "
                   f"({100 * (1 - kept / solid):.0f}% removed)")
        solid = kept
        if solid == 0:
            log.append("    skipped: hollowing removed everything")
            return False, log

    vox, lo = vox.crop(lo)
    log.append(f"    {solid:,} blocks, bounds {vox.shape}, "
               f"origin offset {tuple(int(v) for v in lo)}")

    os.makedirs(job.out, exist_ok=True)
    offset = (0, 0, 0) if job.no_offset else tuple(int(v) for v in lo)

    present = vox.used_ids()
    used = [i for i in range(1, len(blocks) + 1) if i in present]
    if len(blocks) > 1:
        log.append(f"    {len(used)} of {len(blocks)} ramp steps used")

    if not job.no_schem:
        schem = os.path.join(job.out, name + ".schem")
        try:
            write_schem(schem, vox, blocks, job.data_version, offset)
            log.append(f"    wrote {schem}")
        except ValueError as e:
            log.append(f"    skipped the .schem: {e}")

    if job.bp:
        bpdir = job.bp_out or job.out
        os.makedirs(bpdir, exist_ok=True)
        bpath = os.path.join(bpdir, name + ".bp")
        write_bp(bpath, vox, blocks, name, job.bp_author)
        log.append(f"    wrote {bpath}")

    if job.lt or job.lt_struct:
        ltdir = job.lt_out or job.out
        os.makedirs(ltdir, exist_ok=True)
        per_state = {}
        for i in used:
            per_state[blocks[i - 1]] = merge_boxes(vox.select(vox.ids == i))
        boxes = np.concatenate(list(per_state.values()))
        log.append(f"    merged {solid:,} blocks into {len(boxes):,} boxes "
                   f"({solid / max(len(boxes), 1):.1f}x)")
        g = job.lt_grid
        nblk, peak, avg = lt_grid_density(boxes, g)
        sx, sy, sz = [d / g for d in vox.shape]
        log.append(f"    at 1:{g} that is {sx:.1f} x {sy:.1f} x {sz:.1f} blocks, "
                   f"{nblk:,} occupied; density peak {peak}, avg {avg:.0f} "
                   f"tiles/block")
        if g != 16:
            cell = max(1, g // 8)
            log.append(f"    for lt_shade, --cell {cell} keeps the shading "
                       f"grain at {'1/8' if g >= 8 else '1/%d' % g} of a block "
                       f"here")
        if peak > job.density_limit:
            log.append(f"    WARNING: peak {peak} exceeds maxAllowedDensity "
                       f"{job.density_limit} - raise the limit, use a coarser "
                       f"--lt-grid, or shade with a bigger --cell")
        if job.lt:
            txt = os.path.join(ltdir, name + ".txt")
            with open(txt, "w") as f:
                f.write(lt_snbt(per_state, g))
            log.append(f"    wrote {txt}")
        if job.lt_struct:
            lts = os.path.join(ltdir, name + ".ltstruct")
            write_ltstruct(lts, per_state, g)
            log.append(f"    wrote {lts}")

    if not job.no_preview:
        write_preview(os.path.join(job.out, name + "_preview.png"),
                      vox, len(blocks))

    if job.stl:
        stl = os.path.join(job.out, name + ".stl")
        n = write_stl(stl, vox, job.stl_scale)
        log.append(f"    wrote {stl} ({n:,} triangles)")
    return True, log


def _run(task):
    try:
        return process(*task)
    except Exception as e:
        return False, [f"  [{task[1]}]", f"    FAILED: {e}"]


def num_list(text, what):
    try:
        return [float(p) for p in str(text).replace(" ", "").split(",") if p != ""]
    except ValueError:
        sys.exit(f"{what}: expected a number or a comma-separated list, got {text!r}")


def bay_diagonals(spec):
    """'5x8' -> the four plan angles from bay centre to its four corners."""
    try:
        w, l = [float(v) for v in spec.lower().replace(",", "x").split("x")]
    except ValueError:
        sys.exit(f"--bay: expected WxL, e.g. 5x8, got {spec!r}")
    t = math.degrees(math.atan2(w, l))
    return [round(v, 1) for v in (t, 180 - t, 180 + t, 360 - t)]


def discover_pier_file():
    """Find a project pier-geometry JSON when --pier-file is omitted."""
    env = os.environ.get("SWEEP_PIER_FILE")
    here = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()
    names = ("piers.json", "vault_piers.json", "pier_geometry.json")
    candidates = []
    if env:
        candidates.append(os.path.expanduser(os.path.expandvars(env)))
    for d in (cwd, here, os.path.dirname(here)):
        candidates.extend(os.path.join(d, n) for n in names)
    seen = set()
    for path in candidates:
        path = os.path.abspath(path)
        if path in seen:
            continue
        seen.add(path)
        if os.path.isfile(path):
            return path
    return None


def _xyz(value, *, origin=(0.0, 0.0, 0.0), rings=None, label="point",
         default_y=None):
    """Resolve a pier point from [x,z], [x,y,z], {x,z}, or polar JSON.
    A point without its own Y gets default_y (the file's
    geometry.plan_datum_y when it has one), else the origin Y."""
    rings = rings or {}
    ox, oy, oz = origin
    if default_y is not None:
        oy = float(default_y)
    if isinstance(value, (list, tuple)):
        if len(value) == 2:
            return float(value[0]), oy, float(value[1])
        if len(value) == 3:
            return float(value[0]), float(value[1]), float(value[2])
        raise ValueError(f"{label}: coordinate list must be [x,z] or [x,y,z]")
    if not isinstance(value, dict):
        raise ValueError(f"{label}: expected a coordinate list or object")

    if "x" in value and "z" in value:
        return float(value["x"]), float(value.get("y", oy)), float(value["z"])

    radius = value.get("radius", value.get("r"))
    if radius is None and "ring" in value:
        ring = rings.get(value["ring"])
        if ring is None:
            raise ValueError(f"{label}: ring {value['ring']!r} is not defined")
        if isinstance(ring, dict):
            radius = ring.get("radius", ring.get("r"))
        else:
            radius = ring
    angle = value.get("angle", value.get("theta"))
    if radius is not None and angle is not None:
        # Plan convention for JSON polar points: 0 deg = +X, +90 deg = +Z.
        a = math.radians(float(angle))
        r = float(radius)
        x = ox + r * math.cos(a)
        z = oz + r * math.sin(a)
        y = float(value.get("y", oy))
        return x, y, z

    raise ValueError(
        f"{label}: use x/z coordinates, [x,z], [x,y,z], or radius+angle/ring+angle")


def load_pier_pair(path, start_name, end_name):
    path = os.path.abspath(os.path.expanduser(os.path.expandvars(path)))
    with open(path) as f:
        root = json.load(f)
    piers = root.get("piers", root) if isinstance(root, dict) else None
    if not isinstance(piers, dict):
        raise ValueError("pier file must be an object, optionally with a top-level 'piers' object")

    origin_raw = root.get("origin", [0, 0, 0]) if isinstance(root, dict) else [0, 0, 0]
    if isinstance(origin_raw, dict):
        origin = (float(origin_raw.get("x", 0)), float(origin_raw.get("y", 0)),
                  float(origin_raw.get("z", 0)))
    elif len(origin_raw) == 2:
        origin = (float(origin_raw[0]), 0.0, float(origin_raw[1]))
    elif len(origin_raw) == 3:
        origin = tuple(float(v) for v in origin_raw)
    else:
        raise ValueError("origin must be [x,z], [x,y,z], or {x,y,z}")
    rings = root.get("rings", {}) if isinstance(root, dict) else {}
    # sweep-piers-v1 files keep the springing level as geometry.plan_datum_y
    geometry = root.get("geometry", {}) if isinstance(root, dict) else {}
    default_y = None
    if isinstance(geometry, dict) and geometry.get("plan_datum_y") is not None:
        default_y = float(geometry["plan_datum_y"])

    def get_named(name):
        if name in piers:
            return piers[name]
        folded = [k for k in piers if str(k).casefold() == str(name).casefold()]
        if len(folded) == 1:
            return piers[folded[0]]
        available = ", ".join(sorted(str(k) for k in piers)[:20])
        raise KeyError(f"pier {name!r} not found (available: {available or 'none'})")

    a = _xyz(get_named(start_name), origin=origin, rings=rings, label=start_name,
             default_y=default_y)
    b = _xyz(get_named(end_name), origin=origin, rings=rings, label=end_name,
             default_y=default_y)
    return path, a, b


def endpoint_yaw(start, end, mode="revolve"):
    """Yaw that aligns the sweep plane/run with the XZ direction start -> end."""
    dx = end[0] - start[0]
    dz = end[2] - start[2]
    span = math.hypot(dx, dz)
    if span <= 1e-9:
        raise ValueError("start and end piers have the same X/Z position")
    # voxelise() turns local (x, z) into world (x*cos + z*sin, -x*sin + z*cos)
    if mode == "revolve":
        # Revolved arch lies in local X/Y, so its plan direction is local +X,
        # which lands on world (cos yaw, -sin yaw).
        yaw = math.degrees(math.atan2(-dz, dx)) % 360.0
    else:
        # Extrusion runs along local +Z, which lands on world
        # (sin yaw, cos yaw). (The pre-Gothic script used atan2(dx, -dz), which
        # sent any run with a Z component the wrong way.)
        yaw = math.degrees(math.atan2(dx, dz)) % 360.0
    return yaw, span, end[1] - start[1]


def apply_pier_geometry(ap, args):
    """Resolve --start-pier/--end-pier into automatic yaw and a measured span."""
    have_start = bool(args.start_pier)
    have_end = bool(args.end_pier)
    if have_start != have_end:
        ap.error("--start-pier and --end-pier must be used together")
    if not have_start:
        return None
    if args.bay:
        ap.error("--bay cannot be combined with --start-pier/--end-pier")
    if args.yaw is not None:
        ap.error("do not give --yaw with named piers; use --yaw-offset for calibration")

    if args.pier_file:
        pier_file = os.path.abspath(os.path.expanduser(os.path.expandvars(args.pier_file)))
        if not os.path.isfile(pier_file):
            ap.error(f"--pier-file: not found: {pier_file}")
    else:
        pier_file = discover_pier_file()
    if not pier_file:
        ap.error("named piers need --pier-file JSON (or piers.json/vault_piers.json in the project folder)")
    try:
        pier_file, start, end = load_pier_pair(pier_file, args.start_pier, args.end_pier)
        yaw, span, dy = endpoint_yaw(start, end, args.mode)
    except KeyError as e:
        ap.error(f"pier geometry: {e.args[0] if e.args else e}")
    except (OSError, ValueError, TypeError, AttributeError) as e:
        ap.error(f"pier geometry: {e}")

    yaw = (yaw + float(args.yaw_offset)) % 360.0
    args.yaw = f"{yaw:.10g}"
    args.pier_span = span
    args.pier_start_xyz = start
    args.pier_end_xyz = end
    print(f"pier geometry: {args.start_pier} -> {args.end_pier}")
    print(f"  file  {pier_file}")
    print(f"  start ({start[0]:.3f}, {start[1]:.3f}, {start[2]:.3f})")
    print(f"  end   ({end[0]:.3f}, {end[1]:.3f}, {end[2]:.3f})")
    print(f"  plan span = {span:.3f} blocks" + (f"  (delta Y {dy:+.3f})" if abs(dy) > 1e-9 else ""))
    print(f"  auto yaw  = {yaw:.6f} deg" + (f"  (includes {args.yaw_offset:+g} deg offset)" if args.yaw_offset else ""))
    return span


# ----------------------------------------------------------------------------
# Gothic (two-centred pointed) rib
# ----------------------------------------------------------------------------
def gothic_fit(span, rise):
    """Fit one symmetric two-centred pointed arch to a full spring-to-spring
    span and a spring-to-crown rise, both measured on the inner edge (first
    column) of the profile.

    Returns (half run, circle radius, sweep angle of EACH half in degrees).
    The two halves are mirror images of each other about the crown plane.
    """
    span = float(span)
    rise = float(rise)
    if span <= 0:
        raise ValueError("the span must be greater than 0")
    if rise <= 0:
        raise ValueError("the rise must be greater than 0")
    run = span / 2.0
    if rise < run - 1e-9:
        raise ValueError(
            f"rise {rise:g} is less than half the span ({run:g}). A two-centred "
            f"pointed arch needs a rise of at least half the span: exactly half "
            f"gives a round arch, about 0.866 x the span an equilateral one")
    radius = (run * run + rise * rise) / (2.0 * run)
    angle = math.degrees(math.atan2(rise, radius - run))
    return run, radius, angle


def _gothic_part_note(args):
    """Which pier a single half springs from, when that is well defined."""
    if args.gothic_part == "full" or getattr(args, "pier_start_xyz", None) is None:
        return ""
    off = float(args.yaw_offset) % 360.0
    if min(off, 360.0 - off) < 1e-9:
        first = "end"          # local +X points start -> end
    elif abs(off - 180.0) < 1e-9:
        first = "start"
    else:
        return ""
    other = "start" if first == "end" else "end"
    pier = first if args.gothic_part == "left" else other
    return f"  (the half that springs from the {pier} pier)"


def configure_gothic(ap, args, span):
    """--gothic: work out radius and half-sweep angle from the span and rise."""
    if not args.gothic:
        return
    if span is None:
        ap.error("--gothic needs a span: give --start-pier and --end-pier, or --span")

    spring_y = args.spring_y
    start = getattr(args, "pier_start_xyz", None)
    end = getattr(args, "pier_end_xyz", None)
    if start is not None and spring_y is None:
        if abs(float(start[1]) - float(end[1])) > 1e-6:
            ap.error(f"the two piers spring at different heights (Y {start[1]:g} and "
                     f"{end[1]:g}); a pointed rib is symmetric, so give --spring-y "
                     f"to choose one springing level")
        spring_y = (float(start[1]) + float(end[1])) / 2.0

    chosen = [n for n, v in (("--rise", args.rise),
                             ("--rise-ratio", args.rise_ratio),
                             ("--crown-y", args.crown_y)) if v is not None]
    if len(chosen) != 1:
        ap.error("--gothic needs exactly one of --rise, --rise-ratio or --crown-y"
                 + (f" (got {' and '.join(chosen)})" if chosen else ""))

    if args.rise is not None:
        rise = float(args.rise)
        source = f"fixed rise {rise:g}"
    elif args.rise_ratio is not None:
        if args.rise_ratio < 0.5 - 1e-12:
            ap.error("--rise-ratio must be at least 0.5 (0.5 = round arch, "
                     "0.866 = equilateral, higher = steeper lancet)")
        rise = span * float(args.rise_ratio)
        source = f"rise ratio {args.rise_ratio:g} x full span"
    else:
        if spring_y is None:
            ap.error("--crown-y needs a springing height: use named piers, or give --spring-y")
        rise = float(args.crown_y) - float(spring_y)
        if rise <= 0:
            ap.error(f"--crown-y {args.crown_y:g} is not above the springing level "
                     f"Y {spring_y:g}")
        source = f"absolute crown Y {args.crown_y:g}"

    try:
        run, radius, angle = gothic_fit(span, rise)
    except ValueError as e:
        ap.error(f"gothic: {e}")

    args.gothic_span = float(span)
    args.gothic_rise_resolved = float(rise)
    args.radius = f"{radius:.12g}"
    args.angle = f"{angle:.12g}"
    args.spring_y_resolved = spring_y
    args.crown_y_resolved = None if spring_y is None else float(spring_y) + rise

    print("gothic fit:")
    print(f"  source      = {source}")
    print(f"  full span   = {span:.6f}")
    print(f"  half run    = {run:.6f}")
    print(f"  rise        = {rise:.6f}")
    print(f"  radius      = {radius:.6f}")
    print(f"  half sweep  = {angle:.6f} deg")
    if spring_y is not None:
        print(f"  spring Y    = {spring_y:.6f}")
        print(f"  crown Y     = {spring_y + rise:.6f}")
    print(f"  output part = {args.gothic_part}{_gothic_part_note(args)}")


def suffix(combo, varying):
    parts = []
    for key, values in varying.items():
        if len(values) > 1:
            field = {"r": "radius", "a": "angle", "y": "yaw", "l": "length"}[key]
            parts.append(f"_{key}{combo[field]:g}".replace(".", "p"))
    return "".join(parts)


def collect_inputs(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for f in sorted(os.listdir(p)):
                if f.lower().endswith((".png", ".bmp", ".tif", ".tiff", ".jpg", ".jpeg")):
                    out.append(os.path.join(p, f))
        else:
            out.append(p)
    return out


def discover_ramp_file(ramp_name):
    """Find a ramps JSON for --ramp when --ramp-file was omitted.

    This keeps --ramp useful in the common project layout while still failing
    clearly if no suitable JSON is available.
    """
    env = os.environ.get("LT_RAMPS_FILE")
    here = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()
    names = ("ramps.json", "gothic_ramps.json", "lt_ramps.json")
    candidates = []
    if env:
        candidates.append(os.path.expanduser(os.path.expandvars(env)))
    for d in (cwd, here, os.path.dirname(here)):
        candidates.extend(os.path.join(d, n) for n in names)

    seen = set()
    for path in candidates:
        path = os.path.abspath(path)
        if path in seen or not os.path.isfile(path):
            continue
        seen.add(path)
        try:
            with open(path) as f:
                data = json.load(f)
        except (OSError, ValueError):
            continue
        if ramp_name in data:
            return path
    return None


def validate_args(ap, args):
    if args.ppb <= 0:
        ap.error("--ppb must be greater than 0")
    if args.samples < 1:
        ap.error("--samples must be at least 1")
    if not 0.0 <= args.air_weight <= 1.0:
        ap.error("--air-weight must be between 0 and 1")
    if not 0.0 <= args.threshold <= 1.0:
        ap.error("--threshold must be between 0 and 1")
    if not 0.0 <= args.air_level <= 1.0:
        ap.error("--air-level must be between 0 and 1")
    if args.max_voxels < 1:
        ap.error("--max-voxels must be at least 1")
    if args.hollow < 0:
        ap.error("--hollow cannot be negative")
    if args.workers < 0:
        ap.error("--workers must be 0 (all CPUs) or a positive integer")
    if args.stl_scale <= 0:
        ap.error("--stl-scale must be greater than 0")
    if args.density_limit < 1:
        ap.error("--density-limit must be at least 1")
    if args.span is not None and args.span <= 0:
        ap.error("--span must be greater than 0")

    if args.gothic:
        if args.mode != "revolve":
            ap.error("--gothic needs --mode revolve (the default)")
        given = [n for n, v in (("--radius", args.radius), ("--angle", args.angle))
                 if v is not None]
        if given:
            ap.error("--gothic works out --radius and --angle from the span and "
                     f"rise; leave off {' and '.join(given)}")
    else:
        stray = [n for n, v in (("--rise", args.rise),
                                ("--rise-ratio", args.rise_ratio),
                                ("--crown-y", args.crown_y),
                                ("--spring-y", args.spring_y)) if v is not None]
        if args.gothic_part != "full":
            stray.append("--gothic-part")
        if stray:
            verb = "works" if len(stray) == 1 else "work"
            ap.error(f"{', '.join(stray)} only {verb} together with --gothic "
                     "(add --gothic to build a pointed rib)")
        if args.span is not None and not args.fit_span:
            ap.error("--span is only used by --gothic or --fit-span")

    if not args.inputs and not args.geometry_only:
        ap.error("give at least one profile image or folder "
                 "(or use --geometry-only to check the numbers)")

def build_parser():
    ap = argparse.ArgumentParser(
        description="Sweep a profile image into a Minecraft schematic in one step: "
                    "a round arch (revolve), a straight run (extrude), or a pointed "
                    "Gothic rib (--gothic), optionally placed between named piers.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("inputs", nargs="*",
                    help="profile image(s) or a folder of them (can be left out "
                         "with --geometry-only)")

    g = ap.add_argument_group("shape")
    g.add_argument("--mode", choices=["revolve", "extrude"], default="revolve")
    g.add_argument("--angle", default=None,
                   help="revolve: sweep angle in degrees (comma-separated list "
                        "allowed). Defaults to 90; --gothic works it out")
    g.add_argument("--radius", default=None,
                   help="revolve: blocks from the axis to the inner edge of the "
                        "profile (comma-separated list allowed). Defaults to 0; "
                        "--gothic works it out")
    g.add_argument("--length", default="16",
                   help="extrude: run length in blocks (comma-separated list allowed)")
    g.add_argument("--yaw", default=None,
                   help="rotate the whole sweep about the vertical axis, in degrees "
                        "(no resampling loss). Comma-separated list allowed; "
                        "'quad' means 45,135,225,315. Defaults to 0 unless named "
                        "piers calculate it automatically")
    g.add_argument("--bay", default=None, metavar="WxL",
                   help="bay width x length, e.g. 5x8 - sets --yaw to the four plan "
                        "diagonals of that bay")
    g.add_argument("--hollow", type=int, nargs="?", const=1, default=0,
                   metavar="N",
                   help="keep only an N-block-deep shell (bare --hollow means 1)")
    g.add_argument("--geometry-only", action="store_true",
                   help="work out and print the pier/Gothic geometry and the sweeps "
                        "that would be built, then stop without voxelising")

    g = ap.add_argument_group("named piers")
    g.add_argument("--pier-file", default=None, metavar="JSON",
                   help="named pier geometry. If omitted, looks for piers.json, "
                        "vault_piers.json, or pier_geometry.json (or $SWEEP_PIER_FILE)")
    g.add_argument("--start-pier", default=None, metavar="NAME",
                   help="start pier name from --pier-file; requires --end-pier")
    g.add_argument("--end-pier", default=None, metavar="NAME",
                   help="end pier name from --pier-file; automatically sets yaw "
                        "and measures the plan span")
    g.add_argument("--yaw-offset", type=float, default=0.0, metavar="DEG",
                   help="calibration offset added to automatically calculated pier yaw")
    g.add_argument("--fit-span", action="store_true",
                   help="also fit plain geometry to the span: extrude sets "
                        "--length=span; revolve derives a single-circle chord angle "
                        "from --radius (use only when that is the intended arch "
                        "geometry). Not needed with --gothic")
    g.add_argument("--span", type=float, default=None, metavar="BLOCKS",
                   help="full spring-to-spring span by hand, for --gothic or "
                        "--fit-span; overrides the pier span when piers are given")

    g = ap.add_argument_group("Gothic pointed rib (--gothic)")
    g.add_argument("--gothic", action="store_true",
                   help="build a symmetric pointed rib from two mirrored circular "
                        "halves that meet at the crown. Span from the piers or "
                        "--span, height from one of --rise, --rise-ratio, --crown-y")
    g.add_argument("--rise", "--gothic-rise", dest="rise", type=float, default=None,
                   metavar="BLOCKS",
                   help="spring-to-crown rise of the rib's inner edge; at least "
                        "half the span")
    g.add_argument("--rise-ratio", type=float, default=None, metavar="RATIO",
                   help="rise as a fraction of the FULL span: 0.5 = round arch, "
                        "0.866 = equilateral, higher = steeper lancet")
    g.add_argument("--crown-y", type=float, default=None, metavar="Y",
                   help="absolute Y of the crown; rise = crown Y minus spring Y "
                        "(spring Y comes from the piers or --spring-y)")
    g.add_argument("--spring-y", type=float, default=None, metavar="Y",
                   help="springing level, for --crown-y without pier Y data or "
                        "when the two piers spring at different heights")
    g.add_argument("--gothic-part", choices=["full", "left", "right"], default="full",
                   help="the whole pointed rib, or one half: left = the first "
                        "half, springing from the end pier; right = its mirror, "
                        "springing from the start pier (swapped by --yaw-offset 180)")

    g = ap.add_argument_group("profile image")
    g.add_argument("--ppb", type=float, default=16.0,
                   help="pixels per block in the profile image")
    g.add_argument("--threshold", type=float, default=0.5,
                   help="pixels darker than this are solid (0-1)")
    g.add_argument("--invert", action="store_true",
                   help="light pixels are solid instead")
    g.add_argument("--transpose", action="store_true",
                   help="swap the image axes (soffit drawn at the bottom, not the left)")
    g.add_argument("--flip-x", action="store_true")
    g.add_argument("--flip-y", action="store_true")
    g.add_argument("--no-trim", action="store_true",
                   help="keep blank border around the profile")
    g.add_argument("--samples", type=int, default=3,
                   help="supersamples per block axis (3 = 27 samples per block)")
    g.add_argument("--air-weight", type=float, default=0.7,
                   help="air vote weight; lower keeps thin detail")

    g = ap.add_argument_group("blocks")
    g.add_argument("--block", default="minecraft:stone")
    g.add_argument("--paint", action="store_true",
                   help="read the grey levels inside the profile as tone and "
                        "map them onto a ramp, so relief sweeps with the "
                        "moulding. Needs --ramp-file or --palette")
    g.add_argument("--ramp-file", default=None, metavar="JSON",
                   help="lt_shade ramps file to take the palette from")
    g.add_argument("--ramp", default=None, metavar="NAME",
                   help="which ramp in that file (dark to light)")
    g.add_argument("--palette", default=None,
                   help="comma-separated block ids, dark to light, instead "
                        "of a ramp file")
    g.add_argument("--air-level", type=float, default=0.97,
                   help="in --paint mode, pixels lighter than this are air "
                        "(ignored if the image has real transparency)")
    g.add_argument("--mc", default=DEFAULT_MC, choices=sorted(DATA_VERSIONS),
                   help="Minecraft version to stamp on the schematic")
    g.add_argument("--data-version", type=int, default=None,
                   help="override the DataVersion number directly")

    g = ap.add_argument_group("outputs")
    g.add_argument("--out", default="out", help="output folder")
    g.add_argument("--no-schem", action="store_true",
                   help="skip the .schem - LittleTiles output only")
    g.add_argument("--no-offset", action="store_true",
                   help="zero the paste offset instead of storing the sweep origin")
    g.add_argument("--no-preview", action="store_true")
    g.add_argument("--stl", action="store_true", help="also write an STL")
    g.add_argument("--stl-scale", type=float, default=1.0,
                   help="STL units per block")
    g.add_argument("--bp", action="store_true",
                   help="also write an Axiom blueprint (.bp)")
    g.add_argument("--bp-out", default=None, metavar="DIR",
                   help="where the .bp files go (default: --out)")
    g.add_argument("--bp-author", default="schem_to_bp.py",
                   help="Author field stored in the blueprint")
    g.add_argument("--lt", action="store_true",
                   help="also write the LittleTiles import string (.txt)")
    g.add_argument("--lt-struct", action="store_true",
                   help="also write a .ltstruct blueprint for "
                        "littletiles_batch.py inject")
    g.add_argument("--lt-grid", type=int, default=16,
                   choices=[1, 2, 4, 8, 16, 32],
                   help="LittleTiles grid: one source block becomes one grid "
                        "unit, so the finished piece is 1/N the size. 16 is "
                        "LittleTiles' default and writes no grid key")
    g.add_argument("--density-limit", type=int, default=2048,
                   help="warn above this many tiles in any one block "
                        "(match your LittleTiles maxAllowedDensity)")
    g.add_argument("--lt-out", default=None, metavar="DIR",
                   help="where the LittleTiles files go (default: --out). "
                        "Point this at ~/Desktop/lt/converted to feed inject "
                        "directly")

    g = ap.add_argument_group("performance")
    g.add_argument("--workers", "-j", type=int, default=1, metavar="N",
                   help="run N sweeps in parallel; 0 means one per CPU core")
    g.add_argument("--max-voxels", type=int, default=SCHEM_MAX_BYTES,
                   help="refuse a sweep whose bounding box is bigger than this, "
                        "as a guard against typos. Only solid blocks are kept "
                        "in memory, so a big box is fine; the default is the "
                        "most a .schem can hold")
    return ap


def main():
    ap = build_parser()
    args = ap.parse_args()
    validate_args(ap, args)

    # 1. geometry: named piers -> yaw + span, optional --span override, Gothic fit
    pier_span = apply_pier_geometry(ap, args)
    span = pier_span
    if args.span is not None:
        if span is not None and abs(float(args.span) - span) > 1e-6:
            print(f"  span override = {args.span:.3f} blocks (pier span was {span:.3f})")
        span = float(args.span)
    configure_gothic(ap, args, span)

    # the plain defaults, for whatever the piers / Gothic fit did not set
    if args.yaw is None:
        args.yaw = "0"
    if args.radius is None:
        args.radius = "0"
    if args.angle is None:
        args.angle = "90"

    if args.bay:
        args.yaw = ",".join(f"{v:g}" for v in bay_diagonals(args.bay))
        print(f"bay {args.bay} -> yaw angles {args.yaw}")
    if args.yaw.strip().lower() == "quad":
        args.yaw = "45,135,225,315"

    radii = num_list(args.radius, "--radius")
    angles = num_list(args.angle, "--angle")
    lengths = num_list(args.length, "--length")
    yaws = num_list(args.yaw, "--yaw")
    if not radii or any(r < 0 for r in radii):
        ap.error("--radius must contain one or more non-negative numbers")
    if not angles or any(a <= 0 or a > 360 for a in angles):
        ap.error("--angle must be greater than 0 and no more than 360 degrees")
    if not lengths or any(n <= 0 for n in lengths):
        ap.error("--length must contain one or more numbers greater than 0")
    if not yaws:
        ap.error("--yaw must contain at least one number")

    if args.fit_span and args.gothic:
        print("note: --gothic already fits the rib to the span, so --fit-span "
              "changes nothing here")
    elif args.fit_span:
        if span is None:
            ap.error("--fit-span needs --start-pier and --end-pier (or --span)")
        if args.mode == "extrude":
            lengths = [span]
            args.length = f"{span:.10g}"
            print(f"  fit span  -> extrusion length {span:.6f}")
        else:
            if len(radii) != 1:
                ap.error("--fit-span in revolve mode requires exactly one --radius")
            r = radii[0]
            if r <= 0:
                ap.error("--fit-span in revolve mode requires --radius > 0")
            if span > 2.0 * r + 1e-9:
                ap.error(f"span {span:.3f} exceeds diameter {2*r:.3f}; "
                         "a single circular arc of this radius cannot span the endpoints")
            fitted = math.degrees(2.0 * math.asin(min(1.0, span / (2.0 * r))))
            angles = [fitted]
            args.angle = f"{fitted:.10g}"
            print(f"  fit span  -> circular chord angle {fitted:.6f} deg at radius {r:g}")
            print("  note: --fit-span uses a single circular chord; use --gothic for "
                  "a pointed two-centred rib between the piers")

    if args.mode == "revolve":
        combos = [dict(radius=r, angle=a, yaw=y, length=0.0)
                  for r in radii for a in angles for y in yaws]
        varying = {"r": radii, "a": angles, "y": yaws}
    else:
        combos = [dict(radius=0.0, angle=0.0, yaw=y, length=n)
                  for n in lengths for y in yaws]
        varying = {"l": lengths, "y": yaws}

    shape = f"gothic-{args.gothic_part}" if args.gothic else args.mode
    if args.geometry_only:
        print(f"geometry only - nothing built. mode={shape}, "
              f"{len(combos)} sweep(s) per profile image:")
        for c in combos:
            if args.mode == "revolve":
                print(f"  radius {c['radius']:.6f}  angle {c['angle']:.6f} deg  "
                      f"yaw {c['yaw']:.6f} deg")
            else:
                print(f"  length {c['length']:.6f}  yaw {c['yaw']:.6f} deg")
        return

    # 2. blocks
    if args.data_version is None:
        args.data_version = DATA_VERSIONS[args.mc]

    if args.ramp and not args.ramp_file and not args.palette:
        found = discover_ramp_file(args.ramp)
        if found:
            args.ramp_file = found
            print(f"using ramp file {found}")
        else:
            sys.exit(f"--ramp {args.ramp!r} names a ramp, but no ramps JSON was found. "
                     "Add --ramp-file /path/to/ramps.json or set LT_RAMPS_FILE.")

    if args.palette:
        args.blocks = [b if ":" in b else "minecraft:" + b
                       for b in args.palette.replace(" ", "").split(",") if b]
    elif args.ramp_file:
        args.ramp_file = os.path.expanduser(os.path.expandvars(args.ramp_file))
        with open(args.ramp_file) as f:
            ramps = json.load(f)
        key = args.ramp
        if key is None:
            plain = [k for k in ramps
                     if not k.endswith(("_stairs", "_slab", "_wall"))]
            if len(plain) != 1:
                sys.exit("--ramp: pick one of %s" % ", ".join(sorted(ramps)))
            key = plain[0]
        if key not in ramps:
            sys.exit("no ramp %r in %s (have %s)"
                     % (key, args.ramp_file, ", ".join(sorted(ramps))))
        args.blocks = [b if ":" in b else "minecraft:" + b for b in ramps[key]]
    else:
        args.blocks = [args.block]
    if not args.blocks:
        sys.exit("palette is empty")
    if len(args.blocks) > 255:
        sys.exit("palette has %d blocks; sweep2schem supports at most 255 materials"
                 % len(args.blocks))
    if len(set(args.blocks)) != len(args.blocks):
        sys.exit("palette contains duplicate block ids; remove duplicates so schematic "
                 "palette indices stay unambiguous")
    if args.paint and len(args.blocks) < 2:
        sys.exit("--paint needs at least two palette blocks: give --ramp-file/--ramp "
                 "or --palette")

    # 3. profiles -> one task per image per sweep
    files = collect_inputs(args.inputs)
    if not files:
        sys.exit("no images found")

    pal = (f"{len(args.blocks)}-step ramp" if args.paint else args.block)
    print(f"mode={shape}  ppb={args.ppb}  block={pal}  "
          f"DataVersion={args.data_version}  hollow={args.hollow or 'off'}")
    print(f"{len(files)} image(s) x {len(combos)} sweep(s) "
          f"= {len(files) * len(combos)} schematic(s)")

    tasks = []
    for f in files:
        base = os.path.splitext(os.path.basename(f))[0]
        try:
            mask, tone = load_profile(f, args, args.blocks)
        except Exception as e:
            print(f"[{base}] FAILED to read: {e}")
            continue
        if mask is None:
            print(f"[{base}] skipped: no solid pixels "
                  f"(try --invert or --threshold)")
            continue
        h_px, w_px = mask.shape
        print(f"[{base}] profile {w_px} x {h_px} px  ->  "
              f"{w_px / args.ppb:.2f} x {h_px / args.ppb:.2f} blocks")
        for combo in combos:
            job = copy.copy(args)
            for k, v in combo.items():
                setattr(job, k, v)
            tasks.append((mask, base + suffix(combo, varying), job, tone))

    if not tasks:
        sys.exit("no valid sweep tasks were produced")

    # 4. run
    requested_workers = args.workers if args.workers > 0 else (os.cpu_count() or 1)
    workers = max(1, min(requested_workers, len(tasks)))
    if requested_workers > 1 and len(tasks) == 1:
        print("note: -j/--workers parallelizes independent sweeps; this command has "
              "only one sweep, so it will use one worker")
    written = 0

    if workers > 1:
        print(f"running on {workers} worker processes")
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for ok, log in ex.map(_run, tasks):
                print("\n".join(log))
                written += ok
    else:
        for task in tasks:
            ok, log = _run(task)
            print("\n".join(log))
            written += ok

    print(f"done - {written} sweep(s) completed; outputs are in {args.out}/")


if __name__ == "__main__":
    main()
