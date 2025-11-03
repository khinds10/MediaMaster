#!/usr/bin/python3
# Media Master Main File Indexer (run $ python ./indexer.py)
# @author khinds
# @license http://opensource.org/licenses/gpl-license.php GNU Public License
import os, sys, re, subprocess, json, MySQLdb, json
import includes.mimes as mimes
import includes.mysql as mysql
import includes.thumbs as thumbs
import settings as settings
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich import box
from time import time

# Initialize Rich console
console = Console()

# Data structures to track operations
inserted_records = []
created_thumbnails = []
current_status = "Initializing..."
current_file = ""
current_phase = "Indexing"
start_time = time()
spinner_frame_idx = 0

def createLargerVideoVersion(videoPath, originalWidth, originalHeight):
    """
    Create a larger version of a small video using ffmpeg.
    The new video will be double the size and have -LG suffix.
    """
    # Calculate new dimensions (double the size)
    newWidth = originalWidth * 2
    newHeight = originalHeight * 2
    
    # Create the new filename with -LG suffix
    directory = os.path.dirname(videoPath)
    filename = os.path.basename(videoPath)
    name, ext = os.path.splitext(filename)
    newFilename = f"{name}-LG{ext}"
    newPath = os.path.join(directory, newFilename)
    
    # Check if the larger version already exists
    if os.path.exists(newPath):
        return newPath
    
    # Build ffmpeg command to resize the video
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', videoPath,
        '-vf', f'scale={newWidth}:{newHeight}',
        '-c:v', 'libx264',  # Use H.264 codec
        '-c:a', 'copy',     # Copy audio without re-encoding
        '-preset', 'medium', # Balance between speed and quality
        '-crf', '23',       # Constant rate factor for quality
        '-y',               # Overwrite output file if it exists
        newPath
    ]
    
    try:
        # Run ffmpeg command
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            return newPath
        else:
            raise Exception(f"FFmpeg failed with return code {result.returncode}")
            
    except subprocess.TimeoutExpired:
        raise Exception("FFmpeg process timed out")
    except Exception as e:
        raise e

def create_display_layout() -> Layout:
    """Create the Rich layout with status panel and three main sections"""
    layout = Layout()
    layout.split_column(
        Layout(name="status", size=4),
        Layout(name="main", ratio=1)
    )
    layout["main"].split_row(
        Layout(name="inserted", ratio=1),
        Layout(name="thumbnails", ratio=1),
        Layout(name="summary", ratio=1)
    )
    return layout

def render_status_panel() -> Panel:
    """Render the status panel with spinner and current activity"""
    global spinner_frame_idx
    elapsed = int(time() - start_time)
    minutes = elapsed // 60
    seconds = elapsed % 60
    elapsed_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
    
    # Animated spinner frames - update frame index on each render
    spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    spinner_frame_idx = (spinner_frame_idx + 1) % len(spinner_frames)
    spinner_char = spinner_frames[spinner_frame_idx]
    
    # Use Text.from_markup to properly parse Rich markup
    content = Text()
    
    # Phase indicator with spinner
    content.append(current_phase + " ", style="bold cyan")
    content.append(spinner_char, style="cyan")
    content.append(f" ({elapsed_str})\n", style="dim")
    
    # Current status/activity
    if current_status:
        content.append("Status: ", style="bold")
        content.append(current_status + "\n", style="yellow")
    
    # Current file being processed
    if current_file:
        # Truncate long file paths
        display_file = current_file if len(current_file) <= 120 else "..." + current_file[-117:]
        content.append("Processing: ", style="bold")
        content.append(display_file, style="dim")
    
    return Panel(
        content,
        title=Text.from_markup("[bold white]Status[/bold white]"),
        border_style="white",
        box=box.ROUNDED
    )

def render_inserted_panel() -> Panel:
    """Render the inserted records panel"""
    if not inserted_records:
        content = Text("No records inserted yet...", style="dim")
    else:
        content = Text()
        # Show last 15 records (most recent at the bottom)
        for record in inserted_records[-15:]:
            # Truncate very long SQL statements for display
            display_record = record if len(record) <= 120 else record[:117] + "..."
            content.append(display_record + "\n", style="green")
        if len(inserted_records) > 15:
            content.append(f"\n... and {len(inserted_records) - 15} more records", style="dim italic")
    
    title_text = Text.from_markup(f"[bold cyan]Inserted Records[/bold cyan] ({len(inserted_records)})")
    return Panel(
        content,
        title=title_text,
        border_style="cyan",
        box=box.ROUNDED
    )

def render_thumbnails_panel() -> Panel:
    """Render the created thumbnails panel"""
    if not created_thumbnails:
        content = Text("No thumbnails created yet...", style="dim")
    else:
        content = Text()
        # Show last 15 thumbnails
        for thumb in created_thumbnails[-15:]:
            # Truncate long paths for display
            display_thumb = thumb if len(thumb) <= 120 else thumb[:117] + "..."
            content.append(display_thumb + "\n", style="yellow")
        if len(created_thumbnails) > 15:
            content.append(f"\n... and {len(created_thumbnails) - 15} more thumbnails", style="dim italic")
    
    title_text = Text.from_markup(f"[bold yellow]Created Thumbnails[/bold yellow] ({len(created_thumbnails)})")
    return Panel(
        content,
        title=title_text,
        border_style="yellow",
        box=box.ROUNDED
    )

def render_summary_panel(total_inserted=0, total_thumbnails=0, update_sql="", delete_sql="") -> Panel:
    """Render the summary panel"""
    content = Text()
    content.append("Total Records Inserted: ", style="bold")
    content.append(f"{total_inserted}\n", style="bold green")
    content.append("Total Thumbnails Created: ", style="bold")
    content.append(f"{total_thumbnails}\n\n", style="bold yellow")
    
    if update_sql:
        content.append("Final Update Query:\n", style="bold cyan")
        # Truncate if too long, otherwise show full
        display_sql = update_sql if len(update_sql) <= 150 else update_sql[:147] + "..."
        content.append(display_sql + "\n\n", style="dim")
    
    if delete_sql:
        content.append("Duplicate Removal Query:\n", style="bold cyan")
        # Truncate if too long, otherwise show full
        display_sql = delete_sql if len(delete_sql) <= 150 else delete_sql[:147] + "..."
        content.append(display_sql + "\n", style="dim")
    
    title_text = Text.from_markup("[bold magenta]Final Summary[/bold magenta]")
    return Panel(
        content,
        title=title_text,
        border_style="magenta",
        box=box.ROUNDED
    )

# connection to local DB
db = MySQLdb.connect(host=settings.host, user=settings.user, passwd=settings.passwd, db=settings.db)
try:
    if sys.argv[1] == 'new':
        truncateDB = 'TRUNCATE `directories_list`'
        console.print(f"[dim]Executing: {truncateDB}[/dim]")
        mysql.executeMySQL(db, truncateDB)

        truncateDB = 'TRUNCATE `files_list`'
        console.print(f"[dim]Executing: {truncateDB}[/dim]")
        mysql.executeMySQL(db, truncateDB)

        truncateDB = 'TRUNCATE `text_list`'
        console.print(f"[dim]Executing: {truncateDB}[/dim]")
        mysql.executeMySQL(db, truncateDB)
        
except IndexError:
    console.print()
    console.print('[red]please provide a "new" or "update" as a flag for the indexer[/red]')
    console.print('[yellow]usage: python3 reindex.py new|update[/yellow]')
    console.print()
    exit()

# Initialize the layout
layout = create_display_layout()

def generate_layout():
    """Generate the current layout state"""
    layout["status"].update(render_status_panel())
    layout["inserted"].update(render_inserted_panel())
    layout["thumbnails"].update(render_thumbnails_panel())
    layout["summary"].update(render_summary_panel(
        total_inserted=len(inserted_records),
        total_thumbnails=len(created_thumbnails)
    ))
    return layout

# Start with Live display for indexing phase
current_phase = "Indexing Files"
current_status = "Scanning directories and indexing files..."
with Live(generate_layout(), refresh_per_second=8, screen=True) as live:
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
        
        # Update status with current folder
        current_status = f"Scanning: {thisFolder}"
        current_file = folder
        live.update(generate_layout())
            
        thisDirectoryID = 0
        try:
            thisDirectoryID = mysql.recordDirectoryFound(db, parentFolder, thisFolder)
        except:
            errorLog = open("errors.log", "a")
            errorLog.write("Could not check if directory found: \"" + parentFolder + "\" -- \"" + thisFolder + "\"\n")
            errorLog.close()  
        
        if thisDirectoryID > 0:
            for filename in files:
                with open(os.path.join(folder, filename), 'r') as fullPathFile:            

                    # build and execute query
                    fullPath = fullPathFile.name
                    current_file = fullPath
                    current_status = f"Processing: {os.path.basename(filename)}"
                    live.update(generate_layout())
                    
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
                            current_status = f"Analyzing: {os.path.basename(filename)}"
                            live.update(generate_layout())
                            
                            (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(fullPath)
                            mimeType = mimes.magicMimeTypes.file(fullPath)
                            baseName = re.split(r'\.([^.]*)$', os.path.basename(fullPath))
                            thisFileName, fileExtension = os.path.splitext(fullPath)
                            thisFileName = thisFileName
                            fileExtension = fileExtension
                            directoryName = os.path.dirname(fullPath)
                            fileName = os.path.basename(fullPath)

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
                                
                                current_status = f"Inserting: {os.path.basename(filename)}"
                                live.update(generate_layout())
                                
                                insertFileSQL = 'INSERT INTO `files_list` (`full_path`,`directory_name`,`base_name`,`ext`,`file_name`,`mime_type`,`size`,`date_accessed`,`date_modified`,`width`,`height`,`directory_id`) VALUES ("' + str(fullPath) + '","' + str(directoryName) + '","' + str(baseName[0]) + '","' + str(fileExtension) + '","' + str(fileName) + '","' + str(mimeType) + '","' + str(size) + '",FROM_UNIXTIME(' + str(atime) + '),FROM_UNIXTIME(' + str(mtime) + '),' + str(width) + ',' + str(height) + ',"' + str(thisDirectoryID) + '")'
                                mysql.executeMySQL(db, insertFileSQL)
                                # Track the inserted record (store full SQL for display)
                                inserted_records.append(insertFileSQL)
                                live.update(generate_layout())
                        except:
                            errorLog = open("errors.log", "a")
                            if 'insertFileSQL' in locals():
                                errorLog.write("Could not perform insert query: \"" + insertFileSQL + "\"\n")
                            errorLog.close()
            db.commit()
    
    # Update status after indexing is complete
    current_status = "Indexing complete!"
    current_file = ""
    live.update(generate_layout())

# get all files found and produce the preview thumbnails
thumbs.createFolderIfNotExists(settings.thumbnailsRoot)
allFiles = mysql.getAllRows(db, "SELECT * FROM `files_list`")

# Update phase for thumbnail creation
current_phase = "Creating Thumbnails"
current_status = "Generating thumbnails for images and videos..."

# Continue with Live display for thumbnail creation
with Live(generate_layout(), refresh_per_second=8, screen=True) as live:
    total_files = len(allFiles)
    processed_count = 0
    
    for file in allFiles:
        fileId,fullPath,directoryName,baseName,ext,fileName,mimeType,size,dateAccessed,dateModified,width,height,directoryId,thumbnail_exists = file
        
        if thumbnail_exists == 0:
            processed_count += 1
            current_file = fullPath
            current_status = f"Creating thumbnail {processed_count}/{total_files}: {os.path.basename(fileName)}"
            live.update(generate_layout())
            
            if mimeType in mimes.imageMimeTypes:
                try:
                    current_status = f"Generating image thumbnail: {os.path.basename(fileName)}"
                    live.update(generate_layout())
                    thumbs.createImageThumbnail(fileId, fullPath, settings.thumbnailSize, settings.thumbnailsRoot)
                    # Track the created thumbnail
                    display_path = fullPath if len(fullPath) <= 100 else fullPath[:97] + "..."
                    created_thumbnails.append(f"Image thumbnail created: {display_path}")
                    live.update(generate_layout())
                except:
                    errorLog = open("errors.log", "a")
                    errorLog.write("Could not generate thumbnail for IMAGE file: \"" +fullPath + "\"\n")
                    errorLog.close()              
            
            if mimeType in mimes.videoMimeTypes:
                try:
                    current_status = f"Generating video thumbnail: {os.path.basename(fileName)}"
                    live.update(generate_layout())
                    
                    # Check if video is small and create larger version if needed
                    if width > 0 and width < 400:
                        try:
                            current_status = f"Upscaling small video: {os.path.basename(fileName)}"
                            live.update(generate_layout())
                            # Create larger version with -LG suffix
                            createLargerVideoVersion(fullPath, width, height)
                        except Exception as e:
                            errorLog = open("errors.log", "a")
                            errorLog.write(f"Could not create larger video version for: {fullPath} - Error: {str(e)}\n")
                            errorLog.close()
                    
                    thumbs.createVideoThumbnail(fileId, fullPath, settings.thumbnailSize, settings.thumbnailsRoot)
                    # Track the created thumbnail
                    display_path = fullPath if len(fullPath) <= 100 else fullPath[:97] + "..."
                    created_thumbnails.append(f"Video thumbnail created: {display_path}")
                    live.update(generate_layout())
                except:
                    errorLog = open("errors.log", "a")
                    errorLog.write("Could not generate thumbnail for VIDEO file: " +fullPath + "\n")
                    errorLog.close()
    
    # Update status after thumbnail creation is complete
    current_status = "Thumbnail creation complete!"
    current_file = ""
    live.update(generate_layout())

# all thumbnails are set to exist after generating them                
allThumbsUpdated = 'UPDATE `files_list` SET `thumbnail_exists` = 1 WHERE TRUE;'
mysql.executeMySQL(db, allThumbsUpdated)
db.commit()

# remove duplicate rows that might have been inserted
removeDuplicateEntries = 'DELETE f1 FROM files_list f1 INNER JOIN (SELECT file_id, ROW_NUMBER() OVER (PARTITION BY full_path ORDER BY file_id) rownum FROM files_list) f2 ON f1.file_id = f2.file_id WHERE f2.rownum > 1;'
mysql.executeMySQL(db, removeDuplicateEntries)
db.commit()

# Display final summary
console.clear()
final_layout = create_display_layout()
final_layout["inserted"].update(render_inserted_panel())
final_layout["thumbnails"].update(render_thumbnails_panel())
final_layout["summary"].update(render_summary_panel(
    total_inserted=len(inserted_records),
    total_thumbnails=len(created_thumbnails),
    update_sql=allThumbsUpdated,
    delete_sql=removeDuplicateEntries
))
console.print(final_layout)
console.print()
