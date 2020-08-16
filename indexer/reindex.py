#!/usr/bin/python
# Media Master Main File Indexer (run $ python ./indexer.py)
# @author khinds
# @license http://opensource.org/licenses/gpl-license.php GNU Public License
import os, sys, re, subprocess, json, MySQLdb, json
import includes.mimes as mimes
import includes.mysql as mysql
import includes.thumbs as thumbs
import settings as settings

# connection to local DB
db = MySQLdb.connect(host=settings.host, user=settings.user, passwd=settings.passwd, db=settings.db)
try:
    if sys.argv[1] == 'new':
        truncateDB = 'TRUNCATE `directories_list`'
        print(truncateDB)
        mysql.executeMySQL(db, truncateDB)

        truncateDB = 'TRUNCATE `files_list`'
        print(truncateDB)
        mysql.executeMySQL(db, truncateDB)

        truncateDB = 'TRUNCATE `text_list`'
        print(truncateDB)
        mysql.executeMySQL(db, truncateDB)
        
except IndexError:
    print ()
    print ('please provide a "new" or "update" as a flag for the indexer')
    print ('usage: python3 reindex.py new|update')
    print ()
    exit()

# put this back below the recordDirectoryFound() function after thumbnailing is done
for folder, subs, files in os.walk(settings.mediaFilesRoot):
    folderDetails = folder.split('/')
    thisFolder = folderDetails.pop()
    parentFolder = '/'.join(folderDetails)
    print()
    print(parentFolder)
    print(parentFolder + '/' + thisFolder)
    print()
    thisDirectoryID = mysql.recordDirectoryFound(db, parentFolder, thisFolder)
    if thisDirectoryID > 0:
        for filename in files:
            with open(os.path.join(folder, filename), 'r') as fullPath:            

                # build and execute query
                fullPath = fullPath.name
                query = "SELECT * FROM `files_list` WHERE `full_path` = " + json.dumps(fullPath)
                allFiles = mysql.getAllRows(db, query)
                try:
                    if allFiles[0][0]:
                        pass
                except:            
                    try:
                        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(fullPath)
                        mimeType = mimes.magicMimeTypes.file(fullPath)
                        baseName = re.split('\.([^.]*)$', os.path.basename(fullPath))
                        thisFileName, fileExtension = os.path.splitext(fullPath)
                        thisFileName = thisFileName
                        fileExtension = fileExtension
                        directoryName = os.path.dirname(fullPath)
                        fileName = os.path.basename(fullPath)
                        print()
                        print('------------------ FILE FOUND ------------------------------')
                        print(fullPath)
                        insertFileSQL = 'INSERT INTO `files_list` (`full_path`,`directory_name`,`base_name`,`ext`,`file_name`,`mime_type`,`size`,`date_accessed`,`date_modified`,`directory_id`) VALUES (' + json.dumps(fullPath) + ',' + json.dumps(directoryName) + ',' + json.dumps(baseName[0]) + ',' + json.dumps(fileExtension) + ',' + json.dumps(fileName) + ',' + json.dumps(mimeType) + ',' + json.dumps(size) + ',FROM_UNIXTIME(' + json.dumps(atime) + '),FROM_UNIXTIME(' + json.dumps(mtime) + '),' + json.dumps(thisDirectoryID) + ')'
                        print(insertFileSQL)
                        mysql.executeMySQL(db, insertFileSQL)                
                    except:
                        pass

        db.commit()

# get all files found and produce the preview thumbnails
thumbs.createFolderIfNotExists(settings.thumbnailsRoot)
allFiles = mysql.getAllRows(db, "SELECT * FROM `files_list`")
for file in allFiles:
    fileId,fullPath,directoryName,baseName,ext,fileName,mimeType,size,dateAccessed,dateModified,width,height,directoryId,thumnail_exists = file
    if thumnail_exists == 0:
        print ('new file found')
        print(mimeType)
        print ()
        if mimeType in mimes.imageMimeTypes:
            print("Creating Image Thumbnail: " + str(fileId))
            print(fullPath)
            try:
                thumbs.createImageThumbnail(fileId, fullPath, settings.thumbnailSize, settings.thumbnailsRoot)
            except:
              print("An exception occurred")
            print()
        
        if mimeType in mimes.videoMimeTypes:
            print(mimeType)
            print(fileName.find(".mp4"))
            print(fileName)
            if fileName.find(".mp4") > 0:
                print("Creating Image Thumbnail: " + str(fileId))
                print(fullPath)
                try:
                    thumbs.createVideoThumbnail(fileId, fullPath, settings.thumbnailSize, settings.thumbnailsRoot)
                except:
                  print("An exception occurred")
                print()
                
allThumbsUpdated = 'UPDATE `files_list` SET `thumnail_exists` = 1 WHERE TRUE;'
print(allThumbsUpdated)
mysql.executeMySQL(db, allThumbsUpdated)
db.commit()
