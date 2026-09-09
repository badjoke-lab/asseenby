"""Remove Berlin LoD2 GroundSurface meshes from the primary-visible C0.

LoD2 GroundSurface polygons represent building-bottom semantics, not the public
plaza. Keep official LoD2 walls/roofs and the dedicated Hansaplatz reference-
projected ground, but remove these semantic floor polygons so they cannot occlude
the Human reference view after turning or moving.
"""

from __future__ import annotations

import bpy


def main() -> None:
    root = bpy.data.collections.get("C0")
    if root is None:
        raise RuntimeError("Missing C0 collection")

    doomed = [obj for obj in list(bpy.data.objects) if obj.get("source_semantic") == "ground"]
    names = [obj.name for obj in doomed]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)

    root["official_lod2_ground_surfaces_rendered"] = False
    root["official_lod2_removed_ground_surfaces"] = len(doomed)
    root["official_lod2_removed_ground_names"] = ";".join(names[:64])
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(f"Removed Berlin LoD2 GroundSurface occluders: {len(doomed)}")


if __name__ == "__main__":
    main()
