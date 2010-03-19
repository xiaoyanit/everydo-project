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

from interfaces import ICategoryManager

class ICategorySelectionProvider(IContentProvider):
    """ """

    name = zope.schema.Text(title=u'context url when deletion')
    category = zope.schema.Text(title=u'context url when deletion')
    is_template_setting = zope.schema.Bool(title=u'used for templates setting or not', default=False)
    can_define_category = zope.schema.Bool(title=u'can define category or not', default=True)
    cat_context = zope.schema.Field()

zope.interface.directlyProvides(ICategorySelectionProvider, ITALNamespaceData)

class CategorySelectionProvider(Explicit):
    implements(ICategorySelectionProvider)
    adapts(Interface, IDefaultBrowserLayer, IBrowserView)

    name = u'category'

    actionbaseurl = ''

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
        self.categories = ICategoryManager(context).getCategories(addable=True)
        self.content_info = ICategoryManager(context).getContentInfo()
        

    render = ZopeTwoPageTemplateFile('selection.pt')

class CategoryListProvider(Explicit):
    implements(ICategorySelectionProvider)
    adapts(Interface, IDefaultBrowserLayer, IBrowserView)

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
        self.categories = ICategoryManager(context).getCategories()
        self.content_info = ICategoryManager(context).getContentInfo()
        self.canModify = _checkPermission('Modify portal content', context)

    render = ZopeTwoPageTemplateFile('list.pt')

    def categoryDeletable(self, id):
        context = self.context
        if self.cat_context:
            context = self.cat_context
            self.actionbaseurl = context.absolute_url() + '/'
        return ICategoryManager(context).categoryDeletable(id)

