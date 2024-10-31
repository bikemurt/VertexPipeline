bl_info = {
    "name": "V Pipeline",
    "description": "Vertex based pipeline",
    "author": "Michael Jared",
    "version": (0,1),
    "location": "View3D > Properties > Godot Pipeline",
    "doc_url": "https://www.michaeljared.ca",
    "blender": (2, 80, 0),
    "category": "Generic"
}

import bpy, math
from mathutils import Vector, Color
from bpy.types import (
            Operator,
            PropertyGroup, 
            Panel,
            UIList,
            Object
        )
from bpy.props import (
            IntProperty,
            EnumProperty,
            BoolProperty,
            FloatProperty,
            StringProperty,
            PointerProperty,
            CollectionProperty
        )
    
### PROPS

class VPipelineProperties(PropertyGroup):
    color_name : StringProperty(name = "Color Vertex Data", default = "ColorX", description = "Color Vertex Data")
    metal_name : StringProperty(name = "Metal/Rough Vertex Data", default = "MetalX", description = "Color Vertex Data")
    v_name : StringProperty(name = "V Name", default = "", description = "Current Vertex Data Name")
    
    naming_UI : BoolProperty(name = "Setup", default = False)
    paint_UI : BoolProperty(name = "Paint", default = False)
    metal_colors_UI : BoolProperty(name = "Metal Colors", default = False)
    palette_UI : BoolProperty(name = "Palettes", default = False)
    
    active_palette : StringProperty(name = "Active Palette", default = "")

### PANEL

class VPipelinePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_v_pipeline"
    bl_label = "V Pipeline"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "V Pipeline"
    
    @classmethod
    def poll(cls, context):
        # If you need specific conditions for the panel to appear, modify the poll method
        return context.area.type == 'VIEW_3D'

    def dropdown(self, box, props, prop, text_override = ""):
        row = box.row()
        
        p = getattr(props, prop)
        if text_override == "":
            row.prop(props, prop,
                icon="TRIA_DOWN" if p else "TRIA_RIGHT",
                icon_only=False, emboss=False
            )
        else:
            row.prop(props, prop,
                icon="TRIA_DOWN" if p else "TRIA_RIGHT",
                icon_only=False, emboss=False, text=text_override
            )
        
        return p

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.VPipelineProps
        obj = context.object
        
        is_color = props.active_palette == props.color_name
        is_metal = props.active_palette == props.metal_name
        
        box = layout.box()
        if self.dropdown(box, props, "naming_UI"):
            row = box.row()
            row.label(text="Color Name:")
            row = box.row()
            row.prop(props, "color_name", text="")
            
            row = box.row()
            row.label(text="Metal/Rough Name:")
            row = box.row()
            row.prop(props, "metal_name", text="")
            
            row = box.row()
            row.operator("object.v_setup", text="Setup")
        
        # CHECK IF SETUP IS COMPLETE
        color_p = bpy.data.palettes.get(props.color_name)
        metal_p = bpy.data.palettes.get(props.metal_name)
        
        obj = context.active_object
        
        setup = False
        if context.active_object:
            attribs = obj.data.color_attributes
            
            color_v = attribs.get(props.color_name)
            metal_v = attribs.get(props.metal_name)
            
            # palettes and vertex colors set up
            setup = color_p and metal_p and color_v and metal_v
        
        
        if setup:
            box = layout.box()
            if self.dropdown(box, props, "paint_UI", f"Paint {props.active_palette}"):
                
                row = box.row()
                row.enabled = bpy.context.active_object.mode != 'OBJECT'
                row.operator("object.mode_set", text="Switch to Object Mode").mode = 'OBJECT'
                
                row = box.row()
                row.enabled = not is_color
                row.operator("object.v_set_active", icon='NONE', text="Color").active_name = 0
                
                row = box.row()
                row.enabled = not is_metal
                row.operator("object.v_set_active", icon='NONE', text="Metal").active_name = 1
                
                row = box.row()
                row.operator("object.v_paint", text="Paint Vertex Colors", icon="BRUSH_PAINT_SELECT")
                
                row = box.row()
                row.prop(context.tool_settings.vertex_paint.brush, "color", text="Active Color")
                
                # only display for metal
                if is_metal:
                    if self.dropdown(box, props, "metal_colors_UI"):
                        metal_colors = ["Shiny Metal", "Painted Metal", "Gloss Plastic", "Matte Plastic"]
                        i = 0
                        for color in metal_colors:
                            row = box.row()
                            row.operator("object.v_set_metal_color", text=color).palette_index = i
                            i += 1
                
                # select polys
                s = ""
                index = 0
                if props.active_palette == props.color_name:
                    s = "Color"
                    index = 0
                elif props.active_palette == props.metal_name:
                    s = "Metal"
                    index = 0
                
                if s != "":
                    row = box.row()
                    row.operator("object.v_select_current_color", text=f"Select Polys Active {s}").index = index
            
            box = layout.box()
            if self.dropdown(box, props, "palette_UI"):
                row = box.row()
                row.operator("object.v_update_geo_palette", text="Update Geonodes Palette")
                
                row = box.row()
                row.operator("object.v_print_palette", text="Print Palettes")
            
                ts = context.tool_settings
                if ts.vertex_paint.palette:
                    row = box.row()
                    row.label(text=f"{props.active_palette} Palette")
                    row = box.row()
                    row.template_palette(ts.vertex_paint, "palette", color=True)
                    
        # SETUP NOT COMPLETE
        else:
            row = layout.row()
            row.label(text="Setup incomplete.")
        
        
### HELPER FUNCTIONS

def srgb_to_linear(c):
    if c < 0.04045:
        return 0.0 if c < 0.0 else c * (1.0 / 12.92)
    
    return ((c + 0.055) / 1.055) ** 2.4

def linear_to_srgb(c):
    if c < 0.0031308:
        srgb = 0.0 if c < 0.0 else c * 12.92
    else:
        srgb = 1.055 * math.pow(c, 1.0 / 2.4) - 0.055
    return srgb




### OPERATORS

class SetActive(bpy.types.Operator):
    """Set Active"""
    bl_idname = "object.v_set_active"
    bl_label = "Set Active"
    bl_options = {'REGISTER', 'UNDO'}
    
    active_name: IntProperty(name = "Set Active Name", default=0)
    
    @classmethod
    def poll(cls, context):
        # Make the operator available in all contexts by returning True
        return True  # You can add custom conditions if needed
    
    
    def set_vertex(self, context, obj, props, v_name):
        if obj and obj.type == 'MESH':
            bpy.ops.object.mode_set(mode='VERTEX_PAINT')
            vertex_paint = context.tool_settings.vertex_paint
            for palette in bpy.data.palettes:
                if palette.name == v_name:
                    vertex_paint.palette = palette
            
            for v in obj.data.vertex_colors:
                if v.name == v_name:
                    v.active_render = True
                    v.active = True
                    props.v_name = v.name
            
            props.active_palette = v_name
            #obj.data.use_paint_mask = True
    
    def execute(self, context):
        scene = context.scene
        props = scene.VPipelineProps
        
        obj = context.active_object
        if self.active_name == 0:
            self.set_vertex(context, obj, props, props.color_name)
        
        if self.active_name == 1:
            self.set_vertex(context, obj, props, props.metal_name)
        
        return {'FINISHED'}

class SetMetalColor(bpy.types.Operator):
    """Set Metal Color"""
    bl_idname = "object.v_set_metal_color"
    bl_label = "Set Metal Color"
    bl_options = {'REGISTER', 'UNDO'}
    
    palette_index: IntProperty(name = "Palette Index", default=0)
    
    @classmethod
    def poll(cls, context):
        # Make the operator available in all contexts by returning True
        return True  # You can add custom conditions if needed
    
    def execute(self, context):
        scene = context.scene
        props = scene.VPipelineProps
        
        context.tool_settings.vertex_paint.brush
        
        palette = bpy.data.palettes.get("MetalX")
        if palette:
            context.tool_settings.vertex_paint.brush.color = palette.colors[self.palette_index].color
            bpy.ops.object.v_paint()
            bpy.ops.object.mode_set(mode='OBJECT')
            
        return {'FINISHED'}


class UpdateGeoPalette(bpy.types.Operator):
    """Update Geo Palette"""
    bl_idname = "object.v_update_geo_palette"
    bl_label = "Update Geo Palette"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        # Make the operator available in all contexts by returning True
        return True  # You can add custom conditions if needed
    
    def set_geo_color(self, obj, mod_name, name, palette_color):
        mod = obj.modifiers[mod_name]
        identifier = mod.node_group.interface.items_tree[name].identifier
        mod[identifier][0] = srgb_to_linear(palette_color.r)
        mod[identifier][1] = srgb_to_linear(palette_color.g)
        mod[identifier][2] = srgb_to_linear(palette_color.b)
    
    def execute(self, context):
        scene = context.scene
        props = scene.VPipelineProps
        
        obj = context.active_object
        if obj:
            mod_name = ""
            
            cc = bpy.data.node_groups['ColorConverter']
            found = False
            for mod in obj.modifiers:
                if mod.type == 'NODES':
                    if mod.node_group == cc:
                        mod_name = mod.name
                        print(mod_name)
                
            c_p = bpy.data.palettes.get(props.color_name)
            if c_p:
                self.set_geo_color(obj, mod_name, "Color0", c_p.colors[0].color)
                self.set_geo_color(obj, mod_name, "Color1", c_p.colors[1].color)
                self.set_geo_color(obj, mod_name, "Color2", c_p.colors[2].color)
                self.set_geo_color(obj, mod_name, "Color3", c_p.colors[3].color)
                
            m_p = bpy.data.palettes.get(props.metal_name)
            if m_p:
                self.set_geo_color(obj, mod_name, "Metal0", m_p.colors[0].color)
                self.set_geo_color(obj, mod_name, "Metal1", m_p.colors[1].color)
                self.set_geo_color(obj, mod_name, "Metal2", m_p.colors[2].color)
                self.set_geo_color(obj, mod_name, "Metal3", m_p.colors[3].color)
            
        return {'FINISHED'}


def color_match(col1, col2, tol=0.001):
    def vector(col):
        return Vector([max(0, min(1, c)) for c in col])

    d = vector(col1) - vector(col2)
    return d.length <= tol

class SelectCurrentColor(bpy.types.Operator):
    """Select Current Color"""
    bl_idname = "object.v_select_current_color"
    bl_label = "Select Current Color"
    bl_options = {'REGISTER', 'UNDO'}
    
    index: IntProperty(name = "Index", default=0)
    
    @classmethod
    def poll(cls, context):
        # Make the operator available in all contexts by returning True
        return True  # You can add custom conditions if needed
    
    def execute(self, context):
        scene = context.scene
        props = scene.VPipelineProps
        
        obj = context.active_object
        mesh = obj.data
        
        v_name = ""
        if self.index == 0:
            v_name = props.color_name
        if self.index == 1:
            v_name = props.metal_name
            
        bpy.ops.object.mode_set(mode='OBJECT')
        
        color_layer = mesh.color_attributes.get(v_name)
        target_color = context.tool_settings.vertex_paint.brush.color
        
        i = 0
        for att in color_layer.data:
            clr = Color((att.color_srgb[0], att.color_srgb[1], att.color_srgb[2]))
            
            if color_match(clr, target_color, 0.01):
                vi = mesh.loops[i].vertex_index
                mesh.vertices[vi].select = True
                
            i += 1
        
        bpy.ops.object.mode_set(mode='EDIT')
        
        return {'FINISHED'}


class PrintPalette(bpy.types.Operator):
    """Print Palette"""
    bl_idname = "object.v_print_palette"
    bl_label = "Print Palette"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        # Make the operator available in all contexts by returning True
        return True  # You can add custom conditions if needed
    
    def execute(self, context):
        scene = context.scene
        props = scene.VPipelineProps
        
        obj = context.active_object
        if obj:
            c_p = bpy.data.palettes.get(props.color_name)
            if c_p:
                print("COLOR")
                for i in range(4):
                    c = c_p.colors[i].color
                    r = round(srgb_to_linear(c.r), 6)
                    g = round(srgb_to_linear(c.g), 6)
                    b = round(srgb_to_linear(c.b), 6)
                    print(f"vec3({r}, {g}, {b}),")
            
            print("METAL")
            m_p = bpy.data.palettes.get(props.metal_name)
            if m_p:
                for i in range(4):
                    c = m_p.colors[i].color
                    r = round((c.r), 6)
                    g = round((c.g), 6)
                    b = round((c.b), 6)
                    print(f"vec3({r}, {g}, {b}),")
            
            
        return {'FINISHED'}

class Setup(bpy.types.Operator):
    """Setup"""
    bl_idname = "object.v_setup"
    bl_label = "Setup"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        # Make the operator available in all contexts by returning True
        return True  # You can add custom conditions if needed
    
    def new_color_att(self, obj, props, name):
        attribs = obj.data.color_attributes
        if not attribs.get(name):
            att = obj.data.color_attributes.new(
                name=name,
                type='BYTE_COLOR',
                domain='CORNER'
            )
            
            for v_index in range(len(obj.data.vertices)):
                att.data[v_index].color = [0, 0, 0, 1]
    
    def new_color_palette(self, name):
        color_p = bpy.data.palettes.get(name)
        if not color_p:
            pal = bpy.data.palettes.new(name)
            
            p1 = pal.colors.new()
            p2 = pal.colors.new()
            p3 = pal.colors.new()
            p4 = pal.colors.new()
            
            pal.colors.active = p1
    
    def execute(self, context):
        scene = context.scene
        props = scene.VPipelineProps
        
        obj = context.active_object
        
        if obj and obj.type == 'MESH':
            # vertex colors
            self.new_color_att(obj, props, props.color_name)
            self.new_color_att(obj, props, props.metal_name)
            self.new_color_att(obj, props, "Color")
            self.new_color_att(obj, props, "AO")
            self.new_color_att(obj, props, "EdgeMask")
            
            # materials
            uber_mat = bpy.data.materials.get("UberShader")
            
            found = False
            for m_slot in obj.material_slots:
                mat = m_slot.material
                if mat == uber_mat:
                    found = True
                    break
            
            if not found:
                obj.data.materials.append(uber_mat)
            
            # palettes
            self.new_color_palette(props.color_name)
            self.new_color_palette(props.metal_name)
            
            # geonodes
            cc = bpy.data.node_groups['ColorConverter']
            found = False
            for mod in obj.modifiers:
                if mod.type == 'NODES':
                    if mod.node_group == cc:
                        found = True
                
            if not found:
                mod = obj.modifiers.new('ColorConverter', type='NODES')
                mod.node_group = cc
                
                c_id = mod.node_group.interface.items_tree["ColorName"].identifier
                mod[c_id] = props.color_name
                
                m_id = mod.node_group.interface.items_tree["MetalName"].identifier
                mod[m_id] = props.metal_name
            
        return {'FINISHED'}

class VPaint(bpy.types.Operator):
    """V Paint"""
    bl_idname = "object.v_paint"
    bl_label = "V Paint"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        # Make the operator available in all contexts by returning True
        return True  # You can add custom conditions if needed
    
    def execute(self, context):
        scene = context.scene
        props = scene.VPipelineProps
        
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        obj = context.active_object
        obj.data.use_paint_mask = True
        bpy.ops.paint.vertex_color_set()
        
        return {'FINISHED'}

###

classes = [VPipelineProperties, VPipelinePanel, SetActive, SetMetalColor, UpdateGeoPalette, SelectCurrentColor, PrintPalette, Setup, VPaint]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.VPipelineProps = PointerProperty(type = VPipelineProperties)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()