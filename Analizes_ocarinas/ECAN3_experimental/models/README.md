# Input models (not committed)

The STL files are third-party designs by **E.CAN3 / ECAN3** and are **not** stored in git (see `.gitignore`). Put them here under the names below to rerun the analysis. The SHA-256 hashes identify the exact files analysed.

| File here | Original file name | Source | Licence (as shown on the page) | SHA-256 |
| --- | --- | --- | --- | --- |
| `v0n3_10h_C5-F6.stl` | `oc_v0n3-v2_by_ec (1).stl` (STL header `OC_V0N3-V2_F2-BY_EC`) | Printables, [@ECAN3_637457](https://www.printables.com/@ECAN3_637457) ("10 Hole Ocarina V0N3 C5 - F6") | not checked: Printables served a bot check | `b954b85ccf38b73501b0c6782f7c32e3b9e37f15c77ac9a67bd51ef5a44018dd` |
| `oot_12h_AC_v3.stl` | `oc_oot_12h-ac_Version-3_no_triforce (1).stl` (header `OC_OOT_12H-AC_V3_HYBRID_H5_T1`) | MakerWorld, [Ocarina of Time - 12 hole Alto C Ocarina](https://makerworld.com/en/models/429897-ocarina-of-time-12-hole-alto-c-ocarina) | Creative Commons Attribution-NonCommercial | `0a83a893357310ca12ccced720d2cacd7cb7272e1f8ccb865eada96d080404a5` |
| `eclipse_12h_AC_assembly.stl` | `obj_1_Assembly.stl` (Bambu Studio export of the 3MF) | MakerWorld, [Eclipse – Twelve-Hole Alto C Ocarina](https://makerworld.com/en/models/1263569-eclipse-twelve-hole-alto-c-ocarina) | Standard Digital File License | `b2c2591df6c61b67729f0691cc8c63faa75fd59f1a9e3984903e233831ee4583` |
| `user_10h_rough_volume_EMPTY.stl` | `10 holes rough volume with simple booleans.stl` | user's Blender export | — | `4fea5e6a…` (84 bytes: header only, **0 triangles**) |

Notes

- The Eclipse export holds four bodies. Only the largest (the ocarina, 125,200 mm³ of plastic) is analysed. The other three are the breakaway pre-support block (19,106 mm³) and two thin surface shells that coincide with the outer skin, consistent with the "Fuzzy" painted regions of the 3MF (6,498 and 3,760 mm³). The page states the model is pre-supported and offered in Fuzzy variants.
- The user's Blender volume file is empty (the export probably had nothing selected). Its reported Blender 3D-Print-Toolbox volume, 66,784.2452 mm³, is used as a reference number in the write-up.
- Designer print settings quoted on the OOT page: 0.4 mm nozzle, 2 walls, 0.2 mm layers, 4 top/bottom layers, 20 % gyroid infill, 5 mm brim, no support, printed standing on the mouthpiece.
