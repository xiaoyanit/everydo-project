from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts

from interfaces import ICommentsManager

from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import getToolByName

class CMFCommentsManager:
    implements(ICommentsManager)
    adapts(IContentish)

    def __init__(self, context):
        self.context = context

    def getComments(self):
        ctool = getToolByName(self.context, 'portal_catalog')
        brains = ctool(portal_type="Discussion Item", sort_on="created",
                sort_order="reversed",
                path='/'.join(self.context.getPhysicalPath()))
        return [b.getObject() for b in brains]

    def getComment(self, id):
        dtool = getToolByName(self.context, 'portal_discussion')
        tb = dtool.getDiscussionFor(self.context)
        return tb.getReply(id)

    def addComment(self,text,attachement=[]):
        """ """
        dtool = getToolByName(self.context, 'portal_discussion')
        mtool = getToolByName(self.context, 'portal_membership')
        tb = dtool.getDiscussionFor(self.context)
        creator = mtool.getAuthenticatedMember().getUserName()
        title = 'Re: ' + self.context.Title()
        id = tb.createReply(title=title, text=text, Creator=creator)
        comment = tb.getReply(id)
        des = unicode(text)[:80] + (len(unicode(text)) < 80 and '...' or '')
        comment.setDescription(des)
        comment.reindexObject()
        return comment

    def attachable(self):
        return False
