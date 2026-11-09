# R52 QA — separate validation vectors

| Dimension | Check | Observed R52 |
|---|---|---|
| Technical | U01 SHA-256 copy and original QA record equality | PASS |
| Technical | SVG well-formed and named geometry layers (5 cases) | PASS |
| Technical | Repeated run stability; reordered JSON stable IDs | PASS |
| Technical | Invalid mode, unreachable circle, missing outline | REJECTED 3/3 |
| Geometric | U01 native internal tests | PASS 116/116 |
| Geometric | Polygon validity and holes = named openings | PASS 5/5 |
| Geometric | Analytical circle/radius/apex residual | PASS within declared numeric tolerance |
| Geometric | 2x dimensions, 4x area, stable IDs | PASS 5/5 |
| Architectural | Member/junction counts and opening identities vs archival fixtures | PASS 5/5 |
| Architectural | Cathedral jamb/mullion/bearing integration | NOT TESTED |
| Historical | Source-scanned ink registration, original scale bars, historic geometric method | UNVERIFIED |
| Structural | Support load path, masonry joints, stresses, thrust | NOT TESTED |
| Downstream 3D | Blender GLB re-run | NOT IN SCOPE. U01-U05 reports archived, not re-run |

Mandatory next failures: circle intersection 0/1/2 cases, 0 radius, inverted tangent, off-arch crown, pinched narrow stone web, reversed winding, duplicate void IDs, wrong source units, unsupported historical approval, non-closed historical gaps, malformed 3/4/5/6/8 foils, asymmetric springings, mismatched nested bearing widths, shape overlap and disconnected components. Accept only exact geometry or explicit rejection with residual.
