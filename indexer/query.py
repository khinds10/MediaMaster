#!/usr/bin/python
# Media Master Query Server
# @author khinds
# @license http://opensource.org/licenses/gpl-license.php GNU Public License
import cgi, json, MySQLdb
import includes.mysql as mysql
print "Content-type:application/json\r\n\r\n"

thumbnailsRoot = 'thumbs'
class Thumbail:
    image = ''
    fullPath = ''

def getThumbForId(id):
    return '/' + str(int(id/1000)) + '/' + str(id) + '.jpg'

# all the image mimeTypes
imageMimeTypes = []
imageMimeTypes.append('"image/gif; charset=binary"')
imageMimeTypes.append('"image/jpeg; charset=binary"')
imageMimeTypes.append('"image/png; charset=binary"')
imageMimeTypes.append('"image/x-ms-bmp; charset=binary"')
whereImageMimeTypes = " OR `mime_type` = ".join(imageMimeTypes)

# all the video mimeTypes
videoMimeTypes = []
videoMimeTypes.append('"application/ogg; charset=binary"')
videoMimeTypes.append('"application/vnd.rn-realmedia; charset=binary"')
videoMimeTypes.append('"audio/mpeg; charset=binary"')
videoMimeTypes.append('"video/mp4; charset=binary"')
videoMimeTypes.append('"video/mpeg; charset=binary"')
videoMimeTypes.append('"video/quicktime; charset=binary"')
videoMimeTypes.append('"video/webm; charset=binary"')
videoMimeTypes.append('"video/x-flv; charset=binary"')
videoMimeTypes.append('"video/x-ms-asf; charset=binary"')
videoMimeTypes.append('"video/x-msvideo; charset=binary"')
whereVideoMimeTypes = " OR `mime_type` = ".join(videoMimeTypes)

# parse possible incoming query HTTP params
sortType = 'newest'
mediaType = 'all'
keyword = ''
arguments = cgi.FieldStorage()
for i in arguments.keys():

    if (arguments[i].name == "sortType"):
        sortType = arguments[i].value

    if (arguments[i].name == "mediaType"):
        mediaType = arguments[i].value

    if (arguments[i].name == "keyword"):
        keyword = arguments[i].value

# connection to local DB
db = MySQLdb.connect(host="localhost", user="user", passwd="password", db="media_master")

# create orderBy based on sortType search if provided
orderBy = ''
if (sortType == "newest"):
    orderBy = 'ORDER BY `date_modified` DESC'

if (sortType == "oldest"):
    orderBy = 'ORDER BY `date_modified` ASC'

if (sortType == "oldest"):
    orderBy = 'ORDER BY `date_modified` ASC'

# create orderBy based on mediaType search if provided
whereClauseMimeType = '`mime_type` = ' + whereImageMimeTypes + whereVideoMimeTypes
if (mediaType == "images"):
    whereClauseMimeType = '`mime_type` = ' + whereImageMimeTypes

if (mediaType == "videos"):
    whereClauseMimeType = '`mime_type` = ' + whereVideoMimeTypes

# build the where clause 
whereClauseKeyword = ""
if keyword is not "":
    whereClauseKeyword = " AND `full_path` LIKE '%" + keyword + "%' "

# build and execute query
query = "SELECT * FROM `files_list` WHERE 1 AND (" + whereClauseMimeType + ") "+ whereClauseKeyword + " " + orderBy + " LIMIT 500"
allFiles = mysql.getAllRows(db, query)

# generate the JSON response of media files found
print '['
for file in allFiles:
    fileId,fullPath,directoryName,baseName,ext,fileName,mimeType,size,dateAccessed,dateModified,width,height,directoryId = file
    thumbnail = Thumbail()
    thumbnail.image = thumbnailsRoot + getThumbForId(fileId)
    thumbnail.fullPath = fullPath
    print json.dumps(thumbnail.__dict__)
    print ','
print '{}]'
