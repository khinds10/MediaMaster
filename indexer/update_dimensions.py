#!/usr/bin/python3
# Media Master Dimension Updater
# Updates existing database records with image and video dimensions
# @author khinds
# @license http://opensource.org/licenses/gpl-license.php GNU Public License
import os, sys, MySQLdb
import includes.mimes as mimes
import includes.mysql as mysql
import settings as settings

# connection to local DB
db = MySQLdb.connect(host=settings.host, user=settings.user, passwd=settings.passwd, db=settings.db)

def update_dimensions():
    print("Starting dimension update for existing files...")
    
    # Get all files that don't have dimensions set
    query = "SELECT file_id, full_path, mime_type FROM files_list WHERE (width = 0 OR width IS NULL) AND (height = 0 OR height IS NULL)"
    files = mysql.getAllRows(db, query)
    
    print(f"Found {len(files)} files without dimensions")
    
    updated_count = 0
    error_count = 0
    
    for file in files:
        file_id, full_path, mime_type = file
        
        width = 0
        height = 0
        
        try:
            if mime_type in mimes.imageMimeTypes:
                # Extract image dimensions
                from PIL import Image
                with Image.open(full_path) as img:
                    width, height = img.size
                    
            elif mime_type in mimes.videoMimeTypes:
                # Extract video dimensions
                import cv2
                cap = cv2.VideoCapture(full_path)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()
                
            # Update the database record
            if width > 0 and height > 0:
                update_query = f"UPDATE files_list SET width = {width}, height = {height} WHERE file_id = {file_id}"
                mysql.executeMySQL(db, update_query)
                updated_count += 1
                print(f"Updated file {file_id}: {width}x{height} - {os.path.basename(full_path)}")
            else:
                print(f"Skipped file {file_id}: Could not extract dimensions - {os.path.basename(full_path)}")
                
        except Exception as e:
            error_count += 1
            print(f"Error processing file {file_id}: {str(e)} - {os.path.basename(full_path)}")
    
    # Commit all changes
    db.commit()
    
    print(f"\nUpdate complete!")
    print(f"Successfully updated: {updated_count} files")
    print(f"Errors: {error_count} files")

if __name__ == "__main__":
    update_dimensions()
