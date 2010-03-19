"""A document type which may contain directly uploaded images and attachments"""

__author__  = 'Martin Aspeli <optilude@gmx.net>'
__docformat__ = 'plaintext'

from zope.interface import implements

from AccessControl import ClassSecurityInfo

try:
  from Products.LinguaPlone.public import *
except ImportError:
  # No multilingual support
  from Products.Archetypes.public import *

from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.ATContentTypes.content.schemata import relatedItemsField

from zopen.plone.messageboard.interfaces import IComment
from zopen.plone.messageboard.config import PROJECTNAME

CommentSchema = BaseSchema.copy() + Schema((

    TextField('text',
        searchable=True,
        primary=True,
        default_output_type='text/html',
        default_content_type='text/x-web-intelligent',
        allowable_content_types=('text/x-web-intelligent',),
        ),

    relatedItemsField,

    ),)

class Comment(BaseContent):
    """A document which may contain directly uploaded images and attachments."""

    implements(INonStructuralFolder, IComment)

    # Standard content type setup
    portal_type = meta_type = 'Comment'
    schema = CommentSchema

    # Make sure we get title-to-id generation when an object is created
    _at_rename_after_creation = True

    def canSetDefaultPage(self):
        return False

    def Title(self):
        if hasattr(self, 'aq_parent'):
            return 'Re: ' + self.aq_parent.Title()
        else:
            return ''

    def getCommentAttaches(self):
        objects = self.getRelatedItems()
        files, images = [], []
        for obj in objects:
            if obj.getPortalTypeName() == 'Image':
                images.append(obj)
            elif obj.getPortalTypeName() == 'File':
                files.append(obj)
        return images, files

registerType(Comment, PROJECTNAME)
