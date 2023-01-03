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
imageMimeTypes.append('"image/gif"')
imageMimeTypes.append('"image/jpeg"')
imageMimeTypes.append('"image/png"')
imageMimeTypes.append('"image/x-ms-bmp"')
imageMimeTypes.append('"image/bmp"')
imageMimeTypes.append('"image/x-tga"')
imageMimeTypes.append('"image/webp"')
whereImageMimeTypes = " OR `mime_type` = ".join(imageMimeTypes)

# all the video mimeTypes
videoMimeTypes = []
videoMimeTypes.append('"application/ogg"')
videoMimeTypes.append('"application/vnd.rn-realmedia"')
videoMimeTypes.append('"audio/mpeg"')
videoMimeTypes.append('"video/mp4"')
videoMimeTypes.append('"video/mpeg"')
videoMimeTypes.append('"video/quicktime"')
videoMimeTypes.append('"video/webm"')
videoMimeTypes.append('"video/x-flv"')
videoMimeTypes.append('"video/x-ms-asf"')
videoMimeTypes.append('"video/x-msvideo"')
videoMimeTypes.append('"audio/mp4"')
videoMimeTypes.append('"video/x-m4v"')
videoMimeTypes.append('"video/MP2T"')
whereVideoMimeTypes = " OR `mime_type` = ".join(videoMimeTypes)

# parse possible incoming query HTTP params
sortType = 'random'
mediaType = 'all'
keyword = ''
page = '0'
year = str(todaysDate.year-50)
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

# page limit is the page number times the page size
page = int(page) * int(pageSize)

# create orderBy based on sortType search if provided
orderBy = ''
if (sortType == "newest"):
    orderBy = 'ORDER BY `date_accessed` DESC'

if (sortType == "oldest"):
    orderBy = 'ORDER BY `date_accessed` ASC'

if (sortType == "random"):
    orderBy = 'ORDER BY RAND()'

# create orderBy based on mediaType search if provided
whereClauseMimeType = '`mime_type` = ' + whereImageMimeTypes + whereVideoMimeTypes
if (mediaType == "images"):
    whereClauseMimeType = '`mime_type` = ' + whereImageMimeTypes

if (mediaType == "videos"):
    whereClauseMimeType = '`mime_type` = ' + whereVideoMimeTypes

# build the where clause 
whereClauseKeyword = ""
if keyword != "":
    whereClauseKeyword = whereClauseKeyword + " AND `full_path` LIKE '%" + keyword + "%' "

# for now remove the blank file extensions of those old flash files
whereClauseKeyword = whereClauseKeyword + " AND `ext` != '' "

# get the years back for which files to return by date modified
whereClauseKeyword = whereClauseKeyword + " AND YEAR(date_modified) >= '" + year + "'"

# build and execute query
query = "SELECT * FROM `files_list` WHERE 1 AND (" + whereClauseMimeType + ") "+ whereClauseKeyword + " " + orderBy + " LIMIT " + str(page) + ", " + str(pageSize)
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
    fileId,fullPath,directoryName,baseName,ext,fileName,mimeType,size,dateAccessed,dateModified,width,height,directoryId,thumbnail_exists = file
    thumbnail = Thumbail()
    thumbnail.image = settings.thumbnailsRoot + getThumbForId(fileId)
    thumbnail.fullPath = fullPath
    thumbnail.fileType = getFileType(mimeType)
    print (json.dumps(thumbnail.__dict__))
    print (',')
print ('{}]}')
