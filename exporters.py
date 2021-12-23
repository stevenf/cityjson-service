import random
import model


class BaseExporter:
    def __init__(self, outputfile):
        self.outputfile = outputfile
        self.f = None
        self.model = None
        
    def writeFile (self, model):
        self.model = model
    
    
class BaseSimpleCityJSONexporter (BaseExporter):    
    def __init__(self, outputfile):
        super().__init__(outputfile)
        
    def writeFile (self, model):
        super().writeFile(model)

class CityJSONexporter(BaseSimpleCityJSONexporter):
    def __init__(self, outputfile):
        super().__init__(outputfile)
        self.first = True
        
    def writeFile (self, model, **args):
        super().writeFile(model)
        
        self.f = open(self.outputfile, "w")
        self.writeHeader()
        
        self.writeCityJSON (self.model)         
        self.writeFooter()

        self.writeEnd()
        self.f.close()
         
    def writeBoundaries (self, loops_vert_idx, tri_face_count, loop_start, loop_total, start_i):
        for i in range(tri_face_count):
            if i>0:
                    self.f.write(",")
            v_start_i = loop_start[i]
            v_end_i = v_start_i + loop_total [i]
         
            self.f.write ("[[")
            for j in range (v_start_i, v_end_i):
                if j>v_start_i:
                    self.f.write(",")
                
                self.f.write (f"{loops_vert_idx[j]+start_i}")
            self.f.write ("]]\n") 
           
    def writeVertices (self, verts):
        for i in range(len(verts)):
            if i>0: self.f.write(",")
            self.f.write  ("\n[")
            (x,y,z) = verts[i]
            self.f.write (f"{x}, {y}, {z}")
            self.f.write  ("]")
   
    def writeHeader (self): 
        self.f.write ('{"CityObjects": ')
        
    def writeFooter (self): 
        self.f.write ('}')
        
    def writeMaterials(self, converter_material_list):

        self.f.write ('\n"appearance": {')
        self.f.write ('\n\t"materials": [')
        
        first = True
        for name in converter_material_list:
            if not first:
                self.f.write ('\n\t\t\t,')
            else:
                first = False
            self.f.write ('\n\t\t\t{')
            cm = converter_material_list[name]
            (r,g,b,a) = cm.color
            name = cm.name
        
            self.f.write ('\n\t\t\t\t"name": ')
            self.f.write ('"{}",'.format(name))
     
            self.f.write ('\n\t\t\t\t"diffuseColor": ')
            self.f.write ('[{},{},{}]'.format (r,g,b))
                    
            self.f.write ('\n\t\t\t}')

        
        self.f.write ('\n\t]')
        self.f.write ('}')
        
        
    def writeLayer (self, layer, start_i):

        self.f.write ('"' + layer.name + '": ')        
        self.f.write ('{"geometry": ')
        self.f.write ('[{"boundaries": [[')
        
        self.writeBoundaries (layer.loops_vert_idx, layer.tri_face_count, layer.loop_start, layer.loop_total, start_i)
        
        self.f.write ('''
        ]
          ],
          "lod": 1,
          "type": "Solid"
        ''' ) 
         
        self.f.write('\n\t\t\t\t,')
        self.f.write('"material": {')
        self.f.write('\n\t\t\t\t\t"": {')
        self.f.write('\n\t\t\t\t\t\t"values": [')
        
        
        self.f.write('\n\t\t\t\t\t\t\t[')						
									
        for i in range (layer.tri_face_count):
            if i != 0: self.f.write (',')
               
            #self.f.write ('1')
            self.f.write ("{}".format(random.randint(0,10))) 
        
        self.f.write('\n\t\t\t\t\t\t]')
        self.f.write('\n\t\t\t\t\t]')
        self.f.write('\n\t\t\t\t\t}')
        self.f.write('\n\t\t\t\t}')
          
          
        self.f.write('''
                }
              ],
              "attributes": {
                "function": "something"
              },
              "type": "Building"
            }    
        ''')
        
        
    def writeVerticesAndMaterials(self,verts, converter_material_list):
        self.f.write ('''
            },
          "type": "CityJSON",
          "version": "1.0",
          "vertices": [
        ''')

        self.writeVertices (verts)
        self.f.write ('],')
        self.writeMaterials(converter_material_list)
        
        self.f.write('''         
          ,"metadata": {
            "geographicalExtent": [
              -1.0,
              -1.0,
              0.0,
              1.0,
              1.0,
              1.0
            ]
          }
        ''')
    
    
        
            
    def writeCityJSON (self, model): #(self, verts, loops_vert_idx, tri_face_count, loop_start, loop_total,converter_material_list):
        #(self.total_verts, self.total_loops_vert_idx, self.total_tri_face_count, self.total_loop_start, self.total_loop_total, self.converter_material_list)        
        verts = model.total_verts
        loops_vert_idx = model.total_loops_vert_idx
        tri_face_count = model.total_tri_face_count
        loop_start = model.total_loop_start
        loop_total = model.total_loop_total
        converter_material_list = model.converter_material_list

        
        if not self.first:
            self.f.write (',')
        else:    
            self.first = False
        
        
        self.f.write ('{"id-1": ') 
        self.f.write ('{"geometry": ')
        self.f.write ('[{"boundaries": [[')
        
        self.writeBoundaries (loops_vert_idx, tri_face_count, loop_start, loop_total,0)
        
        self.f.write ('''
        ]
          ],
          "lod": 1,
          "type": "Solid"
        ''' ) 
         
        self.f.write('\n\t\t\t\t,')
        self.f.write('"material": {')
        self.f.write('\n\t\t\t\t\t"": {')
        self.f.write('\n\t\t\t\t\t\t"values": [')
        
        
        self.f.write('\n\t\t\t\t\t\t\t[')						
									
        for i in range (tri_face_count):
            if i != 0: self.f.write (',')
               
            #self.f.write ('1')
            self.f.write ("{}".format(random.randint(0,10))) 
        
        self.f.write('\n\t\t\t\t\t\t]')
        self.f.write('\n\t\t\t\t\t]')
        self.f.write('\n\t\t\t\t\t}')
        self.f.write('\n\t\t\t\t}')
          
          
        self.f.write('''
        }
      ],
      "attributes": {
        "function": "something"
      },
      "type": "Building"
    }
  },
  "type": "CityJSON",
  "version": "1.0",
  "vertices": [
        ''')

        self.writeVertices (verts)
        self.f.write ('],')
        self.writeMaterials(converter_material_list)
        
        self.f.write('''
         
  ,"metadata": {
    "geographicalExtent": [
      -1.0,
      -1.0,
      0.0,
      1.0,
      1.0,
      1.0
    ]
  }
        ''')
        
    def writeEnd(self):
        self.f.close()
        
        
class CityJSONexporter_v2 (CityJSONexporter):
    def __init__(self, outputfile):
        super().__init__(outputfile)
        
    def writeFile (self, model, **args):
        super().writeFile(model)
        
        self.f = open(self.outputfile, "w")
        self.writeLayers(self.model.layers, self.model.converter_material_list)
        self.f.close()
        
    def writeLayers (self, layers, converter_material_list):
        self.writeHeader()
        self.f.write ('{')
        bfirst = True
        
        start_i = 0
        
        for layer in layers:
            if layer.name != 'Marccccc': 
                if bfirst: 
                    bfirst=False
                else:
                    self.f.write (",")
                self.writeLayer (layer, start_i)
                start_i += len (layer.verts) #+ 1
            
        #add all verts
        verts=[]
        for layer in layers:
            verts += layer.verts
        
        self.writeVerticesAndMaterials (verts, converter_material_list)
        self.writeFooter()    
        

class CityJSONexporter_v3 (CityJSONexporter_v2):
    def __init__(self, outputfile):
        super().__init__(outputfile)
        
    def writeFile (self, model, **args):
        super().writeFile(model)
        
        self.f = open(self.outputfile, "w")
        self.writeLayers(self.model.layers, self.model.converter_material_list)
        self.f.close()        
    
    #MultiSurface 
    def writeBoundariesssss (self, loops_vert_idx, tri_face_count, loop_start, loop_total, start_i):
        for i in range(tri_face_count):
            if i>0:
                    self.f.write(",")
            v_start_i = loop_start[i]
            v_end_i = v_start_i + loop_total [i]
            #print ("face")
            self.f.write ("[")
            for j in range (v_start_i, v_end_i):
                if j>v_start_i:
                    self.f.write(",")
                #print (loops_vert_idx[j])
                self.f.write (f"{loops_vert_idx[j]+start_i}")
            self.f.write ("]\n") 
    
    
    def writeLayer (self, layer, start_i):
        self.f.write ('"' + layer.name + '": ')        
        self.f.write ('{"geometry": ')
        self.f.write ('[{"boundaries": [[')
        
        self.writeBoundaries (layer.loops_vert_idx, layer.tri_face_count, layer.loop_start, layer.loop_total, start_i)
        self.f.write ("]]")
        self.f.write (",")
        
        semantictype = '"WallSurface"' if layer.parent is None else '"Window"' 
        
        self.f.write ('  "lod": 1,')
        self.f.write ('  "type": "Solid",')
        self.f.write ('  "semantics": {')
        self.f.write ('     "surfaces": [{')
        self.f.write (f'        "type": {semantictype}')
        self.f.write ('     }],')
        self.f.write ('     "values": [0]')
        self.f.write ('   }')
     
         
        #skip material even, geeft validatie fout in deze versie, niet in andere versies.
        '''
        self.f.write('\n\t\t\t\t,')
        self.f.write('"material": {')
        self.f.write('\n\t\t\t\t\t"": {')
        self.f.write('\n\t\t\t\t\t\t"values": [')
        
        
        self.f.write('\n\t\t\t\t\t\t\t[')						
									
        for i in range (layer.tri_face_count):
            if i != 0: self.f.write (',')
               
            #self.f.write ('1')
            self.f.write ("{}".format(random.randint(0,10))) 
        
        self.f.write('\n\t\t\t\t\t\t]')
        
        self.f.write('\n\t\t\t\t\t]')
        self.f.write('\n\t\t\t\t\t}')
        self.f.write('\n\t\t\t\t}')
        '''
        stype = self.createTypeAttribuutAsString(layer)
        schildren = self.createChildrenAttribuutAsString(layer)
        sparents = self.createParentsAttribuutAsString(layer)
          
        self.f.write('''
                }
              ],
              "attributes": {
                "function": "something"
              },
        ''')
        
        
        self.f.write (stype)
        
        if schildren != None: self.f.write (',' + schildren)
        if sparents != None: self.f.write (',' + sparents)
      
        self.f.write("}")
        
        
    def createTypeAttribuutAsString(self, layer):
        if layer.type == model.TYPE_BUILDINGPART and layer.parent != None: return f'"type": "BuildingPart"'
        if layer.type == model.TYPE_BUILDINGPART and layer.parent == None: return f'"type": "Building"' # a buildingpart must have a parent otherwise the JSON is not valid
        if layer.type == model.TYPE_BUILDING: return f'"type": "Building"'
        if layer.type == model.TYPE_WINDOW: return f'"type": "BuildingInstallation"'
        
        return f'"type": "Building"'
    
    def createParentsAttribuutAsString(self, layer): 
        if layer.parent: return f'"parents": ["{layer.parent.name}"]'
        
        return None
    
    def createChildrenAttribuutAsString(self, layer): 
        if layer.children:
            sc = ''
            bfirst = True
            for child in layer.children:
                if (child):
                    if not bfirst: 
                        sc+=','
                    bfirst = False
                    sc+=f'"{child.name}"'
            if (len (sc) > 0):
                return f'"children":[{sc}]' 
        