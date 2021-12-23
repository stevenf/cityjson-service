#web service
PORT=80 

#skp2cityjson converter
TEMP_DIRECTORY = ""
ALLOWED_EXTENSIONS_SKP = {'skp'}

#3D viewer
STATIC_FILES_DIRECTORY = ""

#CityJSON upload and storage in DB
ALLOWED_EXTENSIONS_CITYJSON = {'cityjson', 'json'} 
UPLOAD_DIRECTORY= ""
DB_HOST=""
DB_PORT=""
DB_DATABASE=""
DB_USER=""
DB_PASSWORD=""
DB_SCHEMA="public"
DB_TABLE_POLYZ="t3d_upload_polyz"
DB_TABLE_POLYHEDRALS="t3d_upload_polyhedrals"

#DO NOT USE FOR PRODUCTION
USER="user"
PASSWORD="password"