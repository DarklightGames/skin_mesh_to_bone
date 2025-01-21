from bpy.props import EnumProperty, FloatProperty, BoolProperty
from bpy.types import Armature, Operator, Context, Event, Mesh, Object, Modifier
from typing import cast, Optional

def bone_items_cb(self, context: Context):
    armature_object = context.object
    armature_data: Armature = cast(Armature, armature_object.data)
    return [(bone.name, bone.name, '') for bone in sorted(armature_data.bones, key=lambda bone: bone.name)]


def find_armature_modifier(mesh_object: Object, armature_object: Object) -> Optional[Modifier]:
    for modifier in mesh_object.modifiers:
        if modifier.type == 'ARMATURE' and modifier.object == armature_object:
            return modifier
    return None


class SMTB_OT_skin_mesh_to_bone(Operator):
    bl_idname = 'smtb.skin_mesh_to_bone'
    bl_label = 'Skin Mesh to Bone'
    bl_description = 'Skin the selected meshes to a bone on the active armature'
    bl_options = {'REGISTER', 'UNDO'}

    bone: EnumProperty(name='Bone', items=bone_items_cb)
    weight: FloatProperty(name='Weight', default=1.0, min=0.0, max=1.0, subtype='FACTOR')
    should_mirror_vertex_groups: BoolProperty(name='Mirror Vertex Groups', default=True)
    clear_vertex_groups: BoolProperty(name='Clear Vertex Groups', default=False)

    @classmethod
    def poll(cls, context):
        # Return true if the active object is a mesh.
        if context.object is None:
            cls.poll_message_set('No active object')
            return False
        if context.object.type != 'ARMATURE':
            cls.poll_message_set('Active object is not an armature')
            return False
        return True

    def invoke(self, context: Context, event: Event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context: 'Context'):
        layout = self.layout
        flow = layout.grid_flow()
        flow.use_property_split = True
        flow.use_property_decorate = False
        flow.prop(self, 'bone')
        flow.prop(self, 'weight')
        flow.prop(self, 'clear_vertex_groups')
        flow.prop(self, 'should_mirror_vertex_groups')

    def execute(self, context):
        # For all selected objects:
        armature_object = context.object
        for bpy_object in filter(lambda x: x.type == 'MESH', context.selected_objects):

            if self.clear_vertex_groups:
                # Clear all vertex groups.
                for vertex_group in bpy_object.vertex_groups:
                    bpy_object.vertex_groups.remove(vertex_group)

            # Create a vertex group if it doesn't exist.
            vertex_group = bpy_object.vertex_groups.get(self.bone, None)
            if vertex_group is None:
                vertex_group = bpy_object.vertex_groups.new(name=self.bone)

            # Guess the mirror vertex group name.
            if self.should_mirror_vertex_groups:
                mirror_bone = self.bone
                import re
                re.sub(r'[._-]([LR])$', '', mirror_bone)
                if mirror_bone.endswith('L'):
                    mirror_bone = mirror_bone[:-1] + 'R'
                elif mirror_bone.endswith('R'):
                    mirror_bone = mirror_bone[:-1] + 'L'

                # Create the mirror vertex group if it doesn't exist.
                mirror_vertex_group = bpy_object.vertex_groups.get(mirror_bone, None)
                if mirror_vertex_group is None:
                    bpy_object.vertex_groups.new(name=mirror_bone)

            # Add all vertices to the vertex group.
            mesh_data = cast(Mesh, bpy_object.data)
            vertex_group.add(range(len(mesh_data.vertices)), self.weight, 'REPLACE')

            # Add an armature modifier if it doesn't exist.
            armature_modifier = find_armature_modifier(bpy_object, armature_object)
            if armature_modifier is None:
                armature_modifier = bpy_object.modifiers.new(name='Armature', type='ARMATURE')
                armature_modifier.object = armature_object
        return {'FINISHED'}


classes = (
    SMTB_OT_skin_mesh_to_bone,
)
