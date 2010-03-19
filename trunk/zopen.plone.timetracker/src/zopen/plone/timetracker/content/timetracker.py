# encoding: utf-8
from zope.interface import implements
from zope.component import getUtility

from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import *
from Products.ATContentTypes.atct import ATContentTypeSchema

from zopen.plone.timetracker.interfaces import ITimeTrackerContent
from zopen.plone.timetracker.config import PROJECTNAME

class TimeTracker(BaseFolder):
    """  """
    
    implements(ITimeTrackerContent)
    schema = ATContentTypeSchema
    
    _at_rename_after_creation = True

    def getTimeTracker(self):
        return self

registerType(TimeTracker, PROJECTNAME)
