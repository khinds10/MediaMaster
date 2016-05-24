#!/usr/bin/python
# Media Master Mime Types listing
# @author khinds
# @license http://opensource.org/licenses/gpl-license.php GNU Public License
import magic

# load magic mime type reader
magicMimeTypes=magic.open(magic.MAGIC_MIME)
magicMimeTypes.load()

# list of image mimeTypes
imageMimeTypes = ['image/gif; charset=binary',
                  'image/jpeg; charset=binary',
                  'image/png; charset=binary',
                  'image/x-ms-bmp; charset=binary']
                  
# list of video mimeTypes
videoMimeTypes = ['application/ogg; charset=binary',
                  'application/vnd.rn-realmedia; charset=binary',
                  'audio/mpeg; charset=binary',
                  'video/mp4; charset=binary',
                  'video/mpeg; charset=binary',
                  'video/quicktime; charset=binary',
                  'video/webm; charset=binary',
                  'video/x-flv; charset=binary',
                  'video/x-ms-asf; charset=binary',
                  'video/x-msvideo; charset=binary']