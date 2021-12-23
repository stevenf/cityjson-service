import math, os, tempfile, time, random, model, exporters
from mathutils import Matrix, Quaternion, Vector

import sketchup
from skputil import *


class ConverterMaterial:
    def __init__(self, name):
        self.name = name
        self.setColor ( (0,0,0,0) )
        
    def setColor (self, color):
        self.color = color
        
        
class Importer():
    def __init__(self, outputfile, version):
        self.filepath = '/tmp/untitled.skp'
        self.name_mapping = {}
        self.component_meshes = {}
        self.scene = None
        self.version = version
        self.outputfile = outputfile
        self.exporter = self.getExporter ()
        
        self.model = model.Model()
      

    def getExporter (self):
        if self.version == 2: 
            return exporters.CityJSONexporter_v2 (self.outputfile)
        elif self.version == 3: 
            return exporters.CityJSONexporter_v3 (self.outputfile)
        else: 
            return exporters.CityJSONexporter (self.outputfile)
        

    def set_filename(self, filename):

        self.filepath = filename
        self.basepath, self.skp_filename = os.path.split(self.filepath)
        return self  

    def load(self, context, **options):
        self.reuse_material = True 
        self.reuse_group = False 
        self.max_instance = 50 
        self.render_engine = 'CYCLES' 
        self.component_stats = defaultdict(list)
        self.component_skip = proxy_dict()
        self.component_depth = proxy_dict()
        self.group_written = {}
        
        addon_name = __name__.split('.')[0]


        try:
            self.skp_model = sketchup.Model.from_file(self.filepath)
        except Exception as e:
            print(f'Error reading input file: {self.filepath}')
            print(e)
            return {'FINISHED'}

        self.skp_components = proxy_dict(
            self.skp_model.component_definition_as_dict)

        self.write_materials(self.skp_model.materials)

 
        D = SKP_util()


        for c in self.skp_model.component_definitions:
            self.component_depth[c.name] = D.component_deps(c.entities)

        self.component_stats = defaultdict(list)

        self.write_entities(self.skp_model.entities, "Sketchup", Matrix.Identity(4))
       

        for k, _v in self.component_stats.items():
            name, mat = k
            if options['dedub_type'] == "VERTEX":
                self.instance_group_dupli_vert(name, mat, self.component_stats)
            else:
                self.instance_group_dupli_face(name, mat, self.component_stats)


        #find geometric relations
        self.model.findRelations()
        
       
        #Write the model to a CityJSON file    
        self.exporter.writeFile(self.model)

        return
        

    def analyze_entities(self,
                         entities,
                         name,
                         transform,
                         default_material="Material",
                         etype=EntityType.none,
                         component_stats=None,
                         component_skip=[]):

        if etype == EntityType.component:
            component_stats[(name, default_material)].append(transform)

        for group in entities.groups:

            self.analyze_entities(group.entities,
                                  "G-" + group.name,
                                  transform @ Matrix(group.transform),
                                  default_material=inherent_default_mat(
                                      group.material, default_material),
                                  etype=EntityType.group,
                                  component_stats=component_stats)

        for instance in entities.instances:

            mat = inherent_default_mat(instance.material, default_material)
            cdef = self.skp_components[instance.definition.name]
            if (cdef.name, mat) in component_skip:
                continue
            self.analyze_entities(cdef.entities,
                                  cdef.name,
                                  transform @ Matrix(instance.transform),
                                  default_material=mat,
                                  etype=EntityType.component,
                                  component_stats=component_stats)

        return component_stats
    
    def write_materials(self, materials):

        self.materials = {}
        self.materials_scales = {}

        for mat in materials:

            name = mat.name

            if mat.texture:
                self.materials_scales[name] = mat.texture.dimensions[2:]
            else:
                self.materials_scales[name] = (1.0, 1.0)
            
            
            if self.reuse_material: 
                r, g, b, a = mat.color
                tex = mat.texture
                 
                converter_material = ConverterMaterial (name)
                converter_material.setColor (mat.color)
                self.model.converter_material_list[name] = converter_material

                #if tex:
                    #ignore for now

            else:
                self.materials[name] = name 
            
    def write_mesh_data(self,
                        entities=None,
                        name="",
                        default_material='Material',
                        transform=None):

        mesh_key = (name, default_material)
        if mesh_key in self.component_meshes:
            return self.component_meshes[mesh_key]
        verts = []
        loops_vert_idx = []
        mat_index = []
        smooth = []
        mats = keep_offset()
        seen = keep_offset()
        uv_list = []
        alpha = False

        for f in entities.faces:
            
            if f.material:
                mat_number = mats[f.material.name]
            else:      
                mat_number = mats[default_material]
                if default_material != 'Material':
                    try:
                        f.st_scale = self.materials_scales[default_material]
                    except KeyError as _e:
                        print ("keyerror")
                        pass
            
            vs, tri, uvs = f.tessfaces
            num_loops = 0

            mapping = {}
            for i, (v, uv) in enumerate(zip(vs, uvs)):
                l = len(seen)
                mapping[i] = seen[v]
                if len(seen) > l:
                    verts.append(v)
                uvs.append(uv)

            smooth_edge = False

            for edge in f.edges:
                if edge.GetSmooth() == True:
                    smooth_edge = True
                    break

            for face in tri:
                f0, f1, f2 = face[0], face[1], face[2]
                num_loops += 1

                if mapping[f2] == 0:
                    loops_vert_idx.extend([mapping[f2],
                                           mapping[f0],
                                           mapping[f1]])

                    uv_list.append((uvs[f2][0], uvs[f2][1],
                                    uvs[f0][0], uvs[f0][1],
                                    uvs[f1][0], uvs[f1][1]))

                else:
                    loops_vert_idx.extend([mapping[f0],
                                           mapping[f1],
                                           mapping[f2]])

                    uv_list.append((uvs[f0][0], uvs[f0][1],
                                    uvs[f1][0], uvs[f1][1],
                                    uvs[f2][0], uvs[f2][1]))

                smooth.append(smooth_edge)
                mat_index.append(mat_number)

        if len(verts) == 0:
            #print("write_mesh_data: no mesh")
            return None, False

        tri_faces = list(zip(*[iter(loops_vert_idx)] * 3))
        tri_face_count = len(tri_faces)

        loop_start = []
        i = 0
        for f in tri_faces:
            loop_start.append(i)
            i += len(f)

        loop_total = list(map(lambda f: len(f), tri_faces))

        verts = self.TransformVertices (verts, transform)
        self.model.addTotals (verts, loops_vert_idx, tri_face_count, loop_start, loop_total)
        
        self.model.addLayer (name, verts, loops_vert_idx, tri_face_count, loop_start, loop_total)

        return None, alpha
        
    def get_orientations(self, v):

            orientations = defaultdict(list)

            for transform in v:
                loc, rot, scale = Matrix(transform).decompose()
                scale = (scale[0], scale[1], scale[2])
                rot = (rot[0], rot[1], rot[2], rot[3])
                orientations[(scale, rot)].append((loc[0], loc[1], loc[2]))

            for key, locs in orientations.items():
                scale, rot = key
                yield scale, rot, locs    
        
        
    def TransformVertices (self, verts, transform):
        v2 = []
        
        loc, rot, scale = Matrix(transform).decompose()
        scale = (scale[0], scale[1], scale[2])
        rot = (rot[0], rot[1], rot[2], rot[3])
        loc = (loc[0], loc[1], loc[2])
        
        
        for (x,y,z) in verts:
            v2.append ( (x+loc[0],y+loc[1],z+loc[2]) )
       
        return v2
        
    def write_entities(self,
                       entities,
                       name,
                       parent_tranform,
                       default_material="Material",
                       etype=None):

        if etype == EntityType.component and (
                name, default_material) in self.component_skip:
            self.component_stats[(name,
                                  default_material)].append(parent_tranform)
            return

        me, alpha = self.write_mesh_data(entities=entities,
                                         name=name,
                                         default_material=default_material,
                                         transform=parent_tranform)


        for group in entities.groups:
            if group.hidden:
                continue

            self.write_entities(group.entities,
                                "G-" + group_safe_name(group.name),
                                parent_tranform @ Matrix(group.transform),
                                default_material=inherent_default_mat(
                                    group.material, default_material),
                                etype=EntityType.group)

        for instance in entities.instances:
            if instance.hidden:
                continue
                       
            mat_name = inherent_default_mat(instance.material,
                                            default_material)
            cdef = self.skp_components[instance.definition.name]
            self.write_entities(cdef.entities,
                                cdef.name,
                                parent_tranform @ Matrix(instance.transform),
                                default_material=mat_name,
                                etype=EntityType.component)
   
