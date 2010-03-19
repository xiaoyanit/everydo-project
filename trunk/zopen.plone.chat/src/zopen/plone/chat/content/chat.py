from Products.PloneChat.content.PloneChat import PloneChat
from Products.Archetypes.atapi import *
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.atct import ATContentTypeSchema 
from Products.ATContentTypes.content.schemata import relatedItemsField
from DateTime import DateTime

from zopen.plone.widgets.category.interfaces import ICategoryManager
from zopen.plone.chat.config import PROJECTNAME

PloneChat.schema.addField(relatedItemsField.copy())
PloneChat.schema = ATContentTypeSchema + PloneChat.schema

class Chat(BaseFolder, PloneChat):
    """PloneChat class"""

    schema = PloneChat.schema

    security = ClassSecurityInfo()

    def _createChatLog(self):
        wftool = getToolByName(self, 'portal_workflow')
        isPrivate = wftool.getInfoFor(self, 'review_state') == 'private'

        project = self.getProject()
        files = project.files.aq_inner

        if not hasattr(files, 'chatlogs'):
            cm = ICategoryManager(files)
            cm.addCategory('chatlogs', '讨论记录')

        id = self.generateUniqueId() + '.log'
        files.chatlogs.invokeFactory('ChatLog', id)
        chatlog = getattr(files.chatlogs, id)
        # self.setRelatedItems([chatlog])

        if isPrivate:
            wftool.doActionFor(chatlog, 'hide')

        self.reindexObject(['getRawRealtedItems'])
        return chatlog

    security.declareProtected('Modify portal content', 'clearLogs')
    def clearLogs(self):
        """ asdf """
        return PloneChat.clearLogs(self)

    security.declareProtected('Modify portal content', 'newSession')
    def newSession(self):
        """ asdfa """
        logs = self.getLogs() 
        if not logs:
            return

        result = self.PloneChat_logs_view()
        chatlog = self._createChatLog()
        chatlog.setTitle(logs[0]['date'] + ' - ' + logs[-1]['date'])
        chatlog.setDescription(self.getRawDescription())
        chatlog.setText(result, mimetype='text/html')
        chatlog.setRelatedItems(self.getRawRelatedItems())
        chatlog.reindexObject()

        self.setRelatedItems([])
        self.reindexObject(['getRawRealtedItems'])
        self.clearLogs()

registerType(Chat, PROJECTNAME)

