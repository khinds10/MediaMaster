#!/usr/bin/python3
# Media Master MySQL Handler
# @author khinds
# @license http://opensource.org/licenses/gpl-license.php GNU Public License
import os, sys, re, subprocess, json, MySQLdb, json
 
def getOneRow(db, sQLStatement):

    try:
        dbCursor = executeMySQL(db, sQLStatement)
        row = dbCursor.fetchone ()
        dbCursor.close()
    except:
        row = None
        
    if not (row is None):
        return row[0]
    return ''
    
def getAllRows(db, sQLStatement):

    try:
        dbCursor = executeMySQL(db, sQLStatement)
        data = dbCursor.fetchall ()
        dbCursor.close()
    except:
        data = None    
    
    if not (data is None):
        return data
    return ''
    
def executeMySQL(db, sQLStatement):
    dbCursor = db.cursor()
    dbCursor.execute (sQLStatement)
    db.commit()
    return dbCursor

def recordDirectoryFound(db, parentFolder, thisFolder):    
    sql = "SELECT `id` FROM `directories_list` WHERE `path` = " + json.dumps(parentFolder)
    rowDetails = getOneRow(db , sql)
    parentDirectoryID = 0
    try:
        if (rowDetails):
            parentDirectoryID = rowDetails
        executeMySQL(db, "INSERT INTO `directories_list` (`name`, `path`, `parent_id`) VALUES ('" + json.dumps(thisFolder) + "','" + json.dumps(parentFolder) + '/' + json.dumps(thisFolder) + "','" + json.dumps(parentDirectoryID) + "')")
        rowInsertIdentity = getOneRow(db , 'select @@identity')
    except:
        rowInsertIdentity = -1
    return rowInsertIdentity
