#-*- coding:utf-8 -*-
import os
from zope.contenttype import guess_content_type
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.debug import log
from Products.Archetypes.utils import contentDispositionHeader
from types import UnicodeType
from Products.Archetypes.event import ObjectEditedEvent
from zope import event

def download(self, instance, REQUEST=None, RESPONSE=None):
    """Kicks download.

    Writes data including file name and content type to RESPONSE
    """
    file = self.get(instance)
    if not REQUEST:
        REQUEST = instance.REQUEST
    if not RESPONSE:
        RESPONSE = REQUEST.RESPONSE
    filename = self.getFilename(instance)
    if not filename:
        filename = instance.Title()
    
    if filename is not None:
        if REQUEST.HTTP_USER_AGENT.find('MSIE') != -1:
            if type(filename) is UnicodeType:
                filename = filename.encode('gb18030')
            else:
                filename = unicode(filename).encode('gb18030')
            header_value = contentDispositionHeader('attachment', 'gb18030', filename=filename)
        else:
            header_value = contentDispositionHeader('attachment', instance.getCharset(), filename=filename)

        RESPONSE.setHeader("Content-disposition", header_value)
    if hasattr(instance.aq_base, 'tramline_size'):
        archiveName = REQUEST.get('archive_name', '')
        zpath = '/'.join(instance.getPhysicalPath())
        if archiveName:
            # 下载中间的存档版本
            RESPONSE.setHeader('Content-Type', self.getContentType(instance))
            RESPONSE.setHeader("tramline_file", "ok")
            return zpath + ':archive::' + archiveName
        else:
            RESPONSE.setHeader('Content-Type', self.getContentType(instance))
            RESPONSE.setHeader("tramline_file", "ok")
            return zpath
    return file.index_html(REQUEST, RESPONSE)

from Products.Archetypes.Field import FileField, ImageField
FileField.download = download

def index_html(self, REQUEST=None, RESPONSE=None):
    """Make it directly viewable when entering the objects URL
    """
    if REQUEST is None:
        REQUEST = self.REQUEST
    if RESPONSE is None:
        RESPONSE = REQUEST.RESPONSE

    filename = self.getFilename()
    if not filename:
        filename = self.Title()
    
    if filename is not None:
        if REQUEST.HTTP_USER_AGENT.find('MSIE') != -1:
            if type(filename) is UnicodeType:
                filename = filename.encode('gb18030')
            else:
                filename = unicode(filename).encode('gb18030')
            header_value = contentDispositionHeader('attachment', 'gb18030', filename=filename)
        else:
            header_value = contentDispositionHeader('attachment', self.getCharset(), filename=filename)

        RESPONSE.setHeader("Content-disposition", header_value)
    if hasattr(self, 'tramline_size'):
        RESPONSE.setHeader('Content-Type', self.getContentType())
        if not RESPONSE.getHeader("tramline_file"):
            RESPONSE.setHeader("tramline_file", "ok")
            return '/'.join(self.getPhysicalPath())
        else:
            return

    field = self.getPrimaryField()
    data  = field.getAccessor(self)(REQUEST=REQUEST, RESPONSE=RESPONSE)
    if data:
        return data.index_html(REQUEST, RESPONSE)

from Products.ATContentTypes.content.base import ATCTFileContent
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.image import ATImage
ATCTFileContent.index_html = index_html

FileField.orig_get_size = FileField.get_size
ImageField.orig_get_size = ImageField.get_size
def get_size(self, instance):
    if hasattr(instance.aq_base, 'tramline_size'):
        return instance.tramline_size
    else:
        return self.orig_get_size(instance)
    
FileField.get_size = get_size
ImageField.get_size = get_size

ATImage.orig_get_size = ATImage.get_size
def new_get_size(self):
    if hasattr(self,  'tramline_size'):
        return self.tramline_size
    else:
        return self.orig_get_size()

ATImage.get_size = new_get_size

def getTotalSize(self):
    currentSize = self.get_size()

    if self.getPortalTypeName() not in ['Image', 'File', 'Document']:
        return currentSize

    rep_tool = getToolByName(self, 'portal_repository')
    history = rep_tool.getHistory(self, countPurged=False)
    fileTotalSize = currentSize
    if len(history) > 0:
        for vdata in history:
            fileTotalSize += vdata.metadata.get('byte_size', 0)
    return fileTotalSize

from Products.CMFCore.DynamicType import DynamicType
DynamicType.getTotalSize = getTotalSize

ATImage.orig__bobo_traverse__ = ATImage.__bobo_traverse__
def __bobo_traverse__(self, REQUEST, name):
    """Transparent access to image scales
    """
    if hasattr(self,  'tramline_size'):
        if name.startswith('image_') and name not in ['image_view', 'image_view_fullscreen']:
            response = self.REQUEST.RESPONSE
            response.setHeader('Content-Type', self.getContentType())
            response.setHeader("tramline_file", "ok")
            response.write( '/'.join(self.getPhysicalPath()) + ':cache:imagescales:' + name)
            return self 

        elif name == 'image':
            return self
        else:
            return self.orig__bobo_traverse__(REQUEST, name)
    else:
        return self.orig__bobo_traverse__(REQUEST, name)

ATImage.__bobo_traverse__ = __bobo_traverse__

ATFile.o_setFile = ATFile.setFile
def setFile(self, value, **kwargs):
    request = self.REQUEST
    tramlined = request.get('HTTP_X_TRAMLINED', '')
    if not tramlined or (value == ''):
        self.o_setFile(value, **kwargs)
    else:
        fileinfo = value.read().split('|', 1)
        filepath = fileinfo[0]
        filesize = fileinfo[-1]
        filename = value.filename
        mimetype, enc = guess_content_type(filename)

        self.tramline_size = int(filesize)
        if self.tramline_size > 32000000:
            raise "上传的文件大小超过 30M 限制，上传失败！"
        self.setContentType(mimetype)


        #用于修订IE的文件带路径问题
        title = filename.split("\\")[-1]
        self.setFilename(title)
        self.setTitle(title)

        # 是否只上传1个文件？
        tramline_ok = request.response.getHeader('tramline_ok') or ''

        # 不是第一文件了，需要用分隔符合并起来
        if tramline_ok: 
            tramline_ok += '|'
        tramline_ok += '%s:%s:%s' % (filepath,\
                   '/'.join(self.getPhysicalPath()), '')

        event.notify(ObjectEditedEvent(self))
        request.response.setHeader('tramline_ok', tramline_ok)

ATFile.setFile = setFile

ATImage.o_setImage = ATImage.setImage
def setImage(self, value, refresh_exif=True, **kwargs):
    request = self.REQUEST
    tramlined = request.get('HTTP_X_TRAMLINED', '')
    if not tramlined or (value == ''):
        self.o_setImage(value, refresh_exif, **kwargs)
    else:
        fileinfo = value.read().split('|', 1)
        filepath = fileinfo[0]
        filesize = fileinfo[-1]
        filename = value.filename
        mimetype, enc = guess_content_type(filename)

        self.tramline_size = int(filesize)
        if self.tramline_size > 32000000:
            raise "上传的文件大小超过 30M 限制，上传失败！"
        self.setContentType(mimetype)
        #用于修订IE的文件带路径问题
        #不能用setFilename，它会失效，因为通过tramline后，图片为空，
        #ImageField不会生成空的图片
        title = filename.split("\\")[-1]
        self.setTitle(title)

        tramline_ok = request.response.getHeader('tramline_ok') or ''
        if tramline_ok: 
            tramline_ok += '|'
        tramline_ok += '%s:%s:%s' % (filepath,\
                   '/'.join(self.getPhysicalPath()), 's')
        event.notify(ObjectEditedEvent(self))
        request.response.setHeader('tramline_ok', tramline_ok)

ATImage.setImage = setImage

