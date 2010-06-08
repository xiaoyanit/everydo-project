from zope.interface import implements
from zope.component import getMultiAdapter

from Products.Five import BrowserView
from Products.Five.security import checkPermission
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from plone.memoize.instance import memoize

from Products.CMFCore.interfaces import ICatalogTool
from zopen.plone.basecamp.config import typesToShow

import logging; info = logging.getLogger('zopen.plone.basecamp').info

class Dashboard(BrowserView):

    dashboard_tempalte = ViewPageTemplateFile('dashboard.pt')
    # http://basecamphq.com/demos/welcome/
    create_first_project_template = ViewPageTemplateFile('firstproject.pt')

    def __call__(self):
        bv = self.context.unrestrictedTraverse('@@basecamp_view')
        isSiteAdmin = bv.isSiteAdmin()
        if bv.isClient() and not checkPermission('zopen.project.AddProject', self.context):
            bv = self.context.unrestrictedTraverse('@@projectview')
            projects = bv.getActiveProjects()

            if len(projects) == 1 and len(projects.values()[0]) == 1:  # 只有一个项目就不显示什么了
                self.request.response.redirect(projects.values()[0][0].absolute_url())
                return 
            else: # 没有项目
                return self.dashboard_tempalte()

        if isSiteAdmin and self.context.projects.objectCount() == 0:
            return self.create_first_project_template()
        else:
            return self.dashboard_tempalte()

    @memoize
    def showDashboard(self):
        bv = self.context.unrestrictedTraverse('@@basecamp_view')
        isSiteAdmin = bv.isSiteAdmin()
        if bv.isClient() and not isSiteAdmin:
            bv = self.context.unrestrictedTraverse('@@projectview')
            projects = bv.getActiveProjects()

            if len(projects) == 1 and len(projects.values()[0]) == 1:  # 只有一个项目就不显示什么了
                return False
        return True

    def getLatestActivity(self):
        pv = getMultiAdapter( (self.context, self.request), name=u'projectview')
        active_projects = pv.getActiveProjects()
        latest_activity = [] 
        project_counts = sum([len(p) for p in active_projects.values()])

        if project_counts > 3:
            sort_limit = 5
        elif project_counts == 3:
            sort_limit = 8
        elif project_counts == 2:
            sort_limit = 12
        elif project_counts == 1:
            sort_limit = 20

        portal_catalog = getToolByName(self.context, 'portal_catalog')
        for company_name in active_projects:
            for project in active_projects[company_name]:
                path = '/'.join(project.getPhysicalPath())

                query = {'path':path,
                         'portal_type':typesToShow,
                         'sort_order' : 'reverse',
                         'sort_on':'modified',
                         'sort_limit':sort_limit}

                items = portal_catalog.searchResults(query)
                if items:
                    latest_activity.append((company_name, project, items))

        def cmp_first_item(x,y):
            return cmp(x[2][0].ModificationDate, y[2][0].ModificationDate)

        latest_activity.sort(cmp_first_item, reverse=1)

        return latest_activity[:5]


    def getResponsiblePartyTitle(self, item):
        mtool = getToolByName(self.context, 'portal_membership')
        responsor = (item.portal_type != 'Discussion Item' and item.getResponsibleParty) or  item.Creator
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

from plone.app.kss.plonekssview import PloneKSSView

class BasecampKssView(PloneKSSView):

    def redirctContextUrl(self):

        url = self.context.absolute_url()
        self.getCommandSet('zopen').redirect(url=url)
        return self.render()
    
