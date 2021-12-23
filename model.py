

import uuid
import numpy as np
import math, sys

TYPE_UNKNOWN = 0
TYPE_BUILDING = 1
TYPE_WINDOW = 2
TYPE_BUILDINGPART = 3 

class BoundingBox:
    
    def __init__ (self):
        self.xmin = sys.float_info.max
        self.xmax = sys.float_info.min
        self.ymin = sys.float_info.max
        self.ymax = sys.float_info.min
        self.zmin = sys.float_info.max
        self.zmax = sys.float_info.min

    def check (self, x, y, z):
        self.xmin = min (x, self.xmin)
        self.xmax = max (x, self.xmax)
        self.ymin = min (y, self.ymin)
        self.ymax = max (y, self.ymax)
        self.zmin = min (z, self.zmin)
        self.zmax = max (z, self.zmax)        
        
        
    def intersects (self, bb):
        return (self.xmin < bb.xmax and self.xmax > bb.xmin and
            self.ymin < bb.ymax and self.ymax > bb.ymin and 
            self.zmin < bb.zmax and self.zmax > bb.zmin)
        
class Planes:
    def __init__ (self):
        self.planes = []
        
    def findPlane(self, tocheckplane):
        # check if plane in Planes: add plane
        for plane in self.planes:
            if plane == tocheckplane:
                return plane
        return None    
            
    
    def addPlane (self, plane):
        # add plane 
        self.planes.append (plane)
        return plane

class Plane:
    def __init__ (self, a,b,c,d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.id = uuid.uuid4().hex
        
    def equals (self, other):
   
        delta = 1.0

        if (abs (self.a-other.a) <= delta) and (abs (self.b-other.b) <= delta) and (abs (self.c-other.c) <= delta) and (abs (self.d-other.d) <= delta):
            return True
        else:
            return False
        
        
    def __eq__(self, other):
        if (self.equals(other) or self.equals( Plane(-other.a, -other.b, -other.c, -other.d)) ):
            return True
        else:
            return False
            
    def getId (self):
        return self.id
        
    def getEquation (self):
        return (self.a,self.b,self.c,self.d)
    
class Layer:
    def __init__ (self,name, verts, loops_vert_idx, tri_face_count, loop_start, loop_total):
        self.name = name
        self.verts = verts
        self.loops_vert_idx = loops_vert_idx
        self.tri_face_count=tri_face_count
        self.loop_start = loop_start
        self.loop_total = loop_total
        self.id = uuid.uuid4().hex 
        self.boundingbox = BoundingBox()
        
        self.children = set()
        self.parent=None
        self.type = TYPE_UNKNOWN
        
        
        #calculate normals
        self.normals = []
        self.calcNormalsNumpy()

        #will contain a reference to the planes 
        self.planes = []


         
        
    def calcNormalsNumpy(self):
        self.area = 0
        self.normals = []
        
        
        for i in range(len(self.loop_start)):
            i = self.loop_start[i] #start index in loops_verts_index
           
            
            #now assume c is always 3, in other words, triangles
            (v0x, v0y, v0z) = self.verts[self.loops_vert_idx[i]]
            (v1x, v1y, v1z) = self.verts[self.loops_vert_idx[i+1]]
            (v2x, v2y, v2z) = self.verts[self.loops_vert_idx[i+2]]
            
            p1 = np.array([v0x, v0y, v0z])
            p2 = np.array([v1x, v1y, v1z])
            p3 = np.array([v2x, v2y, v2z])
            
            v1 = p3 - p1
            v2 = p2 - p1
            
            cp = np.cross(v1, v2)
            a, b, c = cp
            d = np.dot(cp, p3)
            
            
            self.normals.append ( (a,b,c,d) )
            
            #also calc. area
            self.area += 0.5*math.sqrt(a*a + b*b + c*c)
        
            self.boundingbox.check (v0x, v0y, v0z)
            self.boundingbox.check (v1x, v1y, v1z)
            self.boundingbox.check (v2x, v2y, v2z)
        
            #these are actually the a,b,c,d in the equation of the plane: ax + by + cz + d = 0
       
       
    def detectPlanes(self, planes): 
        self.planes = []
        for (a,b,c,d) in self.normals:
            p = Plane (a,b,c,d)
            fplane = planes.findPlane (p)
            if (fplane is None):
                fplane = planes.addPlane(p)

            self.planes.append (fplane)

            
            
    def debugPlanes(self):
        for plane in self.planes:
            print (f"{plane.id}: {plane.a}, {plane.b}, {plane.c}, {plane.d}")
    
class Model:
    def __init__ (self):
        self.total_verts = []
        self.total_loops_vert_idx = []
        self.total_loop_total= []
        self.total_loop_start= []
        self.total_tri_face_count = 0
        self.converter_material_list = {}
        self.layers=[]
        self.planes = Planes()
    
    def addLayer (self, name, verts, loops_vert_idx, tri_face_count, loop_start, loop_total):
    
        if name!='Marc':     
            layer = Layer (name, verts, loops_vert_idx, tri_face_count, loop_start, loop_total)
            layer.detectPlanes(self.planes)
            self.layers.append (layer)
            
        
    def addTotals (self, verts, loops_vert_idx, tri_face_count, loop_start, loop_total):
       
        l = len (self.total_verts)
        
        self.total_verts.extend (verts)

        for i in range (0,len(loops_vert_idx)):
            self.total_loops_vert_idx.append (loops_vert_idx[i]+l)
        
        self.total_loop_total.extend(loop_total)
        
        last_i = 0
        if len(self.total_loop_start)>0:
            last_i = self.total_loop_start[-1] #last item
            last_i += 3
        for i in range (0, len(loop_start)):
            self.total_loop_start.append (loop_start[i]+last_i)
        

        self.total_tri_face_count += tri_face_count 
        
        
        
    def debugPlaneInOtherPlane (self, pid, lid):
        retlayers =[]
        for a in range (0, len (self.layers)):
            l = self.layers[a]
            if l.id != lid:
                for b in range (0, len (l.planes)):
                    p = l.planes[b]
                    if pid == p.id:
                        retlayers.append (l)
        
        return retlayers
        

        
    def findRelations (self):
        #sort on area desc
        self.layers.sort(key=lambda x: x.area, reverse=True)
        
        #search parents & children relations
        for layer in self.layers:
            for plane in layer.planes:
                pid = plane.id
                retlayers = self.debugPlaneInOtherPlane (pid, layer.id)
                if retlayers:
                    for l2 in retlayers:
                        if (layer.area >= l2.area and layer.boundingbox.intersects(l2.boundingbox)):

                            if (l2.parent==None):
                                l2.parent = layer
                                layer.children.add (l2)
                                
        #TODO find if children are doors or windows, assumption: doors run to floor             
        #for now: all children are windows, just for speed atm.
        for layer in self.layers:
            layer.type = TYPE_WINDOW if layer.parent else TYPE_BUILDINGPART
            
        #debug print
        '''
        for layer in self.layers: 
            for cl in layer.children:
                print (f"{layer.name} {layer.area} parent of {cl.name} {cl.area}")
            print (f"{layer.name} (type:{layer.type}) parent: {'None' if layer.parent is None else layer.parent.name}") 
            print (f"box: {layer.boundingbox.xmin}, {layer.boundingbox.ymin}, {layer.boundingbox.zmin}, {layer.boundingbox.xmax}, {layer.boundingbox.ymax}, {layer.boundingbox.zmax}")
        ''' 
        
    def debugPlanes2 (self):
        for layer in self.layers:
            print (f"{layer.id} - {layer.name}")
            layer.debugPlanes()
            
        self.debugPlanes3()
        
    def debugPlanes3 (self):
        
        for layer in self.layers:
            print (f"{layer.id} - {layer.name}")
            for plane in layer.planes:
                print (f"3: {plane.id}: {plane.a}, {plane.b}, {plane.c}, {plane.d}")