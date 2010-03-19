#-*- coding:utf-8 -*-


from zope.interface import Interface
from zope.interface import implements

from zope.component import getUtility
from zope.component import adapts

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserView

from zope.contentprovider.interfaces import IContentProvider

from Acquisition import Explicit
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.contentprovider.interfaces import ITALNamespaceData
import zope.schema
from Products.CMFCore.utils import _checkPermission


from interfaces import ITeamManager

class ITeamSelectionProvider(IContentProvider):
    name = zope.schema.Text(title=u'context url when deletion')
    category = zope.schema.Text(title=u'context url when deletion')
    is_template_setting = zope.schema.Text(title=u'used for templates setting or not')
    cat_context = zope.schema.Field()

zope.interface.directlyProvides(ITeamSelectionProvider, ITALNamespaceData)


class TeamListProvider(Explicit):
    implements(ITeamSelectionProvider)
    adapts(Interface, IDefaultBrowserLayer, IBrowserView)

    is_template_setting = False

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.view = view
        self.context = context
        self.request = request

    # From IContentProvider
    def update(self):
        context = self.context
        if self.cat_context:
            context = self.cat_context
            self.actionbaseurl = context.absolute_url() + '/'
        self.teams= ITeamManager(context).getTeams()
        self.content_info = ITeamManager(context).getContentInfo()
        self.canModify = _checkPermission('Modify portal content', context)

    render = ZopeTwoPageTemplateFile('list.pt')


    def teamDeletable(self, id):
        context = self.context
        if self.cat_context:
            context = self.cat_context
            self.actionbaseurl = context.absolute_url() + '/'
        return ITeamManager(context).teamDeletable(id)

