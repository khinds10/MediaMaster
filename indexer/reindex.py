#!/usr/bin/python3
# Media Master Main File Indexer (run $ python ./indexer.py)
# @author khinds
# @license http://opensource.org/licenses/gpl-license.php GNU Public License
import os, sys, re, subprocess, json, MySQLdb, json
import includes.mimes as mimes
import includes.mysql as mysql
import includes.thumbs as thumbs
import settings as settings

# Function to print on the same line with proper clearing
def print_status(message):
    # Clear the line with spaces and carriage return to beginning
    sys.stdout.write('\r' + ' ' * 200)  # Adjust the number based on your terminal width
    sys.stdout.write('\r' + message)
    sys.stdout.flush()

# connection to local DB
db = MySQLdb.connect(host=settings.host, user=settings.user, passwd=settings.passwd, db=settings.db)
try:
    if sys.argv[1] == 'new':
        truncateDB = 'TRUNCATE `directories_list`'
        print (truncateDB)
        mysql.executeMySQL(db, truncateDB)

        truncateDB = 'TRUNCATE `files_list`'
        print (truncateDB)
        mysql.executeMySQL(db, truncateDB)

        truncateDB = 'TRUNCATE `text_list`'
        print (truncateDB)
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

    # Skip this folder if any part of the path contains a string from the excluded_folders list (case insensitive)
    should_skip = False
    folder_lower = folder.lower()
    for excluded in settings.excluded_folders:
        excluded_lower = excluded.lower()
        # Check if any component in the path contains the excluded term
        if excluded_lower in folder_lower:
            should_skip = True
            break
    
    if should_skip:
        continue

    print_status(parentFolder + '/' + thisFolder)
        
    thisDirectoryID = 0
    try:
        thisDirectoryID = mysql.recordDirectoryFound(db, parentFolder, thisFolder)
    except:
        errorLog = open("errors.log", "a")
        errorLog.write("Could not check if directory found: \"" + parentFolder + "\" -- \"" + thisFolder + "\"\n")
        errorLog.close()  
    
    if thisDirectoryID > 0:
        for filename in files:
            with open(os.path.join(folder, filename), 'r') as fullPath:            

                # build and execute query
                fullPath = fullPath.name
                query = "SELECT * FROM `files_list` WHERE `full_path` = " + json.dumps(fullPath)
                try:
                    allFiles = mysql.getAllRows(db, query)
                except:
                    errorLog = open("errors.log", "a")
                    errorLog.write("Could not check for file by query: \"" + query + "\"\n")
                    errorLog.close()
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
                        print(fullPath, end='\r')

                        # Check if fileName contains only friendly characters to insert into the DB
                        if re.match(r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};":\\|,.<>\/? ]+$', fileName):
                            # Extract image/video dimensions
                            width = 0
                            height = 0
                            if mimeType in mimes.imageMimeTypes:
                                try:
                                    from PIL import Image
                                    with Image.open(fullPath) as img:
                                        width, height = img.size
                                except:
                                    # If we can't get dimensions, keep them as 0
                                    width = 0
                                    height = 0
                            elif mimeType in mimes.videoMimeTypes:
                                try:
                                    import cv2
                                    cap = cv2.VideoCapture(fullPath)
                                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                                    cap.release()
                                except:
                                    # If we can't get dimensions, keep them as 0
                                    width = 0
                                    height = 0
                            
                            insertFileSQL = 'INSERT INTO `files_list` (`full_path`,`directory_name`,`base_name`,`ext`,`file_name`,`mime_type`,`size`,`date_accessed`,`date_modified`,`width`,`height`,`directory_id`) VALUES ("' + str(fullPath) + '","' + str(directoryName) + '","' + str(baseName[0]) + '","' + str(fileExtension) + '","' + str(fileName) + '","' + str(mimeType) + '","' + str(size) + '",FROM_UNIXTIME(' + str(atime) + '),FROM_UNIXTIME(' + str(mtime) + '),' + str(width) + ',' + str(height) + ',"' + str(thisDirectoryID) + '")'
                            print(insertFileSQL, end='\r')
                            mysql.executeMySQL(db, insertFileSQL)
                        else:
                            print(f"Skipping insertion for file: {fileName} due to invalid characters.", end='\r')
                    except:
                        errorLog = open("errors.log", "a")
                        errorLog.write("Could not perform insert query: \"" + insertFileSQL + "\"\n")
                        errorLog.close()
        db.commit()

# get all files found and produce the preview thumbnails
thumbs.createFolderIfNotExists(settings.thumbnailsRoot)
allFiles = mysql.getAllRows(db, "SELECT * FROM `files_list`")
for file in allFiles:
    fileId,fullPath,directoryName,baseName,ext,fileName,mimeType,size,dateAccessed,dateModified,width,height,directoryId,thumbnail_exists = file
    if thumbnail_exists == 0:
        print('Creating thumbnail for:', fullPath, end='\r')
        print (mimeType)
        print ()
        if mimeType in mimes.imageMimeTypes:
            print ("Creating Image Thumbnail: " + str(fileId))
            print (fullPath)
            try:
                thumbs.createImageThumbnail(fileId, fullPath, settings.thumbnailSize, settings.thumbnailsRoot)
            except:
              print("\nAn exception occurred")  # Keep error printing on a new line
              errorLog = open("errors.log", "a")
              errorLog.write("Could not generate thumbnail for IMAGE file: \"" +fullPath + "\"\n")
              errorLog.close()              
            print('Thumbnail created for:', fullPath, end='\r')
        
        if mimeType in mimes.videoMimeTypes:
            if fileName.find(".mp4") > 0:
                print ("Creating Image Thumbnail: " + str(fileId))
                print (fullPath)
                try:
                    thumbs.createVideoThumbnail(fileId, fullPath, settings.thumbnailSize, settings.thumbnailsRoot)
                except:
                    print("\nAn exception occurred")  # Keep error printing on a new line
                    errorLog = open("errors.log", "a")
                    errorLog.write("Could not generate thumbnail for VIDEO file: " +fullPath + "\n")
                    errorLog.close()    
                print('Thumbnail created for:', fullPath, end='\r')

# all thumbnails are set to exist after generating them                
allThumbsUpdated = 'UPDATE `files_list` SET `thumbnail_exists` = 1 WHERE TRUE;'
print(allThumbsUpdated)
mysql.executeMySQL(db, allThumbsUpdated)
db.commit()

# remove duplicate rows that might have been inserted
removeDuplicateEntries = 'DELETE f1 FROM files_list f1 INNER JOIN (SELECT file_id, ROW_NUMBER() OVER (PARTITION BY full_path ORDER BY file_id) rownum FROM files_list) f2 ON f1.file_id = f2.file_id WHERE f2.rownum > 1;'
print(removeDuplicateEntries)
mysql.executeMySQL(db, removeDuplicateEntries)
db.commit()

# Print newline at the end to separate from next command prompt
print()
