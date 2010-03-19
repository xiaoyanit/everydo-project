# encoding: utf-8
from zope.interface import implements
from zope.component import getUtility

from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import *

from zopen.plone.timetracker.interfaces import ITimeLogContent
from zopen.plone.timetracker.config import PROJECTNAME

TimeLogSchema = BaseSchema + Schema((

    DateTimeField('date',
        required=1,
        ),

    StringField('responsibleParty',
        widget=SelectionWidget(),
    ),

    FloatField('hours'),

    ReferenceField('relatedItems',
        relationship = 'relatesTo',
        multiValued = True,
        isMetadata = True,
        ),
    ))

class TimeLog(BaseContent):
    """ timelog """
    
    security = ClassSecurityInfo()
    implements(ITimeLogContent)

    # Note: ExtensibleSchemaSupport means this may get expanded.
    schema = TimeLogSchema
    _at_rename_after_creation = True

    def Date(self):
        return self.getDate()

registerType(TimeLog, PROJECTNAME)
