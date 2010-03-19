from zope.interface import Interface, implements, directlyProvides
from zope.component import getMultiAdapter, getUtility, adapts
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Acquisition import Explicit
from zope.contentprovider.interfaces import IContentProvider
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserView

# import logging; info = logging.getLogger("zopen.plone.subscription").info

from zopen.plone.subscription.interfaces import ISubscriptionManager
from zopen.plone.org.interfaces import IOrganizedEmployess

from zope.contentprovider.interfaces import ITALNamespaceData
import zope.schema

class IPersonSelectionProvider(IContentProvider):
    """ """
    name = zope.schema.Text(title=u'name of the seletion input')
    selected = zope.schema.TextLine(title=u'ids of the selected')

directlyProvides(IPersonSelectionProvider, ITALNamespaceData)

class SelectionBase(Explicit):
    implements(IPersonSelectionProvider)
    adapts(Interface, IDefaultBrowserLayer, IBrowserView)

    """ """

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.view = view
        self.context = context
        self.request = request

    def update(self):
        pass

    render = ZopeTwoPageTemplateFile('multiselection.pt')

    def getMembers(self):
        project = self.context.getProject()
        adapter = IOrganizedEmployess(project.teams)

        return adapter.get_all_companies_and_people()

class MultiSelectionProvider(SelectionBase):
    render = ZopeTwoPageTemplateFile('multiselection.pt')

class XSelectionProvider(SelectionBase):
    """ select person or UI """
    render = ZopeTwoPageTemplateFile('xselection.pt')
    selected = []

class SelectionProvider(SelectionBase):
    render = ZopeTwoPageTemplateFile('selection.pt')
    selected = []

    def getMembers(self):
        project = self.context.getProject()
        adapter = IOrganizedEmployess(project.teams)
        return adapter.get_all_people()

class ResponsibleSelectionProvider(SelectionBase):
    render = ZopeTwoPageTemplateFile('responsibleselection.pt')
    selected= []

    def update(self):
        mtool = getToolByName(self.context, 'portal_membership')
        mid = mtool.getAuthenticatedMember().getId()

        ctool = getToolByName(self.context, 'portal_catalog')
        r = ctool(portal_type='Person', getId=mid)
        if r:
            person = r[0].getObject()
            company = person.aq_parent

            self.company = {'title':company.Title(), 'id':company.getId()}
            self.person = {'title':person.Title(), 'id':mid}
        else:
            self.company = {'title':'---', 'id':''}
            self.person = {'title':mid, 'id':mid}

