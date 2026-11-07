# Four-window final commands — recovered from supplied terminal logs

The former scratchpad path under /tmp/claude-0/.../scratchpad/rethink is
not a portable source root. Use new_tracery_kit and the corresponding
source images in the research archive.

## Final region classification commands

~~~bash
python3 tracery_regions.py haina_1264.png -o haina_1264_map.png --mirror --glass 51 52
python3 tracery_regions.py haina_1265_v4.png -o haina_1265_map.png --mirror --stone 107 112 113 120 122 126 108 114 115 121 123 127
python3 tracery_regions.py meaux.png -o meaux_map.png --mirror
python3 tracery_regions.py chalons.png -o chalons_map.png --mirror
~~~

## Final mesh exports: explicit --res 0.25

~~~bash
python3 tracery_build.py haina_1264_map.png --res 0.25 -o haina_1264.stl
python3 tracery_build.py haina_1265_map.png --res 0.25 -o haina_1265.stl
python3 tracery_build.py meaux_map.png --res 0.25 -o meaux.stl
python3 tracery_build.py chalons_map.png --res 0.25 -o chalons.stl
~~~

The packaged commands.txt accidentally omitted --res 0.25; default --res
0.2 would generate a different mesh. Always check *_numbers.png before
reusing override IDs; mirror/bridge parameters change region numbering.
Haina 1265 uncorrected mirror gave 42 glass regions, and the final
stone overrides reduced that to 30. All four final user logs reported
one 2D stone piece.

## Mirror source-repair diagnostics
Chalons: x about 1638, overlap 74%, bridges 245, glass 19.
Meaux: x about 1174, overlap 82%, bridges 530, glass 48.
Haina 1264: x about 2060, overlap 76%, bridges 482, glass 21.
Haina 1265: bridges 268, glass 30 after overrides.

Mirror_fill combines original ink and a mirrored copy. Repair should be
logged, reversible and visually overlayed with the untouched source.
One connected region in 2D does not prove watertight mesh or structural
capacity. The original real-size scaling remains unresolved.
