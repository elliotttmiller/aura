"""
AI Construction Plan Executor - Blender Integration
===================================================

This module executes AI-generated construction plans using Blender to create
actual 3D geometry from the AI's instructions.

It translates the high-level construction plan from the Enhanced AI Orchestrator
into concrete Blender operations (modeling, modifiers, materials, etc.)
"""

import os
import sys
import json
import subprocess
import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class BlenderConstructionExecutor:
    """
    Executes AI-generated construction plans using Blender.
    
    Takes the construction_plan from Enhanced AI Orchestrator and translates
    it into actual Blender Python commands to build real 3D geometry.
    """
    
    def __init__(self, blender_path: Optional[str] = None):
        """
        Initialize the Blender Construction Executor.
        
        Args:
            blender_path: Path to Blender executable (auto-detect if None)
        """
        self.blender_path = blender_path or self._find_blender()
        self.output_dir = Path(__file__).parent.parent / "output" / "ai_generated"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Blender path: {self.blender_path}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def _find_blender(self) -> str:
        """Auto-detect Blender installation."""
        # Common Blender paths on Windows
        possible_paths = [
            r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"✓ Found Blender at: {path}")
                return path
        
        logger.warning("⚠ Blender not found in standard locations")
        return "blender"  # Hope it's in PATH
    
    def execute_construction_plan(
        self,
        construction_plan: List[Dict[str, Any]],
        material_specs: Dict[str, Any],
        presentation_plan: Dict[str, Any],
        user_prompt: str,
        output_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute the AI construction plan to create actual 3D geometry.
        
        Args:
            construction_plan: List of construction steps from AI
            material_specs: Material specifications from AI
            presentation_plan: Lighting/camera setup from AI
            user_prompt: Original user prompt for naming
            output_name: Optional output filename
            
        Returns:
            Execution results with file paths and metadata
        """
        logger.info("🔨 Executing AI construction plan with Blender...")
        
        # Generate output filename
        if not output_name:
            safe_name = "".join(c if c.isalnum() or c == " " else "_" for c in user_prompt)
            safe_name = "_".join(safe_name.split())[:40]
            # Always use the time module, never a variable
            output_name = f"ai_{safe_name}_{int(__import__('time').time())}"
        
        output_blend = self.output_dir / f"{output_name}.blend"
        output_glb = self.output_dir / f"{output_name}.glb"
        output_render = self.output_dir / f"{output_name}_render.png"
        
        # Create Blender Python script to execute the plan
        script_content = self._generate_blender_script(
            construction_plan,
            material_specs,
            presentation_plan,
            output_blend.as_posix(),
            output_glb.as_posix(),
            output_render.as_posix()
        )
        
        # Save temporary script
        script_path = self.output_dir / f"temp_script_{int(__import__('time').time())}.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        try:
            # Execute Blender in background mode
            cmd = [
                self.blender_path,
                "--background",
                "--python", str(script_path)
            ]
            
            logger.info(f"Running Blender: {' '.join(cmd)}")
            
            start_time = time.time()
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                logger.info(f"✅ Blender execution successful ({execution_time:.2f}s)")
                
                return {
                    "success": True,
                    "blend_file": output_blend.as_posix(),
                    "glb_file": output_glb.as_posix() if output_glb.exists() else None,
                    "render_file": output_render.as_posix() if output_render.exists() else None,
                    "execution_time": execution_time,
                    "steps_executed": len(construction_plan),
                    "stdout": result.stdout,
                    "model_url": f"/output/ai_generated/{output_glb.name}" if output_glb.exists() else None
                }
            else:
                logger.error(f"❌ Blender execution failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "stdout": result.stdout,
                    "execution_time": execution_time
                }
        
        except subprocess.TimeoutExpired:
            logger.error("❌ Blender execution timed out (>300s)")
            return {
                "success": False,
                "error": "Execution timeout"
            }
        except Exception as e:
            logger.exception("❌ Blender execution exception")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            # Clean up temporary script
            if script_path.exists():
                script_path.unlink()
    
    def _generate_blender_script(
        self,
        construction_plan: List[Dict[str, Any]],
        material_specs: Dict[str, Any],
        presentation_plan: Dict[str, Any],
        output_blend: str,
        output_glb: str,
        output_render: str
    ) -> str:
        """
        Generate Blender Python script from AI construction plan.
        
        This translates high-level operations into concrete Blender commands.
        """
        script = f'''
import bpy
import bmesh
import math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Remove default objects
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj)

print("🔨 Starting AI construction plan execution...")

# Helper functions
def create_material(name, base_color, metallic, roughness, ior=1.45, transmission=0.0):
    """Create a PBR material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Create shader nodes
    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    # Set material properties
    bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['IOR'].default_value = ior
    if 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = transmission
    
    # Connect nodes
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

# Execute construction plan steps
'''
        
        # Add construction steps
        for i, step in enumerate(construction_plan, 1):
            operation = step.get('operation', '')
            params = step.get('parameters', {})
            description = step.get('description', '')
            
            script += f'\nprint("Step {i}: {operation} - {description}")\n'
            script += self._translate_operation(operation, params, i)
        
        # Add materials
        primary_material = material_specs.get('primary_material', {})
        if primary_material:
            script += f'''
# Apply primary material
print("💎 Applying primary material: {primary_material.get('name', 'Material')}")
base_color = hex_to_rgb("{primary_material.get('base_color', '#FFD700')}")
primary_mat = create_material(
    "{primary_material.get('name', 'Primary')}",
    base_color,
    {primary_material.get('metallic', 0.8)},
    {primary_material.get('roughness', 0.2)},
    {primary_material.get('ior', 1.45)},
    {primary_material.get('transmission', 0.0)}
)

# Apply material to all objects
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        if not obj.data.materials:
            obj.data.materials.append(primary_mat)
        else:
            obj.data.materials[0] = primary_mat
'''
        
        # Add lighting and camera from presentation plan
        # Ensure presentation_plan is a dict before using .get()
        if isinstance(presentation_plan, dict):
            lighting = presentation_plan.get('lighting', {})
            camera = presentation_plan.get('camera_angle', {})
        else:
            lighting = {}
            camera = {}
        
        script += f'''
# Setup lighting
print("💡 Setting up lighting...")
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.object
sun.data.energy = {lighting.get('intensity', 1.0) if lighting else 1.0}

# Add fill light
bpy.ops.object.light_add(type='AREA', location=(-5, 5, 5))
fill = bpy.context.object
fill.data.energy = 0.5

# Setup camera
print("📷 Setting up camera...")
bpy.ops.object.camera_add(location=(0, -10, 5))
camera = bpy.context.object
camera.rotation_euler = (math.radians(60), 0, 0)
bpy.context.scene.camera = camera

# Set render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.filepath = "{output_render}"

# Save blend file
print("💾 Saving .blend file...")
bpy.ops.wm.save_as_mainfile(filepath="{output_blend}")

# Export GLB
print("📦 Exporting GLB...")
bpy.ops.export_scene.gltf(
    filepath="{output_glb}",
    export_format='GLB',
    export_materials='EXPORT',
    export_colors=True
)

print("✅ Construction plan executed successfully!")
print(f"   Output .blend: {output_blend}")
print(f"   Output .glb: {output_glb}")
'''
        
        # Format the script with actual file paths
        script = script.format(
            output_blend=output_blend,
            output_glb=output_glb,
            output_render=output_render
        )
        
        return script
    
    def _translate_operation(self, operation: str, params: Dict[str, Any], step_num: int) -> str:
        """
        Translate AI operation into Blender Python code.
        
        Maps high-level operations (create_shank, create_diamond, etc.)
        to concrete Blender modeling commands.
        """
        op_lower = operation.lower()
        
        # Ring band/shank creation
        if 'shank' in op_lower or 'band' in op_lower:
            diameter = params.get('diameter_mm', 18.0) / 1000.0  # Convert mm to meters
            thickness = params.get('thickness_mm', 2.0) / 1000.0
            
            return f'''
# Create ring shank
bpy.ops.mesh.primitive_torus_add(
    major_radius={diameter/2},
    minor_radius={thickness/2},
    location=(0, 0, 0)
)
shank = bpy.context.object
shank.name = "Ring_Shank"
'''
        
        # Bezel setting
        elif 'bezel' in op_lower:
            height = params.get('bezel_height_mm', 3.0) / 1000.0
            diameter = params.get('feature_diameter_mm', 6.0) / 1000.0
            
            return f'''
# Create bezel setting
bpy.ops.mesh.primitive_cylinder_add(
    radius={diameter/2},
    depth={height},
    location=(0, 0, {height/2})
)
bezel = bpy.context.object
bezel.name = "Bezel_Setting"
'''
        
        # Diamond/gemstone
        elif 'diamond' in op_lower or 'gemstone' in op_lower:
            carat = params.get('carat_weight', 1.0)
            # Approximate diameter from carat weight (for round diamond)
            diameter = (carat ** (1/3)) * 0.006  # Rough approximation
            
            return f'''
# Create diamond
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=3,
    radius={diameter/2},
    location=(0, 0, 0.005)
)
diamond = bpy.context.object
diamond.name = "Diamond"
# Make it slightly elongated (diamond shape)
diamond.scale.z = 0.6
'''
        
        # Prong setting
        elif 'prong' in op_lower:
            count = params.get('prong_count', 4)
            height = params.get('prong_height_mm', 2.0) / 1000.0
            diameter = params.get('gemstone_diameter_mm', 6.0) / 1000.0
            
            prong_code = f'''
# Create prong settings
prong_radius = 0.0004  # 0.4mm prongs
prong_height = {height}
gem_radius = {diameter/2}

for i in range({count}):
    angle = (2 * math.pi * i) / {count}
    x = gem_radius * math.cos(angle)
    y = gem_radius * math.sin(angle)
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=prong_radius,
        depth=prong_height,
        location=(x, y, prong_height/2)
    )
    prong = bpy.context.object
    prong.name = f"Prong_{{i+1}}"
'''
            return prong_code
        
        # Primitive shapes
        elif 'primitive' in op_lower:
            prim_type = params.get('type', 'cube').lower()
            dims = params.get('dimensions', {})
            
            if prim_type == 'cylinder':
                radius = dims.get('radius_mm', 1.0) / 1000.0
                height = dims.get('height_mm', 2.0) / 1000.0
                return f'''
bpy.ops.mesh.primitive_cylinder_add(
    radius={radius},
    depth={height},
    location=(0, 0, {height/2})
)
obj = bpy.context.object
obj.name = "Primitive_Step_{step_num}"
'''
            elif prim_type == 'sphere':
                radius = dims.get('radius_mm', 1.0) / 1000.0
                return f'''
bpy.ops.mesh.primitive_uv_sphere_add(
    radius={radius},
    location=(0, 0, 0)
)
obj = bpy.context.object
obj.name = "Primitive_Step_{step_num}"
'''
            else:  # cube or default
                size = dims.get('size_mm', 2.0) / 1000.0
                return f'''
bpy.ops.mesh.primitive_cube_add(
    size={size},
    location=(0, 0, 0)
)
obj = bpy.context.object
obj.name = "Primitive_Step_{step_num}"
'''
        
        # Modifiers
        elif 'modifier' in op_lower:
            mod_type = params.get('type', '').lower()
            
            if mod_type == 'mirror':
                axis = params.get('parameters', {}).get('axis', 'x').upper()
                return f'''
# Apply mirror modifier
if bpy.context.object:
    mod = bpy.context.object.modifiers.new(name="Mirror", type='MIRROR')
    mod.use_axis[0] = {'X' in axis}
    mod.use_axis[1] = {'Y' in axis}
    mod.use_axis[2] = {'Z' in axis}
'''
            elif mod_type == 'array':
                count = params.get('parameters', {}).get('count', 3)
                return f'''
# Apply array modifier
if bpy.context.object:
    mod = bpy.context.object.modifiers.new(name="Array", type='ARRAY')
    mod.count = {count}
'''
            elif mod_type == 'subdivision':
                levels = params.get('parameters', {}).get('levels', 2)
                return f'''
# Apply subdivision modifier
if bpy.context.object:
    mod = bpy.context.object.modifiers.new(name="Subdivision", type='SUBSURF')
    mod.levels = {levels}
    mod.render_levels = {levels}
'''
        
        # Default: add a comment
        return f'# Operation: {operation} (parameters: {params})\n'


def create_executor(blender_path: Optional[str] = None) -> BlenderConstructionExecutor:
    """Factory function to create Blender executor."""
    return BlenderConstructionExecutor(blender_path)


if __name__ == "__main__":
    # Test the executor
    import time
    
    test_plan = [
        {
            "operation": "create_shank",
            "parameters": {"diameter_mm": 18.0, "thickness_mm": 2.0},
            "description": "Create ring band"
        },
        {
            "operation": "create_diamond",
            "parameters": {"carat_weight": 1.0},
            "description": "Add center diamond"
        }
    ]
    
    test_materials = {
        "primary_material": {
            "name": "Gold",
            "base_color": "#FFD700",
            "metallic": 1.0,
            "roughness": 0.2
        }
    }
    
    test_presentation = {
        "lighting": {"intensity": 1.2},
        "camera_angle": {"distance": "medium"}
    }
    
    executor = create_executor()
    result = executor.execute_construction_plan(
        test_plan,
        test_materials,
        test_presentation,
        "test diamond ring"
    )
    
    print(json.dumps(result, indent=2))
