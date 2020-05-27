#!/usr/bin/python
# Media Master Thumbnail Handler
# @author khinds
# @license http://opensource.org/licenses/gpl-license.php GNU Public License
import os, subprocess, json, cv2
from PIL import Image
import includes.thumbs as thumbs

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
    im = Image.open(fullPath)
    im = im.convert('RGB')
    im.thumbnail(thumbnailSize)
    thumbs.createFolderIfNotExists(getOutPutFolderName(fileId, thumbnailsRoot))
    im.save(getOutPutFolderName(fileId, thumbnailsRoot) + "/" + str(fileId) +".jpg", "JPEG")

def video_to_frames(video_filename):
    """Extract frames from video"""
    cap = cv2.VideoCapture(video_filename)
    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    frames = []
    if cap.isOpened() and video_length > 0:
        frame_ids = [0]
        if video_length >= 2:
            frame_ids = [round(video_length * 0.5)]
        count = 0
        success, image = cap.read()
        while success:
            if count in frame_ids:
                frames.append(image)
            success, image = cap.read()
            count += 1
    return frames

def image_to_thumbs(img):
    """Create thumbs from image"""
    height, width, channels = img.shape
    thumbs = {"original": img}
    sizes = [256]
    for size in sizes:
        if (width >= size):
            r = (size + 0.0) / width
            max_size = (size, int(height * r))
            thumbs[str(size)] = cv2.resize(img, max_size, interpolation=cv2.INTER_AREA)
    return thumbs

def createVideoThumbnail(fileId, fullPath, thumbnailSize, thumbnailsRoot):  
  """generate and save thumbnail show 50% through the video"""
  frames = video_to_frames(fullPath)
  print("Generate and save thumbs")
  for i in range(len(frames)):
    thumb = image_to_thumbs(frames[i])
    for k, v in thumb.items():
      cv2.imwrite('videoPreviewTemp.jpg', v)
    createImageThumbnail(fileId, 'videoPreviewTemp.jpg', thumbnailSize, thumbnailsRoot)
