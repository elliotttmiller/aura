import bpy

def import_model(filepath: str):
    """Imports a model from OBJ or STL format."""
    print(f"Backend: Importing from {filepath}")
    if filepath.lower().endswith('.obj'):
        bpy.ops.import_scene.obj(filepath=filepath)
    elif filepath.lower().endswith('.stl'):
        bpy.ops.import_mesh.stl(filepath=filepath)
    else:
        print(f"Unsupported import format for: {filepath}")

def export_model(filepath: str, context, export_format: str):
    """Exports the selected object to OBJ or STL format."""
    print(f"Backend: Exporting to {filepath}")
    if export_format == 'STL':
        bpy.ops.export_mesh.stl(filepath=filepath, use_selection=True)
    elif export_format == 'OBJ':
        bpy.ops.export_scene.obj(filepath=filepath, use_selection=True)
    else:
        print(f"Unsupported export format: {export_format}")
