# cityjson-service
Experimental python service to:
* convert Sketchup to CityJSON
* store/retrieve CityJSON  
* store CityJSON geometries in a Postgres/PostGIS database

## Installation
Download SketchUp SDK for Windows from https://extensions.sketchup.com/sketchup-sdk
Copy SketchUp.dll and SketchUpCommonPreferences to folder

Build Python Bindings using cython from: https://github.com/RedHaloStudio/Sketchup_Importer
or alternatively, go to https://github.com/RedHaloStudio/Sketchup_Importer/releases, download sketchup_importer_?.zip, copy the sketchup.cp39-win_amd64.pyd to the folder and rename to sketchup.pyd. This release also contains the DLLs mentioned above.



## Execution
python server.py

## Remarks
* The server uses Basic Authentication with a single user. Only use this feature for developing/testing.

## config.py
For now the config.py file contains the configuration parameters

```python

#webservice
PORT=<port> #port to run the webservice on.

#skp2cityjson converter
TEMP_DIRECTORY = <temporary directory used to create CityJSON>
ALLOWED_EXTENSIONS_SKP = {'skp'} #only allow .SKP to be uploaded for conversion

#3D viewer
STATIC_FILES_DIRECTORY = "<directory with static file>"

#CityJSON upload and storage in DB
ALLOWED_EXTENSIONS_CITYJSON = {'cityjson', 'json'} #only json and cityjson are allowed to be uploaded
UPLOAD_DIRECTORY= "<directory the uploaded files are stored in>"
DB_HOST="<host address of the PostgreSQL database>"
DB_PORT="<port>"
DB_DATABASE="<database name>"
DB_USER="<user name>"
DB_PASSWORD="<password>"
DB_SCHEMA="<schema>"
DB_TABLE_POLYZ="<table to store uploaded CityJSON geometry as 3D polygons>"
DB_TABLE_POLYHEDRALS="table to store uploaded CityJSON geometry as 3D Polyhedrals"

#DO NOT USE FOR PRODUCTION
#used for basic authentication
USER="user"
PASSWORD="password"
```