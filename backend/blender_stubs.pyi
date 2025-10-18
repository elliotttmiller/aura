"""
Type stubs for Blender Python API (bpy)
This file tells Pylance that these modules exist, even though they're not installed.
These modules only exist inside Blender's Python environment.
"""

# Stub declarations for Blender modules
# These suppress "module not found" warnings in VSCode

class bpy:
    """Blender Python API stub"""
    class ops:
        class mesh:
            @staticmethod
            def primitive_torus_add(**kwargs): ...
            @staticmethod
            def primitive_cylinder_add(**kwargs): ...
            @staticmethod
            def primitive_cube_add(**kwargs): ...
            @staticmethod
            def primitive_uv_sphere_add(**kwargs): ...
            @staticmethod
            def primitive_ico_sphere_add(**kwargs): ...
        
        class object:
            @staticmethod
            def select_all(**kwargs): ...
            @staticmethod
            def delete(**kwargs): ...
            @staticmethod
            def light_add(**kwargs): ...
            @staticmethod
            def camera_add(**kwargs): ...
        
        class export_scene:
            @staticmethod
            def gltf(**kwargs): ...
        
        class wm:
            @staticmethod
            def save_as_mainfile(**kwargs): ...
    
    class data:
        objects: list
        materials: list
    
    class context:
        object: any
        scene: any

class bmesh:
    """BMesh module stub"""
    pass

class mathutils:
    """Mathutils module stub"""
    class Vector:
        def __init__(self, *args): ...

class addon_utils:
    """Addon utilities stub"""
    pass

class bpy_extras:
    """BPY extras stub"""
    class io_utils:
        pass
