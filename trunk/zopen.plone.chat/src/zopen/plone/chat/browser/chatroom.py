import random
import posixpath
from Products.Five import BrowserView
from zope.interface import implements
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from zopen.plone.filerepos.interfaces import IFileManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import logging; info = logging.getLogger('zopen.todo').info

class ChatView(BrowserView):
    uploaded_template = ViewPageTemplateFile('uploaded.pt')

    def isPrivate(self):
        wf_tool = getToolByName(self.context, 'portal_workflow')
        return wf_tool.getInfoFor(self.context, 'review_state') == 'private'

    def getUploadedFiles(self):
        uids = self.context.getRawRelatedItems()
        ctool = getToolByName(self.context, 'portal_catalog')
        return ctool(UID = uids, sort_on='created', sort_order='reverse')[:5]

    def uploadFile(self, upload):
        chatroom = self.context.aq_inner
        wf_tool = getToolByName(chatroom, 'portal_workflow')
        private = wf_tool.getInfoFor(chatroom, 'review_state') == 'private'
        file_manager = getUtility(IFileManager, 'file_manager')
        filerepos = file_manager.getFilerepos(chatroom)

        file_cat = getattr(filerepos, upload.category)
        the_file = file_manager.addFile(file_cat, upload.file)

        if the_file is not None:
            if private:
                wf_tool.doActionFor(the_file, 'hide')
            files = chatroom.getRawRelatedItems()
            files.append(the_file.UID())
            
            #chatlog = chatroom.getChatLog()
            chatroom.setRelatedItems(files)
            #chatlog.reindexObject(['getRawRelatedItems'])
            return self.uploaded_template(file = the_file)
        else:
            return ''

    def getAllSessionsURL(self):
        project = self.context.getProject()
        if hasattr(project.files, 'chatlogs'):
            return '%s?category=chatlogs' % project.files.absolute_url()

