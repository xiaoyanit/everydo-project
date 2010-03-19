from zope.interface import implements

from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName

from Products.Archetypes.atapi import *

from Products.membrane.interfaces import IPropertiesProvider

from Products.borg.interfaces import IEmployeeLocator
from Products.borg.interfaces import IValidRolesProvider

from Products.borg.config import INVALID_ROLES
from Products.borg import permissions

from zopen.plone.org.interfaces import ITeamContent
from zopen.plone.org.config import PROJECTNAME


TeamSchema = BaseSchema.copy() + Schema((

    # Can't use 'roles' because 'validate_roles' exists :-(
    LinesField('roles_',
        accessor='getRoles',
        mutator='setRoles',
        edit_accessor='getRawRoles',
        languageIndependent=True,
        vocabulary='getRoleSet',
        multiValued=1,
        write_permission=permissions.ManageUsers,
        widget=MultiSelectionWidget(
            label=u'Roles',
            description=u"The roles all employees in this team will have",
            ),
        ),

    ReferenceField('members',
        relationship='participatesInTeam',
        allowed_types=('Person',),
        multiValued=1,
        languageIndependent=True,
        widget=ReferenceWidget(
            label=u'Members',
            description=u"Members in this team",
            ),
        ),

    ))

TeamSchema['title'].user_property = True
TeamSchema['description'].user_property = True

class Team(BaseContent):
    """A borg team.
    
    team is collection of members.
    """
    
    implements(ITeamContent, IPropertiesProvider)
    
    security = ClassSecurityInfo()
        
    # Note: ExtensibleSchemaSupport means this may get expanded.
    schema = TeamSchema
    _at_rename_after_creation = True

    #
    # Vocabulary methods
    #
    
    security.declarePrivate('getRoleSet')
    def getRoleSet(self):
        """Get the roles vocabulary to use
        """
        provider = IValidRolesProvider(self)
        return provider.availableRoles

    def setMembers(self, value):
        self.getField('members').set(self, value)

        # reset teamsfolder too
        self.aq_parent.recaculateMembers()
        
registerType(Team, PROJECTNAME)

