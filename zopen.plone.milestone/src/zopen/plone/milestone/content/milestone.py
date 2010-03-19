# encoding: utf-8
from zope.interface import implements
from zope.component import getUtility

from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import *

from zopen.plone.milestone.interfaces import IMilestoneContent
from zopen.plone.milestone.config import PROJECTNAME

MilestoneSchema = BaseSchema + Schema((

    DateTimeField('deadline',
        accessor='end',
        required=1,
        ),

    IntegerField('progress',
        default=0,
        ),

    StringField('responsibleParty',
        index="FieldIndex:schema",
        widget=SelectionWidget(),
    ),

    BooleanField('notify'),

    ReferenceField('relatedItems',
        relationship = 'relatesTo',
        multiValued = True,
        isMetadata = True,
        ),

    ))

class Milestone(BaseContent):
    """ Milestone """
    
    security = ClassSecurityInfo()
    implements(IMilestoneContent)
    
    # Note: ExtensibleSchemaSupport means this may get expanded.
    schema = MilestoneSchema
    _at_rename_after_creation = True


    def addRelatedItem(self, uid):
        ri = self.getRawRelatedItems()
        if uid not in ri:
            self.setRelatedItems( tuple(ri) + (uid, ))

    def removeRelatedItem(self, uid):
        ri = self.getRawRelatedItems()
        self.setRelatedItems( [i for i in ri if i != uid] )

    def setResponsibleParty(self, value):
        self.getField('responsibleParty').set(self, value)

        userids = self.users_with_local_role('Responsor')
        owners = self.users_with_local_role('Owner')
        if userids:
            self.manage_delLocalRoles(userids)
        if value:
            if value in owners:
                self.manage_setLocalRoles(value, ['Responsor', 'Owner'])
            else:
                self.manage_setLocalRoles(value, ['Responsor'])
        else:
            # XXX some hack for project teamfolder
            if hasattr(self, 'getProject'):
                project = self.getProject()
                self.manage_setLocalRoles('teams-' + project.getId(), ['Responsor'])
        self.reindexObjectSecurity()

    def getHours(self):
        return self.getProgress() or 0

registerType(Milestone, PROJECTNAME)

