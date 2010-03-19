from zope.interface import Interface
from zope.interface import implements

from zope.component import getUtility
from zope.component import adapts
from zope.contentprovider.interfaces import ITALNamespaceData
import zope.schema

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserView

from Acquisition import Explicit
from Products.CMFPlone import utils
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import _checkPermission

delete_template = ViewPageTemplateFile('deletion.pt')

class IHrefText(Interface):
    obj = zope.schema.Field()
    deletion_href_base = zope.schema.Text(title=u'context url when deletion')
    show_mode = zope.schema.Text(title=u'how to show: img/text')

zope.interface.directlyProvides(IHrefText, ITALNamespaceData)

class DeletionIconProvider(Explicit):
    implements(IHrefText)
    adapts(Interface, IDefaultBrowserLayer, IBrowserView)

    obj = ''
    deletion_href_base = u'http://asfasdf/asdfas/a'
    show_mode = 'img'

    del_temp = ViewPageTemplateFile('deletion.pt')

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.view = view
        self.context = context
        self.request = request

    # From IContentProvider

    def update(self):
        self.visible = self.obj and _checkPermission('Delete objects', self.obj)
        if self.visible:
            self.deletion_href_base = self.obj.absolute_url()

    render = delete_template
