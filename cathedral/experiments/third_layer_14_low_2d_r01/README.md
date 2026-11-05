# Corrected third ambulatory layer — 2D

The current architectural direction is:

| Layer | Vault count | Relationship |
|---|---:|---|
| Inner | 7 | Protected coordinates retained |
| Middle | 7 | Protected coordinates retained |
| Third | 14 | Two lower vaults per parent bay |

Each pair of third-layer vault entrances sits beneath one higher window. The third layer is significantly lower than the other two. This replaces the previous single-vault interpretation of T2/T6.

Open:

- `THIRD_LAYER_14_PLAN.png` — all fourteen new footprint candidates and unchanged inner/middle context.
- `T2_TWO_LOWER_VAULTS.png` — the two lower vaults at the former T2 sector.
- `ONE_WINDOW_TWO_ENTRANCES.png` — the intended elevation rhythm, drawn schematically.

Each sheet has an editable SVG companion. `LOW14_NATIVE_COORDINATES.svg` contains actual native plan-coordinate numbers with display Y inverted. `LOW14_GEOMETRY.json`, `PAIR_REGISTER.json` and `LOW_VAULT_REGISTER.csv` retain full geometry and identity mappings.

W1–W7 project the higher windows onto the shared middle/third-layer boundary. Gray exterior D1–D9 chapel/window bodies remain context from the selected Study D program. Their nine-compartment count is distinct from the third layer's fourteen vaults. The inherited D5 +640 cap remains unadopted context, not a resolved exterior baseline.

Red dividers are new experimental low-vault divisions. Their receiving lines require architectural support design; no pier/shaft dimensions or structural capacity are supplied. The equal half-bay entrance rhythm is tested in plan. It does not certify clear walking widths or actual vault webs.

The elevation is explicitly **dimensionless and diagrammatic**. No third-layer spring, crown or window sill/head elevation has been selected. Its plotted proportions must not be imported as architectural height defaults. Physical SI conversion also remains unresolved.

Sixty plan/export checks pass in `LOW14_QA.json`. Protected parent files are unchanged, and no generator or 3D model is executed. The R05 crossing, working inner/middle generator, Pass 6J and missing F5ZL-C schedule retain their previous status.

Reproduce:

```bash
python -m pip install numpy shapely matplotlib
python scripts/build_low14.py
```

The script reads the included immutable R04 snapshot and writes only this experimental output directory. If original parent paths are absent on another machine, their live hash checks are listed as unavailable rather than claimed passed; the included geometry is sufficient to rebuild the drawings.
