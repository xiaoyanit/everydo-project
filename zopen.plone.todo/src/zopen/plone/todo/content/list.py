from zope.interface import implements
from Products.Archetypes.atapi import *
from zopen.plone.todo.config import PROJECTNAME
from zopen.plone.todo.interfaces import ITodoListContent
from Products.CMFCore.utils import getToolByName

TodoListSchema = BaseSchema + Schema((

    BooleanField('tracked',),

    # BooleanField('notify'),

    ))

class TodoList(OrderedBaseFolder):
    """ a todo list """
    implements(ITodoListContent)

    schema = TodoListSchema

    def getRelatedMilestones(self):
        ctool = getToolByName(self, 'portal_catalog')
        results = ctool(  portal_type='Milestone', getRawRelatedItems = self.UID()) 
        return results

    def getRelatedMilestoneUIDs(self):
        return [item.UID for item in self.getRelatedMilestones()]

registerType(TodoList, PROJECTNAME)
