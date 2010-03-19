from zope.interface import (
        implements, Interface)
from zope.component import (
        adapts, getUtility)
from zope.component import getMultiAdapter
from DateTime import DateTime
from Acquisition import Explicit
from zope.contentprovider.interfaces import IContentProvider
from zope.publisher.interfaces.browser import (
        IDefaultBrowserLayer, IBrowserView)
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName

class MilestonesProvider(Explicit):
    implements(IContentProvider)
    adapts(Interface, IDefaultBrowserLayer, IBrowserView)

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.view = view
        self.context = context
        self.request = request

    # From IContentProvider
    def update(self):
        catalog_tool = getToolByName(self.context, 'portal_catalog')
        portal_path = getToolByName(self.context, 'portal_url').getPortalPath()
        path = '/'.join(self.context.getPhysicalPath())

        # at portal, so we show only active projects
        if portal_path == path:
            pv = getMultiAdapter( (self.context, self.request), name=u'projectview')
            path = pv.getActiveProjectPaths()

        now = DateTime()
        self.today = DateTime(now.year(), now.month(), now.day())
        self.NameDays = []
        day = self.today
        for i in range(7):
            self.NameDays.append(day.aDay())
            day += 1

        query1 ={ 'portal_type' : 'Milestone',
                  'end'         : {"query":[self.today-1], "range":"max"},
                  'review_state': 'active',
                  'path': path,
                 }
        self.late_milestones = catalog_tool.searchResults(
                query1,
                sort_on='end',
                )

        query2 ={ 'portal_type' : 'Milestone',
                  'review_state': 'active',
                  'end'         : {"query":[self.today,
                                            self.today+14], "range":"minmax"},
                  'path': path,
                }
        brains = catalog_tool.searchResults(
                query2,
                sort_on='end',
                )

        self.next_14_days_cal = [[None] * 7, [None] * 7]
        self.next_14_days_milestones = {}
        day = self.today
        for i in range(2):
            for j in range(7):
                self.next_14_days_cal[i][j] = day.day()
                day += 1

        self.next_14_days_cal[0][0] = "TODAY"
        day = self.today + 1
        self.next_14_days_cal[0][1] = "%s %s" % (day.aMonth(), day.day())

        for b in brains:
            diff = int(b.end - self.today)
            weekno = diff / 7
            if weekno > 1:
                continue

            self.next_14_days_milestones.setdefault(weekno, {}).setdefault(diff % 7,
                    []).append(b)

    render = ZopeTwoPageTemplateFile('milestones.pt')
