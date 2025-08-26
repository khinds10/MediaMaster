#!/usr/bin/python3
# Media Master Query Server
# @author khinds
# @license http://opensource.org/licenses/gpl-license.php GNU Public License
import cgi, json, MySQLdb
import includes.mysql as mysql
import settings as settings
from datetime import date

print("Content-type:application/json\r\n\r\n")

# set the results page size
pageSize = 50
todaysDate = date.today()

# connection to local DB
db = MySQLdb.connect(host=settings.host, user=settings.user, passwd=settings.passwd, db=settings.db)

settings.thumbnailsRoot = 'thumbs'
class Thumbail:
    image = ''
    fullPath = ''
    fileType = ''

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
whereVideoMimeTypes = " OR `mime_type` LIKE ".join(videoMimeTypes)

# parse possible incoming query HTTP params
sortType = 'random'
mediaType = 'all'
keyword = ''
page = '0'
year = str(todaysDate.year-50)
grown = False
expanded = False
featured = False
modelPreview = False
arguments = cgi.FieldStorage()
for i in arguments.keys():

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

# get the years back for which files to return by date modified
#whereClauseKeyword = whereClauseKeyword + " AND date_modified >= '" + year + "-01-01'"

# Add conditions for grown, expanded, and featured
folderConditions = []
if grown:
    folderConditions.append("`directory_name` LIKE '%GROWN%'")
if expanded:
    folderConditions.append("`directory_name` LIKE '%EXPANDED%'")
if featured:
    folderConditions.append("`directory_name` LIKE '%FEATURES%'")

folderCondition = " AND " + " AND ".join(folderConditions) if folderConditions else ""

# build and execute query
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
    if int(year) < 2000:
        query = f"SELECT f.* FROM files_list f INNER JOIN (SELECT DISTINCT directory_name FROM files_list ORDER BY RAND() LIMIT 1) AS random_dir ON f.directory_name = random_dir.directory_name WHERE 1 AND ({whereClauseMimeType}) {whereClauseKeyword} {folderCondition} {orderBy} LIMIT {page}, {pageSize}"
    else:
        query = f"SELECT * FROM `files_list` WHERE 1 AND ({whereClauseMimeType}) {whereClauseKeyword} {folderCondition} {orderBy} LIMIT {page}, {pageSize}"
    
    allFiles = mysql.getAllRows(db, query)

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
    thumbnail = Thumbail()
    thumbnail.image = settings.thumbnailsRoot + getThumbForId(fileId)
    thumbnail.fullPath = fullPath
    thumbnail.fileType = getFileType(mimeType)
    print (json.dumps(thumbnail.__dict__))
    print (',')
print ('{}]}')
