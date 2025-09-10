# File: aura/blender_proc.py
import bpy, bmesh, os, sys
from argparse import ArgumentParser

def main():
    if '--' not in sys.argv: return
    parser = ArgumentParser(description="Aura Blender Post-Processor")
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--ring_size", type=float, default=7.0)
    argv = sys.argv[sys.argv.index('--') + 1:]
    args = parser.parse_args(argv)

    print(f"--- Starting Blender Post-Processing ---")
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
    try:
        bpy.ops.import_scene.obj(filepath=args.input)
    except RuntimeError as e:
        print(f"ERROR: Could not import OBJ file. Reason: {e}", file=sys.stderr); sys.exit(1)
    ai_obj = bpy.context.selected_objects[0]
    if not ai_obj: print("ERROR: OBJ file was empty.", file=sys.stderr); sys.exit(1)

    def get_ring_diameter(us_size): return 12.45 + (us_size * 0.8128)
    ring_diameter_mm = get_ring_diameter(args.ring_size)
    ring_radius = (ring_diameter_mm / 2) / 1000

    shank_bm = bmesh.new()
    profile_geom = bmesh.ops.create_circle(shank_bm, cap_ends=False, radius=0.001, segments=16)
    bmesh.ops.translate(shank_bm, verts=profile_geom['verts'], vec=(0.001, 0, 0))
    bmesh.ops.spin(shank_bm, geom=profile_geom['verts'], cent=(0,0,0), axis=(0,1,0), steps=128)
    shank_mesh = bpy.data.meshes.new("ShankMesh"); shank_bm.to_mesh(shank_mesh); shank_bm.free()
    shank_obj = bpy.data.objects.new("Shank", shank_mesh)
    bpy.context.scene.collection.objects.link(shank_obj)

    print("Assembling AI model with procedural components...")
    bpy.ops.object.select_all(action='DESELECT'); ai_obj.select_set(True)
    bpy.context.view_layer.objects.active = ai_obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    ai_obj.dimensions = (ring_diameter_mm*0.0012, ring_diameter_mm*0.0012, ring_diameter_mm*0.0008)
    ai_obj.location = (0, 0, ring_radius)
    
    bool_mod = shank_obj.modifiers.new(name="AI_Join", type='BOOLEAN')
    bool_mod.object = ai_obj; bool_mod.operation = 'UNION'
    bpy.context.view_layer.objects.active = shank_obj
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    bpy.data.objects.remove(ai_obj, do_unlink=True)
    
    print(f'Exporting final STL to {args.output}')
    try:
        bpy.ops.object.select_all(action='DESELECT'); shank_obj.select_set(True)
        bpy.ops.export_mesh.stl(filepath=args.output, use_selection=True, global_scale=1000.0)
        print(f"Exported successfully.")
    except Exception as e:
        print(f'ERROR: Final STL export failed. Reason: {e}', file=sys.stderr); sys.exit(1)

if __name__ == "__main__":
    main()