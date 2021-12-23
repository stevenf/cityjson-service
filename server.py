import os

from flask import Flask, request, abort, jsonify, send_from_directory
from flask_httpauth import HTTPBasicAuth
from waitress import serve
import uuid
from werkzeug.utils import secure_filename
import werkzeug.security 
from converter import Importer
import uploadtodb
import config 


#if the temp directory doesn't exist, try to create it.
if not os.path.exists(config.TEMP_DIRECTORY):
    os.makedirs(config.TEMP_DIRECTORY)


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #16 MB


#Simple BasicAuthentication, only for testing and development. Do not use for production 
auth = HTTPBasicAuth()
users = {
    config.USER: werkzeug.security.generate_password_hash(config.PASSWORD),
}
@auth.verify_password
def verify_password(username, password):
    #Check if supplied username, password are correct
    if username in users and werkzeug.security.check_password_hash(users.get(username), password): return username

#Check if uploaded file is allowed based on the extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS_SKP   

#
def checkFileAndConvert(request, version):
    
    # check if the post request contains a file
    if 'file' not in request.files:
        abort(400, "no file supplied")
        
    file = request.files['file']
    
    # Check if a filename is supplied
    if file.filename == '':
        abort(400, "no filename supplied")
    if file: 
        #Check if extension is alloweed
        if not allowed_file(file.filename):
            abort(400, "filetype not allowed")
        filename = secure_filename(file.filename)
        
        file.save(os.path.join(config.TEMP_DIRECTORY, filename))
        
        #convert
        inputfile = os.path.join(config.TEMP_DIRECTORY, filename)
        outputfile = filename + ".json"
        
        si = Importer(os.path.join(config.TEMP_DIRECTORY, outputfile), version)
        si.set_filename (inputfile)
        si.load("")
        
        print (outputfile) 
        
        #return the generated CityJSON
        return send_from_directory(config.TEMP_DIRECTORY, outputfile, as_attachment=True)
    return "" 


@app.route('/skp2cityjson/v2', methods=['POST'])
@auth.login_required
def skp2cityjson_v2():
    return checkFileAndConvert (request, version=2)

#curl -F "file=@test2.skp" -X POST http://127.0.0.1:8080/upload
@app.route('/skp2cityjson', methods=['POST'])
@auth.login_required
def skp2cityjson():
    return checkFileAndConvert (request, version=1)

@app.route('/skp2cityjson/v3', methods=['POST'])
@auth.login_required
def skp2cityjson_v3():
    
    return checkFileAndConvert (request, version=3)

@app.route('/skp2cityjson/v1', methods=['POST'])
@auth.login_required
def skp2cityjson_v1():
    
    return checkFileAndConvert (request, version=1)

@app.route('/viewer/<path:path>')
@auth.login_required
def send_static_files(path):
    return send_from_directory(config.STATIC_FILES_DIRECTORY, path)
    
    
#EXTRA: File storage (disk and database)  
@app.route('/upload', methods=['POST'])
@auth.login_required
def upload():
    return uploadtodb.upload (request)    
    
@app.route("/upload/files")
@auth.login_required
def list_files():
    """Endpoint to list files on the server."""
    return uploadtodb.list_files()


@app.route("/upload/files/<path:path>")
@auth.login_required
def get_file(path):
    """Endpoint to download a file."""
    return send_from_directory(config.UPLOAD_DIRECTORY, path, as_attachment=True)
    
    

#Start: python server.py
#Test with cUrl:
#curl -F "file=@<file>.skp" -X POST -u user:password http://127.0.0.1:8080/skp2cityjson


if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=config.PORT)