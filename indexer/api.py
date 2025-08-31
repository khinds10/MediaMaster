#!/usr/bin/env python3
# Media Master API Server
# @author khinds
# @license http://opensource.org/licenses/gpl-license.php GNU Public License
import cgi, json, MySQLdb
import includes.mysql as mysql
import settings as settings
from datetime import date

print("Content-type:application/json\r\n\r\n")

# set the results page size
pageSize = 100
todaysDate = date.today()

# connection to local DB
db = MySQLdb.connect(host=settings.host, user=settings.user, passwd=settings.passwd, db=settings.db)

settings.thumbnailsRoot = 'thumbs'
class Thumbail:
    image = ''
    fullPath = ''
    fileType = ''
    fileId = 0
    isFavorite = False
    width = 0
    height = 0

def getThumbForId(id):
    return '/' + str(int(id/1000)) + '/' + str(id) + '.jpg'

# all the image mimeTypes
imageMimeTypes = []
imageMimeTypes.append('"%image/gif%"')
imageMimeTypes.append('"%image/jpeg%"')
imageMimeTypes.append('"%image/png%"')
imageMimeTypes.append('"%image/x-ms-bmp%"')
imageMimeTypes.append('"%image/bmp%"')
imageMimeTypes.append('"%image/x-tga%"')
imageMimeTypes.append('"%image/webp%"')
whereImageMimeTypes = " OR `mime_type` LIKE ".join(imageMimeTypes)

# all the video mimeTypes
videoMimeTypes = []
videoMimeTypes.append('"%application/ogg%"')
videoMimeTypes.append('"%application/vnd.rn-realmedia%"')
videoMimeTypes.append('"%audio/mpeg%"')
videoMimeTypes.append('"%video/mp4%"')
videoMimeTypes.append('"%video/mpeg%"')
videoMimeTypes.append('"%video/quicktime%"')
videoMimeTypes.append('"%video/webm%"')
videoMimeTypes.append('"%video/x-flv%"')
videoMimeTypes.append('"%video/x-ms-asf%"')
videoMimeTypes.append('"%video/x-msvideo%"')
videoMimeTypes.append('"%audio/mp4%"')
videoMimeTypes.append('"%video/x-m4v%"')
videoMimeTypes.append('"%video/MP2T%"')
videoMimeTypes.append('"%video/x-matroska%"')
videoMimeTypes.append('"%video/x-ms-wmv%"')
videoMimeTypes.append('"%video/avi%"')
videoMimeTypes.append('"%video/x-avi%"')
whereVideoMimeTypes = " OR `mime_type` LIKE ".join(videoMimeTypes)

# parse possible incoming query HTTP params
action = 'query'  # Default action is query
file_id = ''
sortType = 'random'
mediaType = 'all'
keyword = ''
page = '0'
year = str(todaysDate.year-50)
grown = False
expanded = False
featured = False
modelPreview = False
favorites_only = False

# Parse form data
arguments = cgi.FieldStorage()
for i in arguments.keys():
    if (arguments[i].name == "action"):
        action = arguments[i].value

    if (arguments[i].name == "file_id"):
        file_id = arguments[i].value

    if (arguments[i].name == "year"):
        year = arguments[i].value

    if (arguments[i].name == "sortType"):
        sortType = arguments[i].value

    if (arguments[i].name == "mediaType"):
        mediaType = arguments[i].value

    if (arguments[i].name == "keyword"):
        keyword = arguments[i].value

    if (arguments[i].name == "page"):
        page = arguments[i].value

    if (arguments[i].name == "grown"):
        grown = arguments[i].value.lower() == 'true'

    if (arguments[i].name == "expanded"):
        expanded = arguments[i].value.lower() == 'true'

    if (arguments[i].name == "featured"):
        featured = arguments[i].value.lower() == 'true'

    if (arguments[i].name == "modelPreview"):
        modelPreview = arguments[i].value.lower() == 'true'
        
    if (arguments[i].name == "favorites"):
        favorites_only = arguments[i].value.lower() == 'true'

# Handle favorites actions
if action in ['add', 'remove', 'check']:
    response = {"success": False, "message": "Invalid request"}
    
    if action == "add" and file_id:
        try:
            # Check if already a favorite
            check_query = f"SELECT favorite_id FROM favorites WHERE file_id = {file_id}"
            existing = mysql.getOneRow(db, check_query)
            
            if not existing:
                # Add to favorites
                insert_query = f"INSERT INTO favorites (file_id) VALUES ({file_id})"
                mysql.executeMySQL(db, insert_query)
                response = {"success": True, "message": "Added to favorites", "is_favorite": True}
            else:
                response = {"success": True, "message": "Already in favorites", "is_favorite": True}
        except Exception as e:
            response = {"success": False, "message": f"Error adding favorite: {str(e)}"}
    
    elif action == "remove" and file_id:
        try:
            # Remove from favorites
            remove_query = f"DELETE FROM favorites WHERE file_id = {file_id}"
            mysql.executeMySQL(db, remove_query)
            response = {"success": True, "message": "Removed from favorites", "is_favorite": False}
        except Exception as e:
            response = {"success": False, "message": f"Error removing favorite: {str(e)}"}
    
    elif action == "check" and file_id:
        try:
            # Check if file is a favorite
            check_query = f"SELECT favorite_id FROM favorites WHERE file_id = {file_id}"
            existing = mysql.getOneRow(db, check_query)
            is_favorite = existing != ''
            response = {"success": True, "is_favorite": is_favorite}
        except Exception as e:
            response = {"success": False, "message": f"Error checking favorite status: {str(e)}"}
    
    # Return the response as JSON
    print(json.dumps(response))

# Handle query action (original query.py functionality)
elif action == 'query':
    # page limit is the page number times the page size
    page = int(page) * int(pageSize)
    
    # create orderBy based on sortType search if provided
    orderBy = ''
    if (sortType == "newest"):
        orderBy = 'ORDER BY `date_modified` DESC'
    
    if (sortType == "oldest"):
        orderBy = 'ORDER BY `date_modified` ASC'
    
    if (sortType == "random"):
        orderBy = 'ORDER BY RAND()'
    
    # create orderBy based on mediaType search if provided
    whereClauseMimeType = '`mime_type` LIKE ' + whereImageMimeTypes + whereVideoMimeTypes
    if (mediaType == "images"):
        whereClauseMimeType = '`mime_type` LIKE ' + whereImageMimeTypes
    
    if (mediaType == "videos"):
        whereClauseMimeType = '`mime_type` LIKE ' + whereVideoMimeTypes
    
    # build the where clause 
    whereClauseKeyword = ""
    if keyword != "":
        # Split the keyword by minus sign and tilde
        keywords = keyword.replace('-', ' -').replace('~', ' ~').split()
        
        # Initialize include and exclude lists
        include_keywords = []
        exclude_keywords = []
        
        # Process the keywords
        for kw in keywords:
            if kw.startswith('-'):
                exclude_keywords.append(kw[1:])
            elif kw.startswith('~'):
                include_keywords.append(kw[1:])
            else:
                # The first keyword without a modifier is the main keyword
                main_keyword = kw
        
        # Include the main keyword
        whereClauseKeyword = whereClauseKeyword + " AND `full_path` LIKE '%" + main_keyword + "%' "
        
        # Include additional keywords with the tilde modifier
        for include_keyword in include_keywords:
            whereClauseKeyword = whereClauseKeyword + " AND `full_path` LIKE '%" + include_keyword + "%' "
        
        # Exclude keywords with the minus sign modifier
        for exclude_keyword in exclude_keywords:
            whereClauseKeyword = whereClauseKeyword + " AND `full_path` NOT LIKE '%" + exclude_keyword + "%' "
    
    # for now remove the blank file extensions of those old flash files
    whereClauseKeyword = whereClauseKeyword + " AND `ext` != '' "
    
    # Add conditions for grown, expanded, and featured
    folderConditions = []
    if grown:
        folderConditions.append("`directory_name` LIKE '%GROWN%'")
    if expanded:
        folderConditions.append("`directory_name` LIKE '%EXPANDED%'")
    if featured:
        folderConditions.append("`directory_name` LIKE '%FEATURES%'")
    
    folderCondition = " AND " + " AND ".join(folderConditions) if folderConditions else ""
    
    # Build and execute query
    if modelPreview:
        # Select 10 random folders
        folder_query = "SELECT DISTINCT directory_name FROM files_list WHERE directory_name NOT LIKE '%diary%'ORDER BY RAND() LIMIT 10"
        selected_folders = mysql.getAllRows(db, folder_query)
        
        # Prepare to collect files from the selected folders
        allFiles = []
        for folder in selected_folders:
            folder_name = folder[0]
            # Select 5 random files from each folder
            file_query = f"SELECT * FROM files_list WHERE directory_name = '{folder_name}' AND ({whereClauseMimeType}) ORDER BY RAND() LIMIT 5"
            files = mysql.getAllRows(db, file_query)
            allFiles.extend(files)
    else:
        # Base query
        base_query = "SELECT f.* FROM files_list f"
        
        # Join with favorites table if favorites filter is enabled
        if favorites_only:
            base_query += " INNER JOIN favorites fav ON f.file_id = fav.file_id"
        
        # Add filter to exclude small videos when -LG versions exist
        lg_filter = ""
        if mediaType == "videos" or mediaType == "all":
            lg_filter = """ AND NOT (
                f.file_name NOT LIKE '%-LG%' 
                AND EXISTS (
                    SELECT 1 FROM files_list f2 
                    WHERE f2.directory_name = f.directory_name 
                    AND f2.file_name = CONCAT(SUBSTRING_INDEX(f.file_name, '.', 1), '-LG.', SUBSTRING_INDEX(f.file_name, '.', -1))
                    AND f2.mime_type LIKE '%video%'
                )
            )"""
        
        # For random folder selection
        if int(year) < 2000 and not favorites_only:
            query = f"{base_query} INNER JOIN (SELECT DISTINCT directory_name FROM files_list ORDER BY RAND() LIMIT 1) AS random_dir ON f.directory_name = random_dir.directory_name WHERE 1 AND ({whereClauseMimeType}) {whereClauseKeyword} {folderCondition} {lg_filter} {orderBy} LIMIT {page}, {pageSize}"
        else:
            query = f"{base_query} WHERE 1 AND ({whereClauseMimeType}) {whereClauseKeyword} {folderCondition} {lg_filter} {orderBy} LIMIT {page}, {pageSize}"
        
        allFiles = mysql.getAllRows(db, query)
    
    # Get all favorite file_ids for quick lookup
    favorite_ids = set()
    favorite_query = "SELECT file_id FROM favorites"
    favorite_results = mysql.getAllRows(db, favorite_query)
    if favorite_results:
        favorite_ids = {row[0] for row in favorite_results}
    
    def getFileType(mimeType):
        '''assign video or image file type based on known mime types '''
        if mimeType.startswith( 'video/' ):
            return 'video'
        if mimeType.startswith( 'application/vnd' ):
            return 'video'
        if mimeType.startswith( 'audio/mpeg' ):
            return 'video'
        return 'image'
    
    # generate the JSON response of media files found
    print('{"results":[')
    for file in allFiles:
        fileId,fullPath,directoryName,baseName,ext,fileName,mimeType,size,dateAccessed,dateModified,width,height,directoryId,thumbnailExists = file
        
        # Handle null width/height values
        if width is None:
            width = 0
        if height is None:
            height = 0
            
        thumbnail = Thumbail()
        thumbnail.image = settings.thumbnailsRoot + getThumbForId(fileId)
        thumbnail.fullPath = fullPath
        thumbnail.fileType = getFileType(mimeType)
        thumbnail.fileId = fileId
        thumbnail.isFavorite = fileId in favorite_ids
        thumbnail.width = width
        thumbnail.height = height
        print (json.dumps(thumbnail.__dict__))
        print (',')
    print ('{}]}') 
