"""A document type which may contain directly uploaded images and attachments"""

__author__  = 'panjy <panjy@zopen.cn>'
__docformat__ = 'plaintext'

from zope.interface import implements

from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.ATContentTypes.content.schemata import relatedItemsField

from zopen.plone.messageboard.interfaces import IMessage
from zopen.plone.messageboard.config import PROJECTNAME

MessageSchema = BaseSchema.copy() + Schema((

    TextField('text',
        searchable=True,
        primary=True,
        default_output_type='text/html',
        default_content_type='text/x-web-intelligent',
        allowable_content_types=('text/x-web-intelligent',),
        ),

    relatedItemsField,

    ),)

class Message(OrderedBaseFolder):
    """A document which may contain directly uploaded images and attachments."""

    implements(INonStructuralFolder, IMessage)

    # Standard content type setup
    portal_type = meta_type = 'Message'
    schema = MessageSchema

    # Make sure we get title-to-id generation when an object is created
    _at_rename_after_creation = True

    def canSetDefaultPage(self):
        return False

    def getAttachedImagesAndFiles(self):
        objects = self.getRelatedItems()
        files, images = [], []
        for obj in objects:
            if obj.getPortalTypeName() == 'Image':
                images.append(obj)
            elif obj.getPortalTypeName() == 'File':
                files.append(obj)
        return images, files

    def getRelatedMilestones(self):
        ctool = getToolByName(self, 'portal_catalog')
        results = ctool(  portal_type='Milestone', getRawRelatedItems = self.UID()) 
        return results

    def getRelatedMilestoneUIDs(self):
        return [item.UID for item in self.getRelatedMilestones()]

registerType(Message, PROJECTNAME)

