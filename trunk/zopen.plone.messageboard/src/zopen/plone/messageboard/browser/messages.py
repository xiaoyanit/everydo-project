from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from Products.CMFEditions.interfaces.IRepository import IRepositoryTool
from AccessControl import Unauthorized

from zopen.plone.widgets.category.interfaces import ICategoryManager

import logging; info = logging.getLogger('zopen.plone.messageboard').info

class MessagesView(BrowserView):

    def getTimelinedResults(self, category=None, group_by='modified'):

        if category == None:
           path = '/'.join(self.context.getPhysicalPath())
        else:
           path = '/'.join(self.context.getPhysicalPath()) + '/' + category

        query = {'path':path,
                 'portal_type': 'Message',
                 'sort_order' : 'reverse',
                 'sort_on':group_by,
                 'sort_limit':200}

        portal_catalog = getToolByName(self.context, 'portal_catalog')
        results = portal_catalog.searchResults(query)

        return results

    def categoryTitle(self):
        category = self.request.get('category', '')
        return category and ICategoryManager(self.context).getCategoryTitle(category)

