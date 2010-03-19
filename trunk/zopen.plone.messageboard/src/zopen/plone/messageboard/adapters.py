import random

from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts

from zope.component import getUtility
from Products.CMFCore.interfaces import IDiscussionTool
from Products.CMFPlone.utils import _createObjectByType, getToolByName
from zopen.plone.filerepos.interfaces import IFileManager

from zopen.plone.widgets.comments.interfaces import ICommentsManager
from interfaces import IMessage, IDisableAttach

class MessageCommentsManager:
    implements(ICommentsManager)
    adapts(IMessage)

    def __init__(self, context):
        self.context = context

    def getComments(self):
        return self.context.contentValues()

        #ctool = getToolByName(self.context, 'portal_catalog')
        #brains = ctool(portal_type="Comment", sort_on="created",
        #        sort_order="reversed",
        #        path='/'.join(self.context.getPhysicalPath()))
        #return [b.getObject() for b in brains]

    def getComment(self, id):
        return self.context.get(id)

    def addComment(self,text,attachements=[]):
        """ """
        id = str(random.randrange(100000, 999999))
        while id in self.context:
            id = str(random.randrange(100000, 999999))

        _createObjectByType('Comment', self.context, id)
        c = getattr(self.context, id)
        c.setText(text, mimetype='text/x-web-intelligent')
        des = unicode(text)[:80] + (len(unicode(text)) < 80 and '...' or '')
        c.setDescription(des)
        c.reindexObject()

        wf_tool = getToolByName(self.context, 'portal_workflow')
        review_state = wf_tool.getInfoFor(self.context, 'review_state')
        private = review_state == 'private'

        file_manager = getUtility(IFileManager, 'file_manager')
        filerepos = file_manager.getFilerepos(self.context)
        files = []

        for att in attachements:
            file_cat = getattr(filerepos, att.category)
            the_file = file_manager.addFile(file_cat, att.file)

            if the_file is not None:
                files.append(the_file)
                if private:
                    wf_tool.doActionFor(the_file, 'hide')

        if files:
            c.setRelatedItems(files)

        return c

    def attachable(self):
        return not IDisableAttach.providedBy(self.context)

