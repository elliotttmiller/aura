import bpy

def create_object_in_scene(mesh_data: dict, name: str, context):
    """Takes vertex and face data and creates a new object in the scene."""
    # ... (code is the same as previous versions) ...
    verts = mesh_data.get("vertices", [])
    faces = mesh_data.get("faces", [])
    if not verts or not faces: return None
    mesh = bpy.data.meshes.new(name=name)
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return obj

def join_objects(base_obj, detail_obj, context):
    """Joins the detail object to the base object using a boolean modifier."""
    if not base_obj or not detail_obj: return

    print(f"Backend: Joining '{detail_obj.name}' to '{base_obj.name}'")
    
    # Ensure the base object is active and selected
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = base_obj
    base_obj.select_set(True)

    # Create a boolean modifier
    bool_mod = base_obj.modifiers.new(name="AIBoolean", type='BOOLEAN')
    bool_mod.object = detail_obj
    bool_mod.operation = 'UNION'
    
    # Apply the modifier and delete the detail object
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    bpy.data.objects.remove(detail_obj, do_unlink=True)
