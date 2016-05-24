#!/usr/bin/python
# Media Master Thumbnail Handler
# @author khinds
# @license http://opensource.org/licenses/gpl-license.php GNU Public License
import Image, os, thumbs
from ffvideo import VideoStream

def createFolderIfNotExists(folderName):
    if not os.path.exists(folderName):
        os.makedirs(folderName)

def getOutPutFolderName(fileId, thumbnailsRoot):
    return thumbnailsRoot + "/" + str(int(fileId / 1000))

def probe(videoFilePath):
    ''' Give a json from ffprobe command line

    @videoFilePath : The absolute (full) path of the video file, string.
    '''
    command = ["ffprobe",
            "-loglevel",  "quiet",
            "-print_format", "json",
             "-show_format",
             "-show_streams",
             videoFilePath
             ]
    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = pipe.communicate()
    return json.loads(out)

def getVideoDuration(videoFilePath):
    ''' Video's duration in seconds, return a float number'''
    _json = probe(videoFilePath)
    if 'format' in _json:
        if 'duration' in _json['format']:
            return float(_json['format']['duration'])
    if 'streams' in _json:
        # commonly stream 0 is the video
        for s in _json['streams']:
            if 'duration' in s:
                return float(s['duration'])
    raise float(0)

def createImageThumbnail(fileId, fullPath, thumbnailSize, thumbnailsRoot):
    try:
        im = Image.open(fullPath)
        im.thumbnail(thumbnailSize)
        thumbs.createFolderIfNotExists(getOutPutFolderName(fileId, thumbnailsRoot))
        im.save(getOutPutFolderName(fileId, thumbnailsRoot) + "/" + str(fileId) +".jpg", "JPEG")
    except:
        print "cannot create thumbnail for", fullPath

def createVideoThumbnail(fileId, fullPath, thumbnailSize, thumbnailsRoot):
    videoImage = VideoStream(fullPath).get_frame_at_sec(int(getVideoDuration(fullPath) / 2)).image()
    videoImage.save('videoPreviewTemp.jpg')
    createImageThumbnail(fileId, 'videoPreviewTemp.jpg')