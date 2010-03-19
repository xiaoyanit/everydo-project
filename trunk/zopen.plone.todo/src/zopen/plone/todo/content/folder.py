from zope.interface import implements
from Products.Archetypes.atapi import *
from Products.ATContentTypes.atct import ATContentTypeSchema
from zopen.plone.todo.config import PROJECTNAME
from zopen.plone.todo.interfaces import ITodoFolderContent

class TodoFolder(OrderedBaseFolder):
    """ a todo list """

    implements(ITodoFolderContent)

    schema = ATContentTypeSchema

registerType(TodoFolder, PROJECTNAME)
