#-*- coding:utf-8 -*-
import os.path
from zope.interface import implements
from zope.component import adapts
from zope import event

from zope.lifecycleevent import ObjectModifiedEvent

from ZPublisher.HTTPRequest import FileUpload
from OFS.Image import File

#from Products.CMFPlone.interfaces import IPloneTool
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import shasattr

from interfaces import IFileManager
from utils import getMaxAttachmentSize, getQuota

class FileManager(object):
    implements(IFileManager)

    def validateAddAttachment(self, file_upload):
        def FileSize(file):
            if hasattr(file, 'size'):
                size=file.size
            elif hasattr(file, 'tell'):
                file.seek(0, 2)
                size=file.tell()
                file.seek(0)
            else:
                try:
                    size=len(file)
                except TypeError:
                    size=0

            return size

        if FileSize(file_upload) > getMaxAttachmentSize():
            raise ValueError, "Single file exceeded"

    def addAttachment(self, context, file_upload):
        return self.addFile(context, file_upload, is_attachment=True)

    def getFilerepos(self, context):
        project = context.getProject()
        return project.files

    def addFile(self, context, file_upload, is_attachment=False):
        # XXX 由于文件被tramline干掉了，这里的file
        # size可能不正确，此处校验是否仍然有效?
        self.validateAddAttachment(file_upload)

        def findUniqueId(id):

            contextIds = [i.lower() for i in context.objectIds()]
            
            if id.lower() not in contextIds:
                return id

            dotDelimited = id.split('.')

            ext = dotDelimited[-1]
            name = '.'.join(dotDelimited[:-1])

            idx = 0
            while(name.lower() + '.' + str(idx) + '.' + ext.lower()) in contextIds:
                idx += 1

            return(name + '.' + str(idx) + '.' + ext)

        def _add(file, id, filename):
            """ """
            suffix = os.path.splitext(filename)[-1].lower()
            if suffix in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tif',\
            '.tiff', '.dib', '.jpe', '.jfif',]:
                type_name = 'Image'
                mutator = 'setImage'
            else:
                type_name = 'File'
                mutator = 'setFile'
            if is_attachment:
                type_name += 'Attachment'
            new_id = context.invokeFactory(type_name, id)
            attachment = getattr(context, new_id)
            attachment.setTitle(filename)

            getattr(attachment, mutator)(file)

            attachment.unmarkCreationFlag()
            if shasattr(attachment, 'at_post_create_script'):
                attachment.at_post_create_script()

            attachment.reindexObject()

            return attachment

        if file_upload and isinstance(file_upload, FileUpload):

            # Make sure we have a unique file name
            fileName = file_upload.filename

            file_id = ''

            if fileName:
                fileName = fileName.split('/')[-1]
                fileName = fileName.split('\\')[-1]
                fileName = fileName.split(':')[-1]

                plone_utils = getToolByName(context, 'plone_utils')
                file_id = fileName
                # 避免id以_开始
                if file_id[0] == '_':
                    file_id = '-'+file_id

                # TODO should be commented
                #把文件名改为拼音
                file_id = plone_utils.normalizeString(file_id)

            file_id = findUniqueId(file_id)

            #attachment = File(file_id, fileName, file_upload)

            attachment = _add(file_upload, file_id, fileName) 
            event.notify(ObjectModifiedEvent(attachment))
            return attachment

FileManager = FileManager()
