# encoding: utf-8
from zope.interface import implements
from zope.component import getUtility

from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import *
from Products.ATContentTypes.atct import ATContentTypeSchema

from zopen.plone.milestone.interfaces import IMilestoneFolderContent
from zopen.plone.milestone.config import PROJECTNAME

class MilestoneFolder(BaseFolder):
    """ Milestone """
    
    implements(IMilestoneFolderContent)
    schema = ATContentTypeSchema
    
    _at_rename_after_creation = True

registerType(MilestoneFolder, PROJECTNAME)
