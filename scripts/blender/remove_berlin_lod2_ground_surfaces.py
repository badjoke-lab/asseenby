"""Remove Berlin LoD2 GroundSurface meshes from the primary-visible C0.

The LoD2 subset is valuable for cadastral building walls and roofs, but its
GroundSurface polygons are building-bottom semantics rather than a navigable
public plaza surface. In browser review they can read as large flat slabs that
occlude the photographic reference when the Human observer turns or moves.

Keep LoD2 walls/roofs, remove only semantic ground meshes, and let the dedicated
Hansaplatz plaza surface own the walkable foreground.
"""

from __future__ import annotations

import bpy


def main() -> None:
    root = bpy.data.collections.get("C0")
    if root is None:
        raise RuntimeError("Missing C0 collection")

    doomed = [
        obj
        for obj in list(bpy.data.objects)
        if obj.get("source_semantic") == "ground" or obj.name.endswith("_ground")
    ]
    names = [obj.name for obj in doomed]
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)

    root["official_lod2_ground_surfaces_rendered"] = False
    root["official_lod2_removed_ground_surfaces"] = len(doomed)
    root["official_lod2_removed_ground_names"] = ";".join(names[:64])
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(f"Removed Berlin LoD2 ground surfaces from C0: {len(doomed)}")


if __name__ == "__main__":
    main()
