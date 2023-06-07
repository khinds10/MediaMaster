#!/usr/bin/python
# Media Master Main File Indexer (run $ python ./indexer.py)
# @author khinds
# @license http://opensource.org/licenses/gpl-license.php GNU Public License
import os, sys, re, subprocess, json, MySQLdb, json
import includes.mimes as mimes
import includes.mysql as mysql
import includes.thumbs as thumbs
import settings as settings
import datetime

# connection to local DB
db = MySQLdb.connect(host=settings.host, user=settings.user, passwd=settings.passwd, db=settings.db)

# connection to local DB
db_orig = MySQLdb.connect(host=settings.host, user=settings.user, passwd=settings.passwd, db=settings.db_original)

# get all files found and produce the preview thumbnails
allFiles = mysql.getAllRows(db, "SELECT * FROM `files_list`")
for file in allFiles:
    fileId,fullPath,directoryName,baseName,ext,fileName,mimeType,size,dateAccessed,dateModified,width,height,directoryId,thumnail_exists = file
    fullPath = fullPath.replace('/media/khinds/','/home/khinds/Files/')
    originalFile = mysql.getAllRows(db_orig, "SELECT * FROM `files_list` WHERE `full_path` = '" + fullPath + "'")

    print("SELECT * FROM `files_list` WHERE `full_path` = '" + fullPath + "'")
    for original in originalFile:
        fileId_original,fullPath_original,directoryName_original,baseName_original,ext_original,fileName_original,mimeType_original,size_original,dateAccessed_original,dateModified_original,width_original,height_original,directoryId_original,thumnail_exists = original
    
        date_format = datetime.datetime.strptime(str(dateAccessed_original), "%Y-%m-%d")
        dateAccessed_original_unix_time = round(datetime.datetime.timestamp(date_format))

        date_format = datetime.datetime.strptime(str(dateAccessed_original), "%Y-%m-%d")
        dateModified_original_unix_time = round(datetime.datetime.timestamp(date_format))
    
        updateNewFile = 'UPDATE `files_list` SET `date_accessed` = FROM_UNIXTIME(' + str(dateAccessed_original_unix_time) + ', "%Y-%m-%d") , `date_modified` = FROM_UNIXTIME(' + str(dateModified_original_unix_time) + ', "%Y-%m-%d") WHERE file_id = ' + str(fileId)
        print(updateNewFile)
        mysql.executeMySQL(db, updateNewFile)
