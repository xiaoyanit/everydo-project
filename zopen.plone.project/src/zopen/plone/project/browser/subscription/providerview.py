from zope.interface import Interface, implements
from zope.component import getMultiAdapter, getUtility, adapts
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Acquisition import Explicit
from zope.contentprovider.interfaces import IContentProvider
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserView
from Products.CMFCore.utils import _checkPermission

# import logging; info = logging.getLogger("zopen.plone.subscription").info

from zopen.plone.subscription.interfaces import ISubscriptionManager
from zopen.plone.org.interfaces import IOrganizedEmployess

class SubscriptionProvider(Explicit):
    implements(IContentProvider)
    adapts(Interface, IDefaultBrowserLayer, IBrowserView)

    """ """

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.view = view
        self.context = context
        self.request = request

    def update(self):
        pass

    render = ZopeTwoPageTemplateFile('sub.pt')


    def hasSubscriptionForAuthenticatedMember(self):
        sm = ISubscriptionManager(self.context)
        return sm.hasSubscriptionForAuthenticatedMember()

    def getSubscribedMembers(self):

        sm = ISubscriptionManager(self.context)
        subscribers = sm.getSubscribedMembers()

        project = self.context.getProject()
        adapter = IOrganizedEmployess(project.teams)

        return adapter.caculateCompanyPeople(subscribers)

    def canModify(self):
        return _checkPermission('Modify portal content', self.context)

