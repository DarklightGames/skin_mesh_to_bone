if 'bpy' in locals():
    import importlib
    importlib.reload(operators)
else:
    from . import operators

import bpy

classes = (
    *operators.classes,
)

def menu_func(self, context):
    self.layout.operator(operators.SMTB_OT_skin_mesh_to_bone.bl_idname)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == '__main__':
    register()
