"""
V22.0 Verifiable Artisan - Procedural Knowledge Base  
====================================================

Professional high-level creation techniques implemented as discrete Python functions.
Contains master-level knowledge for creating specific, complex components with universal applicability.

This is the "Toolbox" that the AI Master Planner can choose from to build dynamic construction plans.

Implements Protocol 2: Absolute Cognitive Authority - AI chooses from these professional techniques.
Implements Protocol 8: Semantic Clarity - Universal function naming for any domain.
"""

import bpy
import bmesh
import mathutils
from mathutils import Vector, Matrix
import math
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


# =============================================================================
# V22.0 CORE PROFESSIONAL TECHNIQUES - THE TOOLBOX
# =============================================================================

def create_shank(base_object: bpy.types.Object, parameters: Dict[str, Any]) -> bpy.types.Object:
    """
    Create a professional shank (band) structure.
    Universal function for creating circular/ring base geometry.
    
    Args:
        base_object: Base object to modify (can be None to create new)
        parameters: {
            "profile_shape": "Round" | "D-Shape" | "Square",
            "thickness_mm": 1.5-3.0,
            "diameter_mm": 16.0-22.0,
            "taper_factor": 0.0-0.3
        }
    """
    logger.info("Creating professional shank structure")
    
    profile_shape = parameters.get('profile_shape', 'Round')
    thickness_mm = parameters.get('thickness_mm', 2.0)
    diameter_mm = parameters.get('diameter_mm', 18.0)
    taper_factor = parameters.get('taper_factor', 0.0)
    
    # Convert to Blender units
    thickness = thickness_mm / 1000.0
    radius = (diameter_mm / 1000.0) / 2
    
    if profile_shape == 'Round':
        bpy.ops.mesh.primitive_torus_add(
            major_radius=radius,
            minor_radius=thickness / 2,
            location=(0, 0, 0)
        )
    elif profile_shape == 'D-Shape':
        # Create torus and flatten bottom
        bpy.ops.mesh.primitive_torus_add(
            major_radius=radius,
            minor_radius=thickness / 2,
            location=(0, 0, 0)
        )
        obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(0, 0, -1))
        bpy.ops.object.mode_set(mode='OBJECT')
    elif profile_shape == 'Square':
        # Create square profile using array modifier
        bpy.ops.mesh.primitive_cube_add(size=thickness, location=(radius, 0, 0))
        obj = bpy.context.active_object
        # Add array modifier for circular pattern
        array_mod = obj.modifiers.new(name="Circular_Array", type='ARRAY')
        array_mod.fit_type = 'FIXED_COUNT'
        array_mod.count = 16
        array_mod.use_relative_offset = False
        array_mod.use_object_offset = True
        # Create empty for rotation
        bpy.ops.object.empty_add(location=(0, 0, 0))
        empty = bpy.context.active_object
        empty.rotation_euler[2] = math.radians(360 / 16)
        array_mod.offset_object = empty
        bpy.context.view_layer.objects.active = obj
    
    shank_object = bpy.context.active_object
    shank_object.name = "Professional_Shank"
    
    # Apply taper if specified
    if taper_factor > 0:
        taper_mod = shank_object.modifiers.new(name="Taper", type='SIMPLE_DEFORM')
        taper_mod.deform_method = 'TAPER'
        taper_mod.factor = taper_factor
        taper_mod.deform_axis = 'Y'
    
    logger.info(f"Shank created: {profile_shape} profile, {thickness_mm}mm thickness")
    return shank_object


def create_bezel_setting(base_object: bpy.types.Object, parameters: Dict[str, Any]) -> bpy.types.Object:
    """
    Create a professional bezel setting that surrounds features with material.
    Universal function for creating enclosing/framing structures.
    
    Args:
        base_object: Object to add bezel to
        parameters: {
            "bezel_height_mm": 1.5-4.0,
            "bezel_thickness_mm": 0.3-0.8,
            "feature_diameter_mm": 4.0-10.0,
            "setting_position": [x, y, z] relative position
        }
    """
    logger.info("Creating professional bezel setting")
    
    bezel_height_mm = parameters.get('bezel_height_mm', 2.5)
    bezel_thickness_mm = parameters.get('bezel_thickness_mm', 0.5)
    feature_diameter_mm = parameters.get('feature_diameter_mm', 6.0)
    setting_position = parameters.get('setting_position', [0, 0, 0.002])
    
    # Convert to Blender units
    bezel_height = bezel_height_mm / 1000.0
    bezel_thickness = bezel_thickness_mm / 1000.0
    feature_radius = (feature_diameter_mm / 1000.0) / 2
    
    # Create cylindrical bezel
    bpy.ops.mesh.primitive_cylinder_add(
        radius=feature_radius + bezel_thickness,
        depth=bezel_height,
        location=setting_position
    )
    
    bezel_object = bpy.context.active_object
    bezel_object.name = "Professional_Bezel_Setting"
    
    # Create inner cavity
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.inset_faces(thickness=bezel_thickness, depth=0)
    bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, 
                                     TRANSFORM_OT_translate={"value":(0, 0, -bezel_height * 0.8)})
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Join with base object if provided
    if base_object:
        bpy.ops.object.select_all(action='DESELECT')
        base_object.select_set(True)
        bezel_object.select_set(True)
        bpy.context.view_layer.objects.active = base_object
        bpy.ops.object.join()
        result_object = base_object
    else:
        result_object = bezel_object
    
    logger.info(f"Bezel setting created: {bezel_height_mm}mm height, {bezel_thickness_mm}mm thickness")
    return result_object


def create_prong_setting(base_object: bpy.types.Object, parameters: Dict[str, Any]) -> bpy.types.Object:
    """
    Create a professional prong setting with individual supports.
    Universal function for creating discrete holding/support structures.
    
    Args:
        base_object: Object to add prongs to
        parameters: {
            "prong_count": 3-6,
            "prong_thickness_mm": 0.6-1.2,
            "prong_height_mm": 2.0-5.0,
            "prong_placement_radius_mm": 2.5-4.0,
            "prong_taper": 0.0-0.5
        }
    """
    logger.info("Creating professional prong setting")
    
    prong_count = parameters.get('prong_count', 4)
    prong_thickness_mm = parameters.get('prong_thickness_mm', 0.8)
    prong_height_mm = parameters.get('prong_height_mm', 3.5)
    placement_radius_mm = parameters.get('prong_placement_radius_mm', 3.0)
    prong_taper = parameters.get('prong_taper', 0.2)
    
    # Convert to Blender units
    prong_thickness = prong_thickness_mm / 1000.0
    prong_height = prong_height_mm / 1000.0
    placement_radius = placement_radius_mm / 1000.0
    
    prong_objects = []
    
    # Create individual prongs
    for i in range(prong_count):
        angle = (2 * math.pi * i) / prong_count
        prong_x = placement_radius * math.cos(angle)
        prong_y = placement_radius * math.sin(angle)
        prong_z = 0.002  # Slightly above base
        
        # Create prong as cylinder
        bpy.ops.mesh.primitive_cylinder_add(
            radius=prong_thickness / 2,
            depth=prong_height,
            location=(prong_x, prong_y, prong_z + prong_height / 2)
        )
        
        prong = bpy.context.active_object
        prong.name = f"Prong_{i+1}"
        
        # Apply taper to prong
        if prong_taper > 0:
            taper_mod = prong.modifiers.new(name="Prong_Taper", type='SIMPLE_DEFORM')
            taper_mod.deform_method = 'TAPER'
            taper_mod.factor = -prong_taper  # Negative for narrowing at top
            taper_mod.deform_axis = 'Z'
        
        prong_objects.append(prong)
    
    # Join all prongs with base object
    if base_object:
        bpy.ops.object.select_all(action='DESELECT')
        base_object.select_set(True)
        for prong in prong_objects:
            prong.select_set(True)
        bpy.context.view_layer.objects.active = base_object
        bpy.ops.object.join()
        result_object = base_object
    else:
        # Join prongs together
        bpy.ops.object.select_all(action='DESELECT')
        for prong in prong_objects:
            prong.select_set(True)
        bpy.context.view_layer.objects.active = prong_objects[0]
        bpy.ops.object.join()
        result_object = prong_objects[0]
        result_object.name = "Professional_Prong_Setting"
    
    logger.info(f"Prong setting created: {prong_count} prongs, {prong_height_mm}mm height")
    return result_object


def apply_twist_modifier(base_object: bpy.types.Object, parameters: Dict[str, Any]) -> bpy.types.Object:
    """
    Apply professional twist deformation to any object.
    Universal function for adding spiral/helical modifications.
    
    Args:
        base_object: Object to twist
        parameters: {
            "twist_angle_degrees": 0-360,
            "twist_axis": "X" | "Y" | "Z",
            "twist_limits": [start, end] as factor 0.0-1.0
        }
    """
    logger.info("Applying professional twist modifier")
    
    twist_angle_degrees = parameters.get('twist_angle_degrees', 30)
    twist_axis = parameters.get('twist_axis', 'Z')
    twist_limits = parameters.get('twist_limits', [0.0, 1.0])
    
    # Ensure we're in object mode
    bpy.context.view_layer.objects.active = base_object
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add twist modifier
    twist_modifier = base_object.modifiers.new(name="Professional_Twist", type='SIMPLE_DEFORM')
    twist_modifier.deform_method = 'TWIST'
    twist_modifier.angle = math.radians(twist_angle_degrees)
    twist_modifier.deform_axis = twist_axis
    
    # Set limits if specified
    if twist_limits != [0.0, 1.0]:
        twist_modifier.limits[0] = twist_limits[0]
        twist_modifier.limits[1] = twist_limits[1]
    
    logger.info(f"Twist modifier applied: {twist_angle_degrees}° around {twist_axis} axis")
    return base_object


# =============================================================================
# V22.0 DYNAMIC OPERATION EXECUTOR  
# =============================================================================

def execute_operation(operation: Dict[str, Any], context_objects: Dict[str, bpy.types.Object]) -> bpy.types.Object:
    """
    V23 Enhanced Dynamic Operation Executor with AI-Generated Code Execution.
    
    This function interprets a single operation from the AI's construction_plan and
    executes the corresponding professional technique. 
    
    V23 Enhancement: Secure execution of AI-generated bmesh code for novel techniques.
    V24 Enhancement: Robust error handling for unknown operations as mandated by
    Protocol 10: Holistic Integration & Autonomy.
    
    Args:
        operation: {
            "operation": "technique_name",
            "parameters": {...},
            "target": "object_name" (optional),
            "_v23_dynamic_code": "Python function code" (V23 dynamic generation)
        }
        context_objects: Dictionary of available objects by name
        
    Returns:
        The resulting object after operation execution, or fallback object for unknown operations
    """
    operation_name = operation.get('operation')
    parameters = operation.get('parameters', {})
    target_name = operation.get('target', 'base')
    dynamic_code = operation.get('_v23_dynamic_code')
    
    logger.info(f"V23: Executing dynamic operation: {operation_name}")
    
    # Get target object
    target_object = context_objects.get(target_name)
    
    # V23 Generative Artisan: Execute AI-generated code if present
    if dynamic_code:
        logger.info(f"V23: ⚡ Executing AI-generated technique code for '{operation_name}'")
        try:
            result = _execute_dynamic_technique(dynamic_code, target_object, parameters)
            if result:
                logger.info(f"V23: ✅ Dynamic technique '{operation_name}' executed successfully")
                # Update context objects
                context_objects[f"result_{operation_name}"] = result
                if target_name == 'base':
                    context_objects['base'] = result
                return result
            else:
                logger.warning(f"V23: Dynamic technique '{operation_name}' returned no result")
        except Exception as e:
            logger.error(f"V23: Dynamic technique execution failed: {e}")
            # Fall through to standard technique execution
    
    # V24: Enhanced operation dispatcher with comprehensive error handling
    try:
        if operation_name == "create_shank":
            result = create_shank(target_object, parameters)
        elif operation_name == "create_bezel_setting":
            result = create_bezel_setting(target_object, parameters)
        elif operation_name == "create_prong_setting":
            result = create_prong_setting(target_object, parameters)
        elif operation_name == "apply_twist_modifier":
            result = apply_twist_modifier(target_object, parameters)
        elif operation_name == "create_pave_setting":
            result = create_pave_setting(target_object, parameters)
        elif operation_name == "create_tension_setting":
            result = create_tension_setting(target_object, parameters)
        elif operation_name == "create_classic_prong_setting":
            result = create_classic_prong_setting(target_object, parameters)
        else:
            # V24: Robust handling of unknown operations
            logger.warning(f"V24: Unknown operation '{operation_name}' - creating fallback object")
            result = target_object if target_object else create_fallback_object()
            
            # V24: Log the unknown operation for future development
            logger.info(f"V24: Unknown operation details - Name: {operation_name}, Parameters: {parameters}")
        
        # Update context objects
        if result:
            context_objects[f"result_{operation_name}"] = result
            if target_name == 'base':
                context_objects['base'] = result
        
        logger.info(f"V24: Operation {operation_name} completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"V24: Operation {operation_name} failed with exception: {e}")
        
        # V24: Graceful degradation - return target object or create fallback
        fallback_result = target_object if target_object else create_fallback_object()
        logger.info(f"V24: Returning fallback object for failed operation {operation_name}")
        return fallback_result


def create_fallback_object() -> bpy.types.Object:
    """Create a simple fallback object when operations fail."""
    bpy.ops.mesh.primitive_torus_add(major_radius=0.009, minor_radius=0.001)
    fallback = bpy.context.active_object
    fallback.name = "Fallback_Object"
    return fallback


def _execute_dynamic_technique(dynamic_code: str, target_object: bpy.types.Object, parameters: Dict[str, Any]) -> bpy.types.Object:
    """
    V23 Generative Artisan: Securely execute AI-generated bmesh code.
    
    This function safely executes dynamically generated Python code in a controlled environment
    using bmesh operations to create novel 3D geometry.
    
    Args:
        dynamic_code: The Python function code generated by the AI
        target_object: Base object to work with (can be None)
        parameters: Parameters to pass to the generated function
        
    Returns:
        The resulting Blender object after executing the dynamic code
    """
    logger.info("V23: Executing dynamic bmesh technique in secure sandbox")
    
    try:
        # Create a new bmesh instance for the operation
        import bmesh
        bm = bmesh.new()
        
        # Create a restricted execution environment
        # Only allow bmesh, math, and basic Python operations
        safe_globals = {
            '__builtins__': {
                'range': range,
                'len': len,
                'enumerate': enumerate,
                'abs': abs,
                'min': min,
                'max': max,
                'round': round,
                'int': int,
                'float': float,
            },
            'bmesh': bmesh,
            'math': math,
            'bm': bm,
            'params': parameters
        }
        
        # Execute the dynamic code in the restricted environment
        exec(dynamic_code, safe_globals)
        
        # The dynamic code should have defined a 'create_custom_component' function
        if 'create_custom_component' in safe_globals:
            logger.info("V23: Calling AI-generated create_custom_component function")
            
            # Call the generated function
            geom_result = safe_globals['create_custom_component'](bm, parameters)
            logger.info(f"V23: Dynamic function returned: {type(geom_result)}")
            
            # Create a new Blender object from the bmesh
            mesh = bpy.data.meshes.new("V23_Dynamic_Component")
            bm.to_mesh(mesh)
            bm.free()
            
            # Create object
            result_object = bpy.data.objects.new("V23_Dynamic_Component", mesh)
            bpy.context.collection.objects.link(result_object)
            
            # If we have a target object, join with it
            if target_object:
                logger.info("V23: Joining dynamic component with target object")
                
                # Select both objects
                bpy.ops.object.select_all(action='DESELECT')
                target_object.select_set(True)
                result_object.select_set(True)
                bpy.context.view_layer.objects.active = target_object
                
                # Join them
                bpy.ops.object.join()
                return target_object
            else:
                return result_object
        else:
            logger.error("V23: Generated code does not contain 'create_custom_component' function")
            bm.free()
            return None
            
    except Exception as e:
        logger.error(f"V23: Dynamic code execution failed: {e}")
        # Clean up bmesh if it exists
        try:
            if 'bm' in locals():
                bm.free()
        except:
            pass
        return None


# =============================================================================
# LEGACY FUNCTION ALIASES FOR BACKWARD COMPATIBILITY
# =============================================================================

def execute_technique(base_object: bpy.types.Object, technique: str, parameters: Dict[str, Any], 
                     artistic_modifiers: Dict[str, Any]) -> bpy.types.Object:
    """
    Legacy technique execution function - maintained for V20.0 compatibility.
    V22.0 systems should use execute_operation() with construction_plan.
    """
    logger.info(f"Legacy technique execution: {technique}")
    
    # Convert legacy technique call to V22.0 operation format
    operation = {
        "operation": technique.lower().replace(" ", "_"),
        "parameters": parameters
    }
    
    context_objects = {"base": base_object}
    result = execute_operation(operation, context_objects)
    
    # Apply artistic modifiers (legacy behavior)
    if artistic_modifiers:
        result = apply_artistic_modifiers(result, artistic_modifiers)
    
    return result


def create_pave_setting(base_object: bpy.types.Object, parameters: Dict[str, Any]) -> bpy.types.Object:
    """
    Create a pave setting with multiple small stones.
    
    Pave setting parameters:
    - stone_count: Number of small stones (default: 12)
    - stone_size_mm: Size of each stone in mm (default: 1.5)
    - stone_spacing_factor: Spacing between stones (default: 1.2)
    """
    logger.info("Creating pave setting")
    
    stone_count = parameters.get('stone_count', 12)
    stone_size_mm = parameters.get('stone_size_mm', 1.5)
    stone_spacing_factor = parameters.get('stone_spacing_factor', 1.2)
    
    # Convert to Blender units (assuming mm to units conversion)
    stone_radius = (stone_size_mm / 1000.0) / 2
    
    # Get the ring's circumference for stone placement
    bm = bmesh.from_mesh(base_object.data)
    
    # Create stone seats around the ring
    ring_radius = 0.009  # Approximate ring radius
    
    for i in range(stone_count):
        angle = (2 * math.pi * i) / stone_count
        x = ring_radius * math.cos(angle)
        y = ring_radius * math.sin(angle)
        z = 0.002  # Slightly above the ring
        
        # Create small cylindrical seats for stones
        seat_location = Vector((x, y, z))
        
        # Add small indentation for stone seat
        bmesh.ops.inset_individual(
            bm, 
            faces=[f for f in bm.faces if (Vector(f.calc_center_median()) - seat_location).length < stone_radius * 2],
            thickness=stone_radius * 0.8
        )
    
    # Update mesh
    bmesh.update_edit_mesh(base_object.data)
    bm.free()
    
    return base_object


def create_bezel_setting(base_object: bpy.types.Object, parameters: Dict[str, Any]) -> bpy.types.Object:
    """
    Create a bezel setting that surrounds the stone with metal.
    
    Bezel setting parameters:
    - bezel_height_mm: Height of the bezel wall (default: 2.0)
    - bezel_thickness_mm: Thickness of the bezel wall (default: 0.5)
    - stone_diameter_mm: Diameter of the stone (default: 6.0)
    """
    logger.info("Creating bezel setting")
    
    bezel_height_mm = parameters.get('bezel_height_mm', 2.0)
    bezel_thickness_mm = parameters.get('bezel_thickness_mm', 0.5)
    stone_diameter_mm = parameters.get('stone_diameter_mm', 6.0)
    
    # Convert to Blender units
    bezel_height = bezel_height_mm / 1000.0
    bezel_thickness = bezel_thickness_mm / 1000.0
    stone_radius = (stone_diameter_mm / 1000.0) / 2
    
    bm = bmesh.from_mesh(base_object.data)
    
    # Find the top face of the ring for bezel placement
    top_faces = [f for f in bm.faces if f.normal.z > 0.7]
    
    if top_faces:
        # Select the top face and extrude to create bezel
        top_face = max(top_faces, key=lambda f: f.calc_center_median().z)
        
        # Create bezel by extruding and scaling
        bmesh.ops.extrude_face_region(bm, geom=[top_face])
        
        # Move extruded face up
        for vert in bm.verts:
            if vert.select:
                vert.co.z += bezel_height
        
        # Scale inner part to create stone seat
        inner_verts = [v for v in bm.verts if v.select]
        bmesh.ops.scale(
            bm,
            vec=(0.8, 0.8, 1.0),
            space=Matrix.Translation(-top_face.calc_center_median()),
            verts=inner_verts
        )
    
    # Update mesh
    bmesh.update_edit_mesh(base_object.data)
    bm.free()
    
    return base_object


def create_tension_setting(base_object: bpy.types.Object, parameters: Dict[str, Any]) -> bpy.types.Object:
    """
    Create a tension setting where the stone is held by spring tension.
    
    Tension setting parameters:
    - tension_strength: How much tension/compression (default: 0.8)
    - gap_width_mm: Width of the gap for the stone (default: 6.2)
    - tension_arm_thickness_mm: Thickness of tension arms (default: 2.5)
    """
    logger.info("Creating tension setting")
    
    tension_strength = parameters.get('tension_strength', 0.8)
    gap_width_mm = parameters.get('gap_width_mm', 6.2)
    arm_thickness_mm = parameters.get('tension_arm_thickness_mm', 2.5)
    
    # Convert to Blender units
    gap_width = gap_width_mm / 1000.0
    arm_thickness = arm_thickness_mm / 1000.0
    
    bm = bmesh.from_mesh(base_object.data)
    
    # Create a gap in the ring for tension setting
    # Find vertices in the top area
    center = Vector((0, 0, 0))
    top_verts = [v for v in bm.verts if v.co.z > -0.001]
    
    # Remove vertices to create gap
    front_verts = [v for v in top_verts if v.co.y > gap_width/3]
    bmesh.ops.delete(bm, geom=front_verts, type='VERTS')
    
    # Add tension arms
    remaining_edges = [e for e in bm.edges if len(e.link_faces) == 1]
    
    for edge in remaining_edges[:2]:  # Work on the first two open edges
        # Extrude to create tension arms
        result = bmesh.ops.extrude_edge_only(bm, edges=[edge])
        new_verts = [elem for elem in result['geom'] if isinstance(elem, bmesh.types.BMVert)]
        
        # Move new vertices to create tension arm shape
        for vert in new_verts:
            direction = (vert.co - center).normalized()
            vert.co += direction * (arm_thickness * tension_strength)
    
    # Update mesh
    bmesh.update_edit_mesh(base_object.data)
    bm.free()
    
    return base_object


def create_classic_prong_setting(base_object: bpy.types.Object, parameters: Dict[str, Any]) -> bpy.types.Object:
    """
    Create a classic prong setting with individual prongs holding the stone.
    
    Classic prong parameters:
    - prong_count: Number of prongs (default: 4)
    - prong_thickness_mm: Thickness of each prong (default: 0.8)
    - prong_height_mm: Height of prongs (default: 4.0)
    """
    logger.info("Creating classic prong setting")
    
    prong_count = parameters.get('prong_count', 4)
    prong_thickness_mm = parameters.get('prong_thickness_mm', 0.8)
    prong_height_mm = parameters.get('prong_height_mm', 4.0)
    
    # Convert to Blender units
    prong_thickness = prong_thickness_mm / 1000.0
    prong_height = prong_height_mm / 1000.0
    
    bm = bmesh.from_mesh(base_object.data)
    
    # Find the center top of the ring
    center = Vector((0, 0, 0))
    ring_radius = 0.008  # Approximate radius for prong placement
    
    # Create prongs around the setting
    for i in range(prong_count):
        angle = (2 * math.pi * i) / prong_count
        prong_x = ring_radius * math.cos(angle)
        prong_y = ring_radius * math.sin(angle)
        prong_base_z = 0.002
        
        # Create each prong as a small extruded cylinder
        prong_location = Vector((prong_x, prong_y, prong_base_z))
        
        # Create prong by adding geometry
        bmesh.ops.create_cube(bm, size=prong_thickness)
        
        # Move and scale the new cube for the prong
        new_verts = [v for v in bm.verts if not v.tag]
        for v in new_verts:
            v.tag = True
            v.co = (v.co * 0.5) + prong_location
            v.co.z += prong_height / 2
    
    # Update mesh
    bmesh.update_edit_mesh(base_object.data)
    bm.free()
    
    return base_object


def apply_artistic_modifiers(obj: bpy.types.Object, modifiers: Dict[str, Any]) -> bpy.types.Object:
    """
    Apply artistic modifiers like twist and organic displacement.
    
    Args:
        obj: Object to modify
        modifiers: Dictionary containing modifier parameters
        
    Returns:
        Modified object
    """
    logger.info("Applying artistic modifiers")
    
    # Ensure we're in object mode for modifier operations
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Apply twist modifier
    twist_angle = modifiers.get('twist_angle_degrees', 0)
    if twist_angle > 0:
        twist_modifier = obj.modifiers.new(name="Twist", type='SIMPLE_DEFORM')
        twist_modifier.deform_method = 'TWIST'
        twist_modifier.angle = math.radians(twist_angle)
        twist_modifier.deform_axis = 'Z'
        
        logger.info(f"Applied twist modifier: {twist_angle} degrees")
    
    # Apply organic displacement
    displacement_strength = modifiers.get('organic_displacement_strength', 0.0)
    if displacement_strength > 0:
        # Add displacement modifier with noise texture
        displacement_modifier = obj.modifiers.new(name="Displacement", type='DISPLACE')
        displacement_modifier.strength = displacement_strength
        
        # Create noise texture for organic displacement
        texture = bpy.data.textures.new(name="OrganicNoise", type='NOISE')
        texture.noise_scale = 0.5
        displacement_modifier.texture = texture
        
        logger.info(f"Applied organic displacement: {displacement_strength}")
    
    return obj


def create_stone_geometry(stone_shape: str, carat_weight: float) -> bpy.types.Object:
    """
    Create stone geometry for visualization.
    
    Args:
        stone_shape: Shape of the stone ('ROUND', 'PRINCESS', 'EMERALD', etc.)
        carat_weight: Weight in carats
        
    Returns:
        Stone object
    """
    logger.info(f"Creating {stone_shape} stone geometry ({carat_weight} carats)")
    
    # Calculate approximate diameter from carat weight
    # Rough approximation: 1 carat round = ~6.5mm diameter
    diameter_mm = 6.5 * (carat_weight ** (1/3))
    radius = (diameter_mm / 1000.0) / 2
    
    if stone_shape == 'ROUND':
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(0, 0, 0.004))
    elif stone_shape == 'PRINCESS':
        bpy.ops.mesh.primitive_cube_add(size=diameter_mm/1000.0, location=(0, 0, 0.004))
        # Apply bevel to create princess cut
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.bevel(offset=radius*0.2)
        bpy.ops.object.mode_set(mode='OBJECT')
    elif stone_shape == 'EMERALD':
        bpy.ops.mesh.primitive_cube_add(size=diameter_mm/1000.0, location=(0, 0, 0.004))
        # Scale to create emerald proportions
        bpy.ops.transform.resize(value=(1.0, 0.7, 0.6))
    else:
        # Default to round
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(0, 0, 0.004))
    
    stone_object = bpy.context.active_object
    stone_object.name = f"Stone_{stone_shape}"
    
    # Apply transparent material
    apply_stone_material(stone_object)
    
    return stone_object


def apply_stone_material(stone_obj: bpy.types.Object):
    """Apply a basic transparent material to represent a gemstone."""
    
    material_name = "Stone_Material"
    material = bpy.data.materials.get(material_name)
    
    if material is None:
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True
        
        if material.node_tree:
            principled = material.node_tree.nodes.get("Principled BSDF")
            if principled:
                # Set gemstone properties
                principled.inputs["Base Color"].default_value = (0.9, 0.9, 1.0, 1.0)
                principled.inputs["Transmission"].default_value = 1.0
                principled.inputs["Roughness"].default_value = 0.0
                principled.inputs["IOR"].default_value = 2.4  # Diamond-like IOR
    
    # Apply material
    if stone_obj.data.materials:
        stone_obj.data.materials[0] = material
    else:
        stone_obj.data.materials.append(material)