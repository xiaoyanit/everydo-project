from plone.app.kss.plonekssview import PloneKSSView
try:
    from plone.locking.interfaces import ILockable
    HAS_LOCKING = True
except ImportError:
    HAS_LOCKING = False
from Products.CMFCore.PortalFolder import PortalFolderBase

from zope.component import getUtility
from Products.CMFCore.interfaces import IDiscussionTool

from AccessControl import getSecurityManager, User, SecurityManagement

from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
_ = MessageFactory('zopen.widgets')


class KssView(PloneKSSView):

    def kss_obj_delete(self, selector='.kssDeletionRegion'):

        obj = self.context.aq_inner
        if obj.getPortalTypeName() == 'Discussion Item':
            parent = obj.inReplyTo()
            if parent is not None:
                portal_discussion = getUtility(IDiscussionTool)
                talkback = portal_discussion.getDiscussionFor(parent)
            else:
                talkback = obj.aq_parent

            # remove the discussion item
            talkback.deleteReply( str(obj.getId()) )

        else:
            # 被锁定时先解锁
            if HAS_LOCKING:
                lockable = ILockable(obj)
                if lockable.locked():
                    lockable.unlock()

            parent = obj.aq_parent
            # archetypes的manage_delObjects会检查每个item的删除权限
            originalSecurityManager = SecurityManagement.getSecurityManager()
            SecurityManagement.newSecurityManager(None, User.SimpleUser('admin','',('Manager',), ''))
            parent.manage_delObjects(str(obj.getId()))
            SecurityManagement.setSecurityManager(originalSecurityManager)

        if selector.startswith('redirect2'):
            # 跳转到某个地址
            # 需要定义 # class="kssattr-delSelector-redirect2http://test.everydo.com"
            redirect2url = selector[len('redirect2'):]
            self.getCommandSet('zopen').redirect(url=redirect2url)
        else:
            core = self.getCommandSet('core')
            effects = self.getCommandSet('effects')
            selector = core.getParentNodeSelector(selector)
            # effects.effect(selector, 'fade')

            core.deleteNode(selector)

        self.getCommandSet('plone').issuePortalMessage(
                translate(_(u'Deleted.'), default="Deleted.", context=self.request), 
                translate(_(u'Info'), default="Info", context=self.request))
        return self.render()

