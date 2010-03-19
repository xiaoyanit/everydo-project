from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts

from interfaces import ITeamManager

from zopen.plone.org.interfaces import ITeamFolderContent
from Products.CMFPlone.utils import _createObjectByType

from AccessControl import SecurityManagement, User
from Products.CMFCore.utils import getToolByName

class FolderConentsTeamManager:
    implements(ITeamManager)
    adapts(ITeamFolderContent)

    def __init__(self, context):
        self.context = context

    def getContentInfo(self):
        id = self.context.getId()
        url = self.context.absolute_url()
        return id,url 

    def getTeams(self):
        """ """
        folders = self.context.contentValues()
        cats = []

        for folder in folders:
            if not folder.getId().startswith('.'):
                cats.append({'id':folder.getId(),
                    'title':folder.title_or_id(),
                    'description':folder.Description()})
        return cats

    def getCategoryTitle(self, id):
        return getattr(self.context, id).Title() or id

    def addTeam(self,id, title, description=''):
        """ """
        _createObjectByType('Team', self.context.aq_inner, id=id, title=title,\
                            description=description)

    def delCategory(self, id):
        """ """

    def renameTeam(self, id, new_title, new_description=''):
        cat = getattr(self.context, id)
        cat.setTitle(new_title)
        cat.setDescription(new_description)
        cat.reindexObject

    def teamDeletable(self, id):
        cat = getattr(self.context, id)
        return not cat.objectIds()

    def getContentCategory(self, obj):
        cat = obj.aq_parent
        return {'id':cat.getId(), 'title':cat.Title()}

    def setContentCategory(self, obj, new_cat_id):
        cutted = obj.aq_inner.aq_parent.manage_cutObjects(obj.getId())
        new_cat = getattr(self.context, new_cat_id).aq_inner

        # 解决权限的问题
        originalSecurityManager = SecurityManagement.getSecurityManager()
        username = originalSecurityManager.getUser().getUserName()
        deliverUser = User.SimpleUser(username,'', ['Manager', 'Owner'], '')
        acl_users = obj.acl_users.aq_inner
        deliverUser = deliverUser.__of__(acl_users)
        SecurityManagement.newSecurityManager(None, deliverUser)

        new_cat.manage_pasteObjects(cutted)

        SecurityManagement.setSecurityManager(originalSecurityManager)
        return getattr(new_cat, obj.getId())

