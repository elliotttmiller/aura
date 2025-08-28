import os
import sys
import time
import math
import bpy
import bmesh
import addon_utils
import logging
from argparse import ArgumentParser

# --- Setup logger ---
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# --- Utility: Generate output file path ---
def get_output_path(prompt: str) -> str:
    OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    safe_name = "".join(c for c in prompt.lower() if c.isalnum() or c in (' ', '_')).rstrip()
    safe_name = "_".join(safe_name.split())[:40]
    return os.path.join(OUTPUT_DIR, f"output_{safe_name}.stl")

# --- STATE-OF-THE-ART UPGRADE: AI SIMULATION ---
def simulate_ai_influence(target_obj, prompt: str):
    """
    Parses the prompt for keywords and applies corresponding modifiers
    to simulate an intelligent, creative AI process.
    """
    logger.info(f"Simulating AI influence with prompt: '{prompt}'")
    prompt = prompt.lower()

    if "twist" in prompt or "swirl" in prompt:
        logger.debug("Applying Twist modifier")
        twist_mod = target_obj.modifiers.new(name="AITwist", type='SIMPLE_DEFORM')
        twist_mod.deform_method = 'TWIST'
        twist_mod.angle = math.radians(90)
    
    if "organic" in prompt or "vine" in prompt:
        logger.debug("Applying Displace modifier for organic feel")
        noise_tex = bpy.data.textures.new(name="AI_Noise", type='VORONOID')
        noise_tex.noise_scale = 0.5
        disp_mod = target_obj.modifiers.new(name="AIOrganic", type='DISPLACE')
        disp_mod.texture = noise_tex
        disp_mod.strength = 0.0005
        
    if "geometric" in prompt or "facet" in prompt:
        logger.debug("Applying Decimate modifier for geometric look")
        dec_mod = target_obj.modifiers.new(name="AIGeometric", type='DECIMATE')
        dec_mod.ratio = 0.5

# --- Professional Jewelry Generation Logic ---
def generate_jewelry(specs: dict, prompt: str):
    def get_ring_diameter(us_size): return 12.45 + (us_size * 0.8128)
    def get_stone_diameter(carat, shape): return 6.5 * (carat ** (1./3.))

    ring_diameter_mm = get_ring_diameter(specs['ring_size'])
    ring_radius = (ring_diameter_mm / 2) / 1000

    bm = bmesh.new()
    # *** THE FIX IS HERE ***
    # We create the profile geometry *directly* inside the main bmesh object.
    # This resolves the "ValueError: geom is from another mesh".
    profile_geom = bmesh.ops.create_circle(bm, cap_ends=False, radius=0.001, segments=16)

    # The geometry is now part of 'bm', so we can manipulate it.
    profile_verts = profile_geom['verts']
    for v in profile_verts:
        if v.co.x < 0: v.co.x = 0
    bmesh.ops.translate(bm, verts=profile_verts, vec=(0.001, 0, 0))

    # Now we spin the geometry that is already in 'bm'.
    bmesh.ops.spin(bm, geom=profile_verts, cent=(0,0,0), axis=(0,1,0), steps=128, angle=math.radians(360))

    stone_diameter_mm = get_stone_diameter(specs['stone_carat'], specs['stone_shape'])
    stone_radius = (stone_diameter_mm / 2) / 1000

    # We create the setting in a separate bmesh, then add it to the scene. This is a clean workflow.
    setting_bm = bmesh.new()
    for i in range(4):
        prong = bmesh.ops.create_cone(setting_bm, cap_ends=True, radius1=0.0005, radius2=0.0002, depth=0.004, segments=16)
        angle = i * (math.pi / 2)
        x = math.cos(angle) * (stone_radius * 0.9)
        y = math.sin(angle) * (stone_radius * 0.9)
        bmesh.ops.translate(setting_bm, verts=prong['verts'], vec=(x, y, ring_radius + 0.002))

    main_mesh = bpy.data.meshes.new("GeneratedJewelryMesh")
    bm.to_mesh(main_mesh)
    bm.free()
    main_obj = bpy.data.objects.new("GeneratedJewelry", main_mesh)
    bpy.context.scene.collection.objects.link(main_obj)

    simulate_ai_influence(main_obj, prompt)

    setting_mesh = bpy.data.meshes.new("SettingMesh")
    setting_bm.to_mesh(setting_mesh)
    setting_bm.free()
    setting_obj = bpy.data.objects.new("Setting", setting_mesh)
    bpy.context.scene.collection.objects.link(setting_obj)

    bpy.ops.object.select_all(action='DESELECT')
    main_obj.select_set(True)
    setting_obj.select_set(True)
    bpy.context.view_layer.objects.active = main_obj
    bpy.ops.object.join()

    return main_obj

# --- Main Subprocess Execution ---
def main():
    if '--' not in sys.argv: return
    
    parser = ArgumentParser(description="Aura Blender Generation Engine")
    parser.add_argument("prompt", type=str)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--ring_size", type=float, default=7.0)
    parser.add_argument("--stone_carat", type=float, default=1.0)
    parser.add_argument("--stone_shape", type=str, default='ROUND')
    parser.add_argument("--metal", type=str, default='GOLD')
    
    argv = sys.argv[sys.argv.index('--') + 1:]
    args = parser.parse_args(argv)

    logger.info(f"Received prompt: {args.prompt} | Specs: {vars(args)}")

    try:
        addon_utils.enable("io_mesh_stl")
    except Exception as e:
        logger.warning(f"Could not enable STL add-on: {e}. Attempting export anyway.")

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    generated_obj = generate_jewelry(vars(args), args.prompt)

    if not generated_obj or not generated_obj.data.vertices:
        logger.error('Mesh generation failed. No geometry created.')
        sys.exit(1)

    bpy.context.view_layer.objects.active = generated_obj
    for mod in generated_obj.modifiers:
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except RuntimeError as e:
            logger.warning(f"Could not apply modifier {mod.name}: {e}")

    logger.debug(f'Exporting STL to {args.output}')
    try:
        bpy.ops.object.select_all(action='DESELECT')
        generated_obj.select_set(True)
        bpy.ops.export_mesh.stl(filepath=args.output, use_selection=True, global_scale=1000.0)
        logger.info(f"Exported successfully to: {args.output}")
    except Exception as e:
        logger.exception(f'STL export failed. Reason: {e}')
        sys.exit(1)

if __name__ == "__main__":
    main()

import os
import sys
import time
import math
import bpy
import bmesh
import addon_utils
import logging
from argparse import ArgumentParser


# --- Setup logger ---
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# --- Utility: Generate output file path ---

def get_output_path(prompt: str) -> str:
    OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    safe_name = "".join(c for c in prompt.lower() if c.isalnum() or c in (' ', '_')).rstrip()
    safe_name = "_".join(safe_name.split())[:40]
    return os.path.join(OUTPUT_DIR, f"output_{safe_name}.stl")

# --- STATE-OF-THE-ART UPGRADE: AI SIMULATION ---

def simulate_ai_influence(target_obj, prompt: str):
    """
    Parses the prompt for keywords and applies corresponding modifiers
    to simulate an intelligent, creative AI process.
    """
    logger.info(f"Simulating AI influence with prompt: '{prompt}'")
    prompt = prompt.lower()
    if "twist" in prompt or "swirl" in prompt:
        logger.debug("Applying Twist modifier")
        twist_mod = target_obj.modifiers.new(name="AITwist", type='SIMPLE_DEFORM')
        twist_mod.deform_method = 'TWIST'
        twist_mod.angle = math.radians(90)
    if "organic" in prompt or "vine" in prompt:
        logger.debug("Applying Displace modifier for organic feel")
        noise_tex = bpy.data.textures.new(name="AI_Noise", type='VORONOI')
        noise_tex.noise_scale = 0.5
        disp_mod = target_obj.modifiers.new(name="AIOrganic", type='DISPLACE')
        disp_mod.texture = noise_tex
        disp_mod.strength = 0.0005
    if "geometric" in prompt or "facet" in prompt:
        logger.debug("Applying Decimate modifier for geometric look")
        dec_mod = target_obj.modifiers.new(name="AIGeometric", type='DECIMATE')
        dec_mod.ratio = 0.5

# --- Professional Jewelry Generation Logic ---

def generate_jewelry(specs: dict, prompt: str):
    def get_ring_diameter(us_size): return 12.45 + (us_size * 0.8128)
    def get_stone_diameter(carat, shape): return 6.5 * (carat ** (1./3.))

    ring_diameter_mm = get_ring_diameter(specs['ring_size'])
    ring_radius = (ring_diameter_mm / 2) / 1000

    bm = bmesh.new()
    # Create profile circle directly in bm
    circle_geom = bmesh.ops.create_circle(bm, cap_ends=False, radius=0.001, segments=16)
    for v in circle_geom['verts']:
        if v.co.x < 0: v.co.x = 0
    bmesh.ops.translate(bm, verts=circle_geom['verts'], vec=(0.001, 0, 0))
    edges = circle_geom.get('edges') or circle_geom.get('edge_loop')
    if edges is None:
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        edges = [e for e in bm.edges if e.verts[0] in circle_geom['verts'] and e.verts[1] in circle_geom['verts']]
    bmesh.ops.spin(bm, geom=circle_geom['verts'] + edges, cent=(0,0,0), axis=(0,1,0), steps=128, angle=math.radians(360))

    stone_diameter_mm = get_stone_diameter(specs['stone_carat'], specs['stone_shape'])
    stone_radius = (stone_diameter_mm / 2) / 1000

    setting_bm = bmesh.new()
    for i in range(4):
        prong = bmesh.ops.create_cone(setting_bm, cap_ends=True, radius1=0.0005, radius2=0.0002, depth=0.004, segments=16)
        angle = i * (math.pi / 2)
        x = math.cos(angle) * (stone_radius * 0.9)
        y = math.sin(angle) * (stone_radius * 0.9)
        bmesh.ops.translate(setting_bm, verts=prong['verts'], vec=(x, y, ring_radius + 0.002))

    main_mesh = bpy.data.meshes.new("GeneratedJewelryMesh")
    bm.to_mesh(main_mesh)
    bm.free()
    main_obj = bpy.data.objects.new("GeneratedJewelry", main_mesh)
    bpy.context.scene.collection.objects.link(main_obj)

    simulate_ai_influence(main_obj, prompt)

    setting_mesh = bpy.data.meshes.new("SettingMesh")
    setting_bm.to_mesh(setting_mesh)
    setting_bm.free()
    setting_obj = bpy.data.objects.new("Setting", setting_mesh)
    bpy.context.scene.collection.objects.link(setting_obj)

    bpy.ops.object.select_all(action='DESELECT')
    main_obj.select_set(True)
    setting_obj.select_set(True)
    bpy.context.view_layer.objects.active = main_obj
    bpy.ops.object.join()

    return main_obj

def main():
    if '--' not in sys.argv: return
    parser = ArgumentParser(description="Aura Blender Generation Engine")
    parser.add_argument("prompt", type=str)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--ring_size", type=float, default=7.0)
    parser.add_argument("--stone_carat", type=float, default=1.0)
    parser.add_argument("--stone_shape", type=str, default='ROUND')
    parser.add_argument("--metal", type=str, default='GOLD')

    argv = sys.argv[sys.argv.index('--') + 1:]
    args = parser.parse_args(argv)

    logger.info(f"Received prompt: {args.prompt} | Specs: {vars(args)}")

    try:
        addon_utils.enable("io_mesh_stl")
    except Exception as e:
        logger.warning(f"Could not enable STL add-on: {e}. Attempting export anyway.")

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    generated_obj = generate_jewelry(vars(args), args.prompt)

    if not generated_obj or not generated_obj.data.vertices:
        logger.error('Mesh generation failed. No geometry created.')
        sys.exit(1)

    bpy.context.view_layer.objects.active = generated_obj
    for mod in generated_obj.modifiers:
        bpy.ops.object.modifier_apply(modifier=mod.name)

    logger.debug(f'Exporting STL to {args.output}')
    try:
        bpy.ops.object.select_all(action='DESELECT')
        generated_obj.select_set(True)
        bpy.ops.export_mesh.stl(filepath=args.output, use_selection=True, global_scale=1000.0)
        logger.info(f"Exported successfully to: {args.output}")
    except Exception as e:
        logger.exception(f'STL export failed. Reason: {e}')
        sys.exit(1)

if __name__ == "__main__":
    main()
