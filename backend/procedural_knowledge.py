"""
Aura V14.0 Sentient Artisan Environment - Procedural Knowledge Base
================================================================

Professional jewelry techniques implemented as discrete Python functions.
Contains master-level knowledge for creating specific, complex jewelry components.

Implements Protocol 3: Cognitive Authority - Deep domain knowledge integration.
"""

import bpy
import bmesh
import mathutils
from mathutils import Vector, Matrix
import math
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def execute_technique(base_object: bpy.types.Object, technique: str, parameters: Dict[str, Any], 
                     artistic_modifiers: Dict[str, Any]) -> bpy.types.Object:
    """
    Master dispatcher for executing professional jewelry techniques.
    
    Args:
        base_object: The base ring object to modify
        technique: The technique name ('Pave', 'Bezel', 'Tension', 'ClassicProng')
        parameters: Technique-specific parameters
        artistic_modifiers: Global artistic modifications
        
    Returns:
        Modified object with applied technique
    """
    logger.info(f"Executing technique: {technique}")
    
    # Ensure we're in edit mode for modifications
    bpy.context.view_layer.objects.active = base_object
    bpy.ops.object.mode_set(mode='EDIT')
    
    try:
        if technique == "Pave":
            result = create_pave_setting(base_object, parameters)
        elif technique == "Bezel":
            result = create_bezel_setting(base_object, parameters)
        elif technique == "Tension":
            result = create_tension_setting(base_object, parameters)
        elif technique == "ClassicProng":
            result = create_classic_prong_setting(base_object, parameters)
        else:
            logger.warning(f"Unknown technique: {technique}, using ClassicProng")
            result = create_classic_prong_setting(base_object, {"prong_count": 4, "prong_thickness_mm": 0.8})
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Apply artistic modifiers
        result = apply_artistic_modifiers(result, artistic_modifiers)
        
        logger.info(f"Technique {technique} executed successfully")
        return result
        
    except Exception as e:
        # Ensure we return to object mode even if there's an error
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass
        logger.error(f"Error executing technique {technique}: {e}")
        raise


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
        twist_modifier = obj.modifiers.new(name="AuraTwist", type='SIMPLE_DEFORM')
        twist_modifier.deform_method = 'TWIST'
        twist_modifier.angle = math.radians(twist_angle)
        twist_modifier.deform_axis = 'Z'
        
        logger.info(f"Applied twist modifier: {twist_angle} degrees")
    
    # Apply organic displacement
    displacement_strength = modifiers.get('organic_displacement_strength', 0.0)
    if displacement_strength > 0:
        # Add displacement modifier with noise texture
        displacement_modifier = obj.modifiers.new(name="AuraDisplacement", type='DISPLACE')
        displacement_modifier.strength = displacement_strength
        
        # Create noise texture for organic displacement
        texture = bpy.data.textures.new(name="AuraOrganicNoise", type='NOISE')
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
    stone_object.name = f"AuraStone_{stone_shape}"
    
    # Apply transparent material
    apply_stone_material(stone_object)
    
    return stone_object


def apply_stone_material(stone_obj: bpy.types.Object):
    """Apply a basic transparent material to represent a gemstone."""
    
    material_name = "AuraStone_Material"
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