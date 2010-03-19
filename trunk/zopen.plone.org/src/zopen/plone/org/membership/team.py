from zope.interface import implements
from zope.component import adapts

from Products.CMFCore.utils import getToolByName

from Products.membrane.interfaces import IGroup
from Products.membrane.interfaces import IMembraneUserAuth
from Products.membrane.interfaces import ICategoryMapper

from Products.membrane.config import ACTIVE_STATUS_CATEGORY
from Products.membrane.config import TOOLNAME as MEMBRANE_TOOL
from Products.membrane.utils import generateCategorySetIdForType

from zopen.plone.org.interfaces import ITeam, ITeamContent

class Team(object):
    """Provide team information.
    """
    implements(ITeam)
    adapts(ITeamContent)

    def __init__(self, context):
        self.context = context
        
    @property
    def id(self):
        return self.context.getId()

    def getMembers(self):
        memberIds = self.context.getMembers()
        mt = getToolByName(self.context, 'portal_membership')
        members = [mt.getMemberById(id) for id in memberIds]
        return [m for m in members if m]

class Group(object):
    """Allow team to act as groups for contained employees
    """
    implements(IGroup)
    adapts(ITeamContent)
    
    def __init__(self, context):
        self.context = context
        
    def Title(self):
        return self.context.Title()
    
    def getRoles(self):
        """Get roles for this team-group.
        
        Return an empty list of roles if the team is in a workflow state
        that is not active in membrane_tool.
        """
        mb = getToolByName(self.context, MEMBRANE_TOOL)
        wf = getToolByName(self.context, 'portal_workflow')
        
        reviewState = wf.getInfoFor(self.context, 'review_state')
        wfmapper = ICategoryMapper(mb)
        categories = generateCategorySetIdForType(self.context.portal_type)
        if wfmapper.isInCategory(categories, ACTIVE_STATUS_CATEGORY, reviewState):
            return self.context.getRoles()
        else:
            return ()
    
    def getGroupId(self):
        # XXX This is only for basecamp site only now!
        pp = self.context.aq_inner.aq_parent.aq_parent
        if hasattr(pp, 'getPortalTypeName'):
            if pp.getPortalTypeName() == 'Plone Site':
                return self.context.getId()
            else: # if pp.getPortalTypeName() == 'Project':
                return '%s-%s' % (self.context.getId(), pp.getId())

        return '%s-%s' % (self.context.getId(), self.context.UID())

    def getGroupMembers(self):
        return [m.getId() for m in self.context.getMembers()]

