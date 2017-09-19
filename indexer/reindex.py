#!/usr/bin/python
# Media Master Main File Indexer (run $ python ./indexer.py)
# @author khinds
# @license http://opensource.org/licenses/gpl-license.php GNU Public License
import os, sys, re, subprocess, json, MySQLdb
import includes.mimes as mimes
import includes.mysql as mysql
import includes.thumbs as thumbs

# connection to local DB
db = MySQLdb.connect(host="localhost", user="user", passwd="password", db="media_master")

# file system references, create thumbnails root if necessary
mediaFilesRoot = '/path/to/media/files/folder'
thumbnailSize = 256, 256
thumbnailsRoot = '/path/to/media/files/folder/thumbs'

# put this back below the recordDirectoryFound() function after thumbnailing is done
for folder, subs, files in os.walk(mediaFilesRoot):
    folderDetails = folder.split('/')
    thisFolder = folderDetails.pop()
    parentFolder = '/'.join(folderDetails)
    print 
    print parentFolder
    print parentFolder + '/' + thisFolder
    print
    thisDirectoryID = mysql.recordDirectoryFound(db, parentFolder, thisFolder)
    if thisDirectoryID > 0:
        for filename in files:
            with open(os.path.join(folder, filename), 'r') as fullPath:
                fullPath = fullPath.name
                (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(fullPath)
                try:
                    mimeType = mimes.magicMimeTypes.file(fullPath)
                    baseName = re.split('\.([^.]*)$', os.path.basename(fullPath))
                    thisFileName, fileExtension = os.path.splitext(fullPath)
                    directoryName = os.path.dirname(fullPath)
                    fileName = os.path.basename(fullPath)
                except:
                    pass
                print 
                print '------------------ FILE FOUND ------------------------------'
                print fullPath
                insertFileSQL = "INSERT INTO `files_list` (`full_path`,`directory_name`,`base_name`,`ext`,`file_name`,`mime_type`,`size`,`date_accessed`,`date_modified`,`directory_id`) VALUES ('" + str(fullPath) + "','" + str(directoryName) + "','" + str(baseName[0]) + "','" + str(fileExtension) + "','" + str(fileName) + "','" + str(mimeType) + "','" + str(size) + "',FROM_UNIXTIME(" + str(atime) + "),FROM_UNIXTIME(" + str(mtime) + "),'" + str(thisDirectoryID) + "')"
                try:
                    mysql.executeMySQL(db, insertFileSQL)
                except:
                    pass

# get all files found and produce the preview thumbnails
thumbs.createFolderIfNotExists(thumbnailsRoot)
allFiles = mysql.getAllRows(db, "SELECT * FROM `files_list`")
for file in allFiles:
    fileId,fullPath,directoryName,baseName,ext,fileName,mimeType,size,dateAccessed,dateModified,width,height,directoryId = file
    
    if mimeType in mimes.imageMimeTypes:
        print "Creating Image Thumbnail: " + str(fileId)
        print fullPath
        thumbs.createImageThumbnail(fileId, fullPath, thumbnailSize, thumbnailsRoot)
        print
    
    if mimeType in mimes.videoMimeTypes:
        print "Creating Image Thumbnail: " + str(fileId)
        print fullPath
        try:
            thumbs.createVideoThumbnail(fileId, fullPath, thumbnailSize, thumbnailsRoot)
        except:
            pass
        print
