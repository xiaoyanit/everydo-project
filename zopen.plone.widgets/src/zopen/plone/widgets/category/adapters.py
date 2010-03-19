from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts

from interfaces import ICategoryManager

from Products.CMFCore.interfaces import IFolderish
from Products.CMFPlone.utils import _createObjectByType

from AccessControl import SecurityManagement, User
from Products.CMFCore.utils import getToolByName, _checkPermission

class FolderConentsCategoryManager:
    implements(ICategoryManager)
    adapts(IFolderish)

    def __init__(self, context):
        self.context = context

    def getContentInfo(self):
        id = self.context.getId()
        url = self.context.absolute_url()
        return id,url 

    def getCategories(self, addable=False):
        """ """
        folders = self.context.listFolderContents()
        cats = []

        for folder in folders:
            if not folder.getId().startswith('.'):
                if not addable or _checkPermission('Add portal content', folder):
                    cats.append({'id':folder.getId(), 'title':folder.title_or_id()})
        return cats

    def getCategoryTitle(self, id):
        return getattr(self.context, id).Title() or id

    def addCategory(self,id, title):
        """ """
        _createObjectByType('Large Plone Folder', self.context, id=id, title=title)

    def delCategory(self, id):
        """ """

    def renameCategory(self, id, new_title):
        cat = getattr(self.context, id)
        cat.setTitle(new_title)

    def categoryDeletable(self, id):
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

