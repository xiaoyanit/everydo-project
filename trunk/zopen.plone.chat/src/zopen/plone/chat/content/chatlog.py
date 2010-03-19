from Products.Archetypes.atapi import *

from Products.ATContentTypes.content.schemata import relatedItemsField

from zopen.plone.chat.config import PROJECTNAME

ChatLogSchema = BaseSchema.copy() + Schema((

    TextField('text',
        searchable=True,
        primary=True,
        default_output_type='text/html',
        default_content_type='text/html',
        allowable_content_types=('text/html',),
        ),

    relatedItemsField,

    ),)

class ChatLog(BaseContent):
    """PloneChat class"""

    schema = ChatLogSchema

    def index_html(self):
        """ aaa """
        brefs = self.getBRefs()
        if brefs:
            chatroom = brefs[0]
            return chatroom.PloneChat_logs_view()
        else:
            return self.getText()

registerType(ChatLog, PROJECTNAME)
