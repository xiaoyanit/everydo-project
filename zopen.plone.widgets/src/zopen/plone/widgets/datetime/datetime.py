from zope.interface import ( implements, Interface)

from zope.component import ( getUtility, adapts)

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserView

from zope.contentprovider.interfaces import IContentProvider

from Acquisition import Explicit

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

import zope.schema

class IMonthProvider(IContentProvider):
    """ """
    month = zope.schema.Int(title=u'the current month')

from zope.contentprovider.interfaces import ITALNamespaceData
zope.interface.directlyProvides(IMonthProvider, ITALNamespaceData)

class MonthProvider(Explicit):
    implements(IMonthProvider)
    adapts(Interface, IDefaultBrowserLayer, IBrowserView)

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.view = view
        self.context = context
        self.request = request

    # From IContentProvider
    def update(self):
        pass

    render = ZopeTwoPageTemplateFile("month.pt")
