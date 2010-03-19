# -*- coding: UTF-8 -*-

import random
import calendar
import copy

from DateTime import DateTime
from Products.Five import BrowserView
from zope.component import adapts
from zope.interface import Interface, implements, directlyProvides
from zope.contentprovider.interfaces import IContentProvider
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserView

from zope.contentprovider.interfaces import ITALNamespaceData
import zope.schema

from Acquisition import Explicit
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

import logging; info = logging.getLogger('zopen.plone.milestones').info

class IMilestoneSelectionProvider(IContentProvider):
    selected = zope.schema.TextLine(title=u'ids of the selected')

directlyProvides(IMilestoneSelectionProvider, ITALNamespaceData)

class MilestoneSelectionProvider(Explicit):
    implements(IMilestoneSelectionProvider)
    adapts(Interface, IDefaultBrowserLayer, IBrowserView)
    selected = []

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.view = view
        self.context = context
        self.request = request

    def update(self):
        # XXX 不可重用了！！
        project = self.context.getProject()
        path = '/'.join(project.getPhysicalPath())

        query = {'path' : path,
                 'portal_type': 'Milestone',
                 'sort_on' : 'end',
                }

        portal_catalog = getToolByName(self.context, 'portal_catalog')
        results = portal_catalog.searchResults(query)
        self.milestones = results
        if not results:
            raise 'no milstones'

    def render(self):
        option = """<option value="%s" %s>%s</option>"""
        options = [option % (b.UID, 
                     self.selected and (b.UID in self.selected) and 'selected="selected"' or '',
                     (b.review_state == 'completed' and '(已完成)' or '') +  b.Title) 
                     for b in self.milestones] 

        options.insert(0, option % ('',  '', '-------'))
        return ''.join(options)

