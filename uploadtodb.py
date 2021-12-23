
import config
import os
from werkzeug.utils import secure_filename
from flask import Flask, request, abort, jsonify, send_from_directory
import psycopg2
import json


class CityJSONProcessor:
    def __init__(self, host, port, db, user, password, schema, table_polyz, table_polyhedral, filename):
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password
        self.schema = schema
        self.table_polyz = table_polyz
        self.table_polyhedral = table_polyhedral
        self.filename=filename
        
        self.conn = None    
        self.conn = psycopg2.connect(f"dbname={db} user={user} host={host} password={password}")
    
    def checkTable(self, tablename):
        sql = f"SELECT EXISTS (SELECT FROM pg_tables WHERE  schemaname = '{self.schema}' AND tablename  = '{tablename}')"
        
        cur = self.conn.cursor()
        cur.execute(sql)
    
        exists = cur.fetchone()[0]
        cur.close()
        
        return exists
        
        
    def createTable(self, tablename):
        sql = f"CREATE TABLE {self.schema}.{tablename} (\
                id serial,\
                geom geometry(MultiPolygonZ, 7415)\
                );"    
      
        cur = self.conn.cursor()
        cur.execute(sql)
        cur.close()
        print (sql)
        self.conn.commit()
      
    def checkTables(self):
        if not self.checkTable(self.table_polyz):
            print ("niet bestaat")
            self.createTable(self.table_polyz)
            
        if not self.checkTable(self.table_polyhedral):
            self.createTable(self.table_polyhedral)    
    
    def loadCityJSON(self):
        with open(os.path.join(config.UPLOAD_DIRECTORY, self.filename)) as f:
            cityjson = json.load(f)
        
        #load vertex data
        vertices = cityjson["vertices"]
        for vertex in vertices:
            print (vertex)
        
        coords = "" 
        bfirst = True
        
        for scityobject in cityjson["CityObjects"]:
            cityobject = cityjson["CityObjects"][scityobject]
            geometry = cityobject["geometry"]
            boundaries = geometry[0]["boundaries"]          
            
            for a in boundaries:

                for b in a:
                    print (b)
                    if not bfirst:
                        coords += ","
                    else: 
                        bfirst = False
                    coords += "(("
                    cfirst = True
                    firstvertex=None
                    for c in b:
                        vertex = vertices[c]
                        if not cfirst:
                            coords += ", "
                        else:
                            firstvertex = vertex
                            cfirst = False
                        print (vertex)
                        coords+= f"{vertex[0]} {vertex[1]} {vertex[2]}"
                    coords+= f", {firstvertex[0]} {firstvertex[1]} {firstvertex[2]}"
                    coords += "))"    
                    
            print (coords)
            
            multipolygonz = "MULTIPOLYGONZ("+coords+")"
            print (multipolygonz)
            
            sql = f"insert into t3d_upload_polyz (geom) values (ST_GeomFromText('{multipolygonz}',7415))" 

            cur = self.conn.cursor()
            cur.execute(sql)
            cur.close()
            self.conn.commit()

        
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS_CITYJSON 

def list_files():
    files = []
    for filename in os.listdir(config.UPLOAD_DIRECTORY):
        path = os.path.join(config.UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)

def upload(request):
    
    # check if the post request has the file part
    if 'file' not in request.files:
        print('No file part')
        abort(400, "no file part")
        
    file = request.files['file']

    if file.filename == '':
        print('No selected file')
        abort(400, "no selected file")
    
    if file: 
        if not allowed_file(file.filename):
            abort(400, "filetype not allowed")
        filename = secure_filename(file.filename)
        file.save(os.path.join(config.UPLOAD_DIRECTORY, filename))
        
        proc = CityJSONProcessor(config.DB_HOST, config.DB_PORT, config.DB_DATABASE, config.DB_USER, config.DB_PASSWORD, config.DB_SCHEMA, config.DB_TABLE_POLYZ, config.DB_TABLE_POLYHEDRALS, filename)
        
        proc.checkTables()
        proc.loadCityJSON ()
        
        print (filename)

    return "", 201
