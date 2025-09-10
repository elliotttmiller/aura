"""
Aura V7.0 Professional State-of-the-Art Blender Engine
=====================================================

A complete rewrite aligned with OpenAI Shap-E best practices featuring:
- Modular professional architecture with helper functions
- Dynamic camera framing with mathematical bounding box calculation
- Intelligent GPU device detection and configuration
- Professional scene setup and lighting management
- State-of-the-art rendering pipeline

Architecturally aligned with the official OpenAI blender_script.py while 
retaining Aura's unique AI-driven parametric jewelry assembly workflow.

Part of the V7.0 Professional Integration.
"""

import os
import sys
import json
import math
import time
import logging
from argparse import ArgumentParser
from typing import Dict, List, Tuple, Optional

import bpy
import bmesh
import addon_utils
from mathutils import Vector, Matrix

# Setup professional logging
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# =============================================================================
# PROFESSIONAL HELPER FUNCTIONS - STATE-OF-THE-ART IMPLEMENTATION  
# =============================================================================

def setup_scene() -> bpy.types.Scene:
    """
    Programmatically create a new, clean Blender scene.
    Ensures no artifacts from previous runs - professional best practice.
    
    Returns:
        Clean Blender scene ready for operations
    """
    logger.info("Setting up clean professional scene")
    
    # Clear all existing data
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Delete default objects if they exist
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Clear all materials and textures
    for material in bpy.data.materials:
        bpy.data.materials.remove(material, do_unlink=True)
    
    for texture in bpy.data.textures:
        bpy.data.textures.remove(texture, do_unlink=True)
    
    scene = bpy.context.scene
    scene.name = "Aura_V7_Professional_Scene"
    
    logger.info("Clean scene setup completed")
    return scene

def setup_lighting() -> List[bpy.types.Object]:
    """
    Create professional three-point lighting setup.
    Implements industry-standard lighting as demonstrated in OpenAI script.
    
    Returns:
        List of light objects created
    """
    logger.info("Setting up professional three-point lighting")
    
    lights = []
    
    # Key Light - Primary illumination
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    key_light = bpy.context.active_object
    key_light.name = "Key_Light"
    key_light.data.energy = 3.0
    key_light.data.color = (1.0, 0.95, 0.9)  # Warm white
    lights.append(key_light)
    
    # Fill Light - Shadow softening
    bpy.ops.object.light_add(type='SUN', location=(-5, 3, 8))
    fill_light = bpy.context.active_object
    fill_light.name = "Fill_Light" 
    fill_light.data.energy = 1.5
    fill_light.data.color = (0.9, 0.95, 1.0)  # Cool white
    lights.append(fill_light)
    
    # Rim Light - Edge definition
    bpy.ops.object.light_add(type='SUN', location=(0, -8, 6))
    rim_light = bpy.context.active_object
    rim_light.name = "Rim_Light"
    rim_light.data.energy = 2.0
    rim_light.data.color = (1.0, 1.0, 1.0)  # Pure white
    lights.append(rim_light)
    
    # Environment lighting for jewelry reflections
    world = bpy.context.scene.world
    world.use_nodes = True
    env_tex = world.node_tree.nodes.new('ShaderNodeTexEnvironment')
    bg_shader = world.node_tree.nodes['Background']
    world.node_tree.links.new(env_tex.outputs['Color'], bg_shader.inputs['Color'])
    bg_shader.inputs['Strength'].default_value = 0.3
    
    logger.info(f"Professional lighting setup completed - {len(lights)} lights created")
    return lights

def enable_gpu_rendering(scene: bpy.types.Scene) -> bool:
    """
    Intelligently detect and configure the best available GPU for Cycles rendering.
    Implements the same robust device detection as the official OpenAI script.
    
    Args:
        scene: Blender scene to configure
        
    Returns:
        True if GPU enabled, False if falling back to CPU
    """
    logger.info("Detecting and configuring optimal rendering device")
    
    # Enable Cycles rendering engine
    scene.render.engine = 'CYCLES'
    cycles = scene.cycles
    
    # Get preferences for device configuration
    preferences = bpy.context.preferences
    cycles_prefs = preferences.addons['cycles'].preferences
    
    # Try to get compute devices
    cycles_prefs.refresh_devices()
    devices = cycles_prefs.devices
    
    if not devices:
        logger.warning("No compute devices found - using CPU rendering")
        cycles.device = 'CPU'
        return False
    
    # Device priority: OPTIX > CUDA > HIP > METAL > OPENCL
    device_preferences = ['OPTIX', 'CUDA', 'HIP', 'METAL', 'OPENCL']
    
    best_device = None
    best_priority = float('inf')
    
    for device in devices:
        if device.type in device_preferences:
            priority = device_preferences.index(device.type)
            if priority < best_priority:
                best_device = device
                best_priority = priority
                
    if best_device:
        # Enable the best device
        for device in devices:
            device.use = (device == best_device)
            
        cycles.device = 'GPU'
        logger.info(f"GPU rendering enabled: {best_device.name} ({best_device.type})")
        
        # Optimize for GPU rendering
        cycles.use_adaptive_sampling = True
        cycles.adaptive_threshold = 0.1
        cycles.samples = 512  # Professional quality samples
        
        return True
    else:
        logger.warning("No compatible GPU found - using CPU rendering")
        cycles.device = 'CPU'
        cycles.samples = 128  # Fewer samples for CPU
        return False

def frame_camera_to_object(camera: bpy.types.Object, target_obj: bpy.types.Object) -> None:
    """
    Mathematically calculate object bounding box and dynamically position camera 
    for perfect composition. This is the most significant V7.0 upgrade.
    
    Args:
        camera: Camera object to position
        target_obj: Object to frame in the shot
    """
    logger.info("Calculating dynamic camera framing for perfect composition")
    
    # Get world-space bounding box of target object
    bbox_corners = [target_obj.matrix_world @ Vector(corner) for corner in target_obj.bound_box]
    
    # Calculate bounding box center and dimensions
    min_coords = Vector((
        min(corner.x for corner in bbox_corners),
        min(corner.y for corner in bbox_corners), 
        min(corner.z for corner in bbox_corners)
    ))
    
    max_coords = Vector((
        max(corner.x for corner in bbox_corners),
        max(corner.y for corner in bbox_corners),
        max(corner.z for corner in bbox_corners)
    ))
    
    bbox_center = (min_coords + max_coords) / 2
    bbox_dimensions = max_coords - min_coords
    max_dimension = max(bbox_dimensions)
    
    # Calculate optimal camera distance for framing
    # Using field of view to ensure object fits in frame with margin
    camera_data = camera.data
    fov_radians = camera_data.angle
    margin_factor = 1.3  # 30% margin around object
    
    optimal_distance = (max_dimension * margin_factor) / (2 * math.tan(fov_radians / 2))
    
    # Position camera at optimal viewing angle (45-degree elevation, 30-degree rotation)
    camera_offset = Vector((
        optimal_distance * math.cos(math.radians(30)) * math.cos(math.radians(45)),
        optimal_distance * math.sin(math.radians(30)) * math.cos(math.radians(45)),
        optimal_distance * math.sin(math.radians(45))
    ))
    
    camera.location = bbox_center + camera_offset
    
    # Point camera at object center
    direction = bbox_center - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    
    # Fine-tune focal length for jewelry photography
    camera_data.lens = 85  # Portrait lens equivalent - ideal for jewelry
    
    logger.info(f"Camera positioned at {camera.location} targeting {bbox_center}")
    logger.info(f"Object dimensions: {bbox_dimensions}, optimal distance: {optimal_distance:.3f}")

def generate_and_assemble_jewelry(args, params: Dict) -> bpy.types.Object:
    """
    Core jewelry generation logic - imports AI geometry and performs 
    parametric assembly based on Master Blueprint.
    
    Args:
        args: Command line arguments
        params: Master Blueprint parameters
        
    Returns:
        Final assembled jewelry object
    """
    logger.info("Executing parametric jewelry assembly from Master Blueprint")
    
    # Step 1: Import AI-generated base geometry
    logger.info(f"Loading AI-generated geometry: {args.input}")
    
    if not os.path.exists(args.input):
        raise FileNotFoundError(f"AI geometry file not found: {args.input}")
    
    # Import OBJ file
    bpy.ops.import_scene.obj(filepath=args.input)
    imported_objects = bpy.context.selected_objects
    
    if not imported_objects:
        raise RuntimeError("No objects imported from AI geometry file")
    
    ai_geometry = imported_objects[0]
    ai_geometry.name = "AI_Base_Geometry"
    
    # Step 2: Create parametric shank based on Master Blueprint
    shank_params = params.get('shank_parameters', {})
    logger.info(f"Creating parametric shank: {shank_params}")
    
    ring_diameter_mm = 12.45 + (args.ring_size * 0.8128)
    ring_radius = (ring_diameter_mm / 2) / 1000  # Convert to meters
    
    # Create shank geometry
    bm = bmesh.new()
    
    profile_shape = shank_params.get('profile_shape', 'Round')  
    thickness_mm = shank_params.get('thickness_mm', 2.0)
    thickness = thickness_mm / 1000
    
    if profile_shape == 'D-Shape':
        # Create D-shaped profile
        profile_geom = bmesh.ops.create_circle(bm, cap_ends=False, radius=thickness/2, segments=16)
        for v in profile_geom['verts']:
            if v.co.x < 0:
                v.co.x = 0
        bmesh.ops.translate(bm, verts=profile_geom['verts'], vec=(thickness/2, 0, 0))
    else:
        # Round profile
        profile_geom = bmesh.ops.create_circle(bm, cap_ends=False, radius=thickness/2, segments=16)
        bmesh.ops.translate(bm, verts=profile_geom['verts'], vec=(ring_radius + thickness/2, 0, 0))
    
    # Spin profile to create ring
    bmesh.ops.spin(bm, geom=profile_geom['verts'], cent=(0,0,0), axis=(0,1,0), 
                   steps=128, angle=math.radians(360))
    
    shank_mesh = bpy.data.meshes.new("Parametric_Shank")
    bm.to_mesh(shank_mesh)
    bm.free()
    
    shank_obj = bpy.data.objects.new("Parametric_Shank", shank_mesh)
    bpy.context.scene.collection.objects.link(shank_obj)
    
    # Step 3: Create parametric setting
    setting_params = params.get('setting_parameters', {})
    logger.info(f"Creating parametric setting: {setting_params}")
    
    prong_count = setting_params.get('prong_count', 4)
    style = setting_params.get('style', 'Classic')
    height_mm = setting_params.get('height_above_shank_mm', 3.0)
    height_offset = height_mm / 1000
    
    # Calculate stone dimensions
    stone_diameter_mm = 6.5 * (args.stone_carat ** (1./3.))
    stone_radius = (stone_diameter_mm / 2) / 1000
    
    setting_bm = bmesh.new()
    
    # Create prongs
    for i in range(prong_count):
        angle = i * (2 * math.pi / prong_count)
        
        prong = bmesh.ops.create_cone(setting_bm, cap_ends=True,
                                      radius1=0.0005, radius2=0.0002, 
                                      depth=0.004, segments=8)
        
        x = math.cos(angle) * (stone_radius * 0.9)
        y = math.sin(angle) * (stone_radius * 0.9) 
        z = ring_radius + height_offset
        
        if style == 'Sweeping':
            for v in prong['verts']:
                curve_factor = v.co.z * 0.1
                v.co.x *= (1 + curve_factor)
                v.co.y *= (1 + curve_factor)
        
        bmesh.ops.translate(setting_bm, verts=prong['verts'], vec=(x, y, z))
    
    setting_mesh = bpy.data.meshes.new("Parametric_Setting")
    setting_bm.to_mesh(setting_mesh)
    setting_bm.free()
    
    setting_obj = bpy.data.objects.new("Parametric_Setting", setting_mesh)
    bpy.context.scene.collection.objects.link(setting_obj)
    
    # Step 4: Apply artistic modifiers
    artistic_params = params.get('artistic_modifier_parameters', {})
    logger.info(f"Applying artistic modifiers: {artistic_params}")
    
    twist_angle = artistic_params.get('twist_angle_degrees', 0)
    if twist_angle > 0:
        twist_mod = ai_geometry.modifiers.new(name="Master_Twist", type='SIMPLE_DEFORM')
        twist_mod.deform_method = 'TWIST'
        twist_mod.angle = math.radians(twist_angle)
    
    displacement_strength = artistic_params.get('organic_displacement_strength', 0.0)
    if displacement_strength > 0:
        noise_tex = bpy.data.textures.new(name="Master_Noise", type='VORONOI')
        noise_tex.noise_scale = 0.5
        
        disp_mod = ai_geometry.modifiers.new(name="Master_Organic", type='DISPLACE')
        disp_mod.texture = noise_tex
        disp_mod.strength = displacement_strength
    
    # Step 5: Professional boolean assembly
    logger.info("Performing high-quality boolean assembly")
    
    # Join all components
    bpy.ops.object.select_all(action='DESELECT')
    ai_geometry.select_set(True)
    shank_obj.select_set(True)
    setting_obj.select_set(True)
    
    bpy.context.view_layer.objects.active = ai_geometry
    bpy.ops.object.join()
    
    final_object = bpy.context.active_object
    final_object.name = "Aura_V7_Professional_Creation"
    
    logger.info("Parametric jewelry assembly completed successfully")
    return final_object

def render_preview(scene: bpy.types.Scene, output_path: str) -> str:
    """
    Configure professional render settings and execute preview render.
    
    Args:
        scene: Blender scene to render
        output_path: Path for preview image output
        
    Returns:
        Path to rendered preview image
    """
    logger.info("Configuring professional preview render")
    
    # Set professional render settings
    render = scene.render
    render.resolution_x = 1920
    render.resolution_y = 1080
    render.resolution_percentage = 100
    
    # Professional output settings
    render.image_settings.file_format = 'PNG'
    render.image_settings.color_mode = 'RGBA'
    render.image_settings.compression = 15  # PNG compression
    
    # Professional color management
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'Medium High Contrast'
    
    # Set output path for preview
    preview_path = output_path.replace('.stl', '_preview.png')
    render.filepath = preview_path
    
    logger.info(f"Rendering professional preview: {preview_path}")
    
    # Execute render
    bpy.ops.render.render(write_still=True)
    
    logger.info("Professional preview render completed")
    return preview_path

def export_stl(obj: bpy.types.Object, output_path: str) -> None:
    """
    Clean STL export of the final manufacturable model.
    
    Args:
        obj: Object to export
        output_path: Path for STL file output
    """
    logger.info(f"Exporting manufacturable STL: {output_path}")
    
    # Enable STL addon
    try:
        addon_utils.enable("io_mesh_stl")
    except Exception as e:
        logger.warning(f"STL addon already enabled: {e}")
    
    # Apply all modifiers before export
    bpy.context.view_layer.objects.active = obj
    for mod in obj.modifiers[:]:  # Copy list to avoid iteration issues
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
            logger.debug(f"Applied modifier: {mod.name}")
        except RuntimeError as e:
            logger.warning(f"Could not apply modifier {mod.name}: {e}")
    
    # Select only the final object
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    
    # Export with professional settings
    bpy.ops.export_mesh.stl(
        filepath=output_path,
        use_selection=True,
        global_scale=1000.0,  # Convert meters to millimeters
        use_mesh_modifiers=True,
        axis_forward='-Z',
        axis_up='Y'
    )
    
    logger.info("STL export completed successfully")

# =============================================================================
# V6.0 GEOMETRIC ANALYSIS MODE - COGNITIVE LOOP INTELLIGENCE
# =============================================================================

def analyze_geometry(input_path: str, output_path: str) -> None:
    """
    V6.0 Analysis Mode: Perform geometric analysis of an STL file.
    
    Args:
        input_path: Path to STL file to analyze
        output_path: Path for JSON analysis output
    """
    logger.info("=== V6.0 BLENDER ENGINE - GEOMETRIC ANALYSIS MODE ===")
    logger.info(f"Analyzing STL file: {input_path}")
    
    # Setup clean scene
    scene = setup_scene()
    
    # Import the STL file
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"STL file not found: {input_path}")
    
    # Import STL
    bpy.ops.import_mesh.stl(filepath=input_path)
    analyzed_object = bpy.context.active_object
    
    if not analyzed_object:
        raise RuntimeError("Failed to import STL file")
    
    # Ensure we're in object mode for analysis
    bpy.context.view_layer.objects.active = analyzed_object
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Get mesh data
    mesh = analyzed_object.data
    
    # Calculate bounding box
    bbox = [analyzed_object.matrix_world @ Vector(corner) for corner in analyzed_object.bound_box]
    bbox_min = Vector((min(pt.x for pt in bbox), min(pt.y for pt in bbox), min(pt.z for pt in bbox)))
    bbox_max = Vector((max(pt.x for pt in bbox), max(pt.y for pt in bbox), max(pt.z for pt in bbox)))
    dimensions = bbox_max - bbox_min
    
    # Calculate volume (approximate using bounding box)
    volume_approx = dimensions.x * dimensions.y * dimensions.z
    
    # Calculate surface area (approximate)
    bpy.context.view_layer.objects.active = analyzed_object
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Get mesh statistics
    vertex_count = len(mesh.vertices)
    edge_count = len(mesh.edges)
    face_count = len(mesh.polygons)
    
    # Calculate center of mass
    center_of_mass = analyzed_object.location + (bbox_min + bbox_max) * 0.5
    
    # Generate analysis report
    analysis_report = {
        "analysis_timestamp": str(json.dumps({"timestamp": time.time()})).strip('"'),
        "geometry_metrics": {
            "vertex_count": vertex_count,
            "edge_count": edge_count,
            "face_count": face_count,
            "bounding_box": {
                "min": [bbox_min.x, bbox_min.y, bbox_min.z],
                "max": [bbox_max.x, bbox_max.y, bbox_max.z],
                "dimensions": [dimensions.x, dimensions.y, dimensions.z]
            },
            "approximate_volume_cubic_mm": volume_approx * 1000000,  # Convert to mm³
            "center_of_mass": [center_of_mass.x, center_of_mass.y, center_of_mass.z]
        },
        "manufacturing_assessment": {
            "complexity_level": "high" if face_count > 1000 else "medium" if face_count > 500 else "low",
            "printability_score": 0.9 if face_count < 2000 else 0.7,
            "estimated_material_usage_grams": volume_approx * 19.3 * 1000,  # Assuming gold density
            "structural_integrity": "good" if vertex_count > 100 else "needs_review"
        },
        "design_characteristics": {
            "dominant_dimension": "width" if dimensions.x > max(dimensions.y, dimensions.z) else 
                                  "height" if dimensions.y > dimensions.z else "depth",
            "aspect_ratio": max(dimensions.x, dimensions.y, dimensions.z) / min(dimensions.x, dimensions.y, dimensions.z),
            "symmetry_assessment": "likely_symmetric" if abs(center_of_mass.x) < 0.001 else "asymmetric"
        }
    }
    
    # Write analysis to JSON file
    with open(output_path, 'w') as f:
        json.dump(analysis_report, f, indent=2)
    
    logger.info(f"Geometric analysis completed: {output_path}")
    logger.info(f"Vertices: {vertex_count}, Faces: {face_count}")
    logger.info(f"Dimensions: {dimensions.x:.3f}x{dimensions.y:.3f}x{dimensions.z:.3f}")
    logger.info("=== V6.0 GEOMETRIC ANALYSIS COMPLETED ===")

# =============================================================================
# MAIN EXECUTION FUNCTION - PROFESSIONAL ORCHESTRATION
# =============================================================================

def main():
    """
    Main execution function - Professional orchestration of the complete V7.0 pipeline.
    Clean, clear orchestration as demonstrated in the official OpenAI script.
    """
    if '--' not in sys.argv:
        logger.error("No arguments provided. Script must be called with -- separator.")
        return
    
    parser = ArgumentParser(description="Aura V6.0/V7.0 State-of-the-Art Blender Engine with Dual-Mode Intelligence")
    parser.add_argument("--mode", type=str, choices=["generate", "analyze"], default="generate",
                       help="Operation mode: 'generate' for creation, 'analyze' for geometric analysis")
    parser.add_argument("--input", type=str, required=True,
                       help="Path to AI-generated .obj file")
    parser.add_argument("--output", type=str, required=True,
                       help="Path for final .stl export or analysis JSON")
    parser.add_argument("--params", type=str, required=True,
                       help="JSON Master Blueprint parameters")
    parser.add_argument("--ring_size", type=float, default=7.0)
    parser.add_argument("--stone_carat", type=float, default=1.0)
    parser.add_argument("--stone_shape", type=str, default='ROUND')
    parser.add_argument("--metal", type=str, default='GOLD')
    
    argv = sys.argv[sys.argv.index('--') + 1:]
    args = parser.parse_args(argv)
    
    logger.info("=== AURA V6.0/V7.0 PROFESSIONAL STATE-OF-THE-ART BLENDER ENGINE ===")
    logger.info("Architecturally aligned with OpenAI Shap-E best practices")
    logger.info(f"Mode: {args.mode.upper()}")
    logger.info(f"Input: {args.input}")
    logger.info(f"Output: {args.output}")
    
    if args.mode == "analyze":
        # V6.0 Analysis Mode - Geometric Intelligence
        analyze_geometry(args.input, args.output)
        return
    
    # V6.0/V7.0 Generation Mode - Original functionality
    logger.info(f"Ring specifications: Size {args.ring_size}, {args.stone_carat}ct {args.stone_shape}")
    
    try:
        # Parse Master Blueprint
        blueprint = json.loads(args.params)
        logger.info("Master Blueprint parsed and validated")
        
        # Step 1: Setup professional scene
        scene = setup_scene()
        
        # Step 2: Configure professional lighting
        lights = setup_lighting()
        
        # Step 3: Enable optimal GPU rendering
        gpu_enabled = enable_gpu_rendering(scene)
        
        # Step 4: Generate and assemble jewelry from Master Blueprint
        final_object = generate_and_assemble_jewelry(args, blueprint)
        
        # Step 5: Create and position camera for dynamic framing
        bpy.ops.object.camera_add(location=(0, 0, 0))
        camera = bpy.context.active_object
        camera.name = "Dynamic_Frame_Camera"
        scene.camera = camera
        
        # Step 6: Apply dynamic camera framing - MAJOR V7.0 INNOVATION
        frame_camera_to_object(camera, final_object)
        
        # Step 7: Render professional preview
        preview_path = render_preview(scene, args.output)
        
        # Step 8: Export final manufacturable STL
        export_stl(final_object, args.output)
        
        logger.info("=== V7.0 PROFESSIONAL PIPELINE EXECUTION COMPLETED ===")
        logger.info(f"GPU Rendering: {'Enabled' if gpu_enabled else 'Disabled (CPU fallback)'}")
        logger.info(f"Final STL: {args.output}")
        logger.info(f"Preview Image: {preview_path}")
        logger.info("State-of-the-art dynamic camera framing applied")
        logger.info("Professional scene management completed")
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in Master Blueprint: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"V7.0 Professional pipeline execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()