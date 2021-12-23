

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_CITYJSON 

def list_files():
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)

def upload(request, version):
    
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

        file.save(os.path.join(TEMP_DIRECTORY, filename))

        #convert
        inputfile = os.path.join(TEMP_DIRECTORY, filename)
        outputfile = filename + ".json"
        
        si = SceneImporter(os.path.join(TEMP_DIRECTORY, outputfile), version)
        si.set_filename (inputfile)
        si.load("")
        
        return send_from_directory(TEMP_DIRECTORY, outputfile, as_attachment=True)
    return "" 
