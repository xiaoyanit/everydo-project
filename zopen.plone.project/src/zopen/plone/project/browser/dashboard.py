from Products.Five import BrowserView
from zope.interface import implements
from zope.component import getUtility
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize

from zopen.plone.project.config import typesToShow
import logging; info = logging.getLogger('zopen.plone.project').info

class DashboardView(BrowserView):

    def getTimelinedResults(self, group_by='modified'):
        
        path = '/'.join(self.context.getPhysicalPath())

        portal_catalog = getToolByName(self.context, 'portal_catalog')
        brains = portal_catalog.searchResults({
                    'path'       : path,
                    'portal_type': typesToShow,
                },
                sort_order = 'reverse',
                sort_on    = group_by,
                )

        return brains

        dates_result = {}
        for b in brains:
            try:
                obj = b.getObject()
            except AttributeError:
                continue

            modified = b.modified
            day = DateTime(
                    modified.year(),
                    modified.month(),
                    modified.day())
            if not dates_result.has_key(day):
                dates_result[day] = []

            data = {}
            data['getId'] = b.getId
            data['getIcon'] = b.getIcon
            data['Description'] = b.Description
            data['modified'] = b.modified

            data['is_private'] = b.review_state == 'private'
            data['getPath'] = b.getPath()

            # 获取作者信息
            mtool = getToolByName(self.context, 'portal_membership')
            author = mtool.getMemberInfo(b.Creator)
            data['author'] = author and author['fullname'] or b.Creator

            data['obj'] = obj
            data['pretty_title_or_id'] = obj.pretty_title_or_id()
            cat = obj.aq_parent
            dates_result[day].append(data)

        return dates_result

    @memoize
    def getResponsiblePartyTitle(self, responsor):
        mtool = getToolByName(self.context, 'portal_membership')
        mi = mtool.getMemberInfo(responsor)
        if mi:
            return mi['fullname'] or responsor

        # a group?
        else:
            gtool = getToolByName(self.context, 'portal_groups')
            group = gtool.getGroupInfo(responsor)
            if group:
                return group['title'] or responsor
            else:
                return responsor

