#!/usr/bin/python
# Media Master Mime Types listing
# @author khinds
# @license http://opensource.org/licenses/gpl-license.php GNU Public License
import magic

# load magic mime type reader
magicMimeTypes=magic.open(magic.MAGIC_MIME)
magicMimeTypes.load()

# list of image mimeTypes
imageMimeTypes = ['image/gif',
                  'image/jpeg',
                  'image/png',
                  'image/x-ms-bmp']
                  
# list of video mimeTypes
videoMimeTypes = ['application/ogg',
                  'application/vnd.rn-realmedia',
                  'audio/mpeg',
                  'video/mp4',
                  'video/mpeg',
                  'video/quicktime',
                  'video/webm',
                  'video/x-flv',
                  'video/x-ms-asf',
                  'video/x-msvideo']
