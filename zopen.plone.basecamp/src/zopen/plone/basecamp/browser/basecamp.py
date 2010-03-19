import Globals

from DateTime import DateTime
from zope.interface import implements
from zope.component import getMultiAdapter

from AccessControl import getSecurityManager
from Products.Five import BrowserView
from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName

from zopen.plone.project.permissions import ManageProject

import logging; info = logging.getLogger('zopen.plone.basecamp').info

class BasecampView(BrowserView):

    def __init__(self, context, request):
        super(BasecampView, self).__init__(context, request)
        portal_url = getToolByName(context, 'portal_url')

        self.portal_url = portal_url()
        self.portal  = portal_url.getPortalObject()

        self.cache_url = self.portal_url

        """
        if self.portal_url.startswith('https'):
            http = 'https://'
        else:
            http = 'http://'

        if self.portal_url.endswith('everydo.cn'):
            self.cache_url = http + 'cache.everydo.cn' 
        elif self.portal_url.endswith('everydo.com'):
            self.cache_url = http + 'cache.everydo.com'
        """

    @memoize
    def getCurrentProject(self):
        try:
            return self.context.getProject()
        except AttributeError:
            return None

    @memoize
    def getCurrentProjectId(self):
        project = self.getCurrentProject()
        return project and project.getId() or ''

    def showSiteSettings(self):
        return (not self.getCurrentProjectId()) and self.isSiteAdmin()

    def showProjectSettings(self):
        return self.isProjectAdmin()

    @memoize
    def isSiteAdmin(self):
        user = getSecurityManager().getUser()
        roles = user.getRolesInContext(self.portal)
        return ('Administrator' in roles) or ('Manager' in roles)

    @memoize
    def isProjectAdmin(self):
        project = self.getCurrentProject()
        if project:
            return getSecurityManager().checkPermission(ManageProject, project)
        else:
            return False

    @memoize
    def getCurrentProjectState(self):
        project = self.getCurrentProject()
        wftool = getToolByName(self.context, 'portal_workflow')
        return wftool.getInfoFor(project, 'review_state')

    @memoize
    def isClient(self):
        """ rewrite to my account page """
        user = getSecurityManager().getUser()
        userid = user.getUserName()
        ctool = getToolByName(self.context, 'portal_catalog')
        results = ctool.unrestrictedSearchResults(portal_type="Person", getId=userid)
        if results:
            emp = results[0].getObject()
            return emp.getPhysicalPath()[-2] != 'owner_company'
        else:
            return False

    def gotoMyAccountPage(self):
        """ rewrite to my account page """
        user = getSecurityManager().getUser()
        userid = user.getUserName()
        ctool = getToolByName(self.context, 'portal_catalog')
        results = ctool.unrestrictedSearchResults(portal_type="Person", getId=userid)
        if results:
            emp = results[0].getObject()
            return self.request.response.redirect(emp.absolute_url() + '/base_edit')
        else:
            return self.request.response.redirect(self.context.absolute_url() + '/personalize_form')

    def redirectToSiteSetting(self):
        """ site setting alias """
        self.request.response.redirect(self.context.absolute_url() +
                '/companies/@@prefs_site_companies')

    def redirectToProjectSetting(self):
        """ project setting alias """
        self.request.response.redirect(self.context.absolute_url() +
                '/teams/@@prefs_project_team')

    def getLatestActivity(self):

        pv = getMultiAdapter( (self.context, self.request), name=u'projectview')
        active_projects = pv.getActiveProjects()
        latest_activity = [] 
        portal_catalog = getToolByName(self.context, 'portal_catalog')

        for company_name in active_projects:
            for project in active_projects[company_name]:
                path = '/'.join(project.getPhysicalPath())

                query = {'path':path,
                         'portal_type':['Post', 'Comment', 'File', 'Image', 'Document'],
                         'sort_order' : 'reverse',
                         'sort_on':'modified',
                         'sort_limit':5}


                items = portal_catalog.searchResults(query)
                if items:
                    latest_activity.append((company_name, project, items))

        def cmp_first_item(x,y):
            return cmp(x[2][0].ModificationDate, y[2][0].ModificationDate)

        latest_activity.sort(cmp_first_item, reverse=1)
        return latest_activity[:5]

    def hasLogo(self, companyid):
        company = getattr(self.portal.companies, companyid)
        return company and company.getLogo()

    def getLogo(self, companyid):
        """ return the logo """
        company = getattr(self.portal.companies, companyid)
        if company:
            logo = company.getLogo()
            if logo:
                return logo.index_html(self.request, self.request.response)
        return None

    @memoize
    def hasPhoto(self, username):
        ctool = getToolByName(self.context, 'portal_catalog')
        r = ctool.unrestrictedSearchResults(portal_type='Person', getId=username)
        if r:
            person = r[0]._unrestrictedGetObject()
            photo = person.getPhoto()
            return photo

    def getPhoto(self, username):
        """ return user's photo """
        ctool = getToolByName(self.context, 'portal_catalog')
        r = ctool.unrestrictedSearchResults(portal_type='Person', getId=username)
        if r:
            person = r[0]._unrestrictedGetObject()
            photo = person.getPhoto()
            if photo:
                return photo.index_html(self.request, self.request.response)

    @memoize
    def getMemberName(self, responsor):
        mtool = getToolByName(self.context, 'portal_membership')
        mi = mtool.getMemberInfo(responsor)
        if mi:
            return mi['fullname'] or responsor

    @memoize
    def getGroupName(self, responsor):
        gtool = getToolByName(self.context, 'portal_groups')
        group = gtool.getGroupInfo(responsor)
        if group:
            return group['title'] or responsor
        else:
            return responsor

    def isLogoInWhiteBox(self, companyid):
        company = getattr(self.portal.companies, companyid)
        return company.getLogoInWhiteBox()

    def getCachedURL(self, resource_name):
        # return 'http://cache.everydo.com/'+resource_name

        # debug模式不用缓存
        if Globals.DevelopmentMode:
            return self.portal_url + '/' + resource_name
        else: 
            return self.cache_url + '/' + resource_name

    def getActionName(self,brain):
        """Get person action name"""
        if brain.portal_type in ['TodoItem','Milestone']:
            if brain.review_state == 'completed':
                return "Completed"
            else:
                if not brain.getResponsibleParty:
                    if brain.CreationDate == brain.ModificationDate:
                        return "Created"
                    else:
                        return "Modified"
                else:
                    return "Responsible"
        else:
            if brain.CreationDate == brain.ModificationDate:
                return "Created"
            else:
                return "Modified"

    @memoize
    def today(self):
        now = DateTime()
        return DateTime(now.year(), now.month(), now.day())

    def getExactTime(self, time, extract=0):
        """Get exact time"""
        #time = DateTime(time) 强制转换，会让时区为GMT+8的时间减少8小时
        time_date = DateTime(time.year(), time.month(), time.day())

        today = self.today()
        to_date = today - time_date

        if extract == 1:
            dow = today.dow()
            if to_date == 0:
                return 'Today'
            elif to_date == 1:
                return 'Yesterday'
            elif to_date == -1:
                return 'Tomorrow'
            elif to_date - dow == -5:
                return 'This week'
            elif to_date - dow == -12:
                return 'Next week'
            else:
                return time_date.strftime('%Y/%m/%d')
        elif extract == 2:
            if to_date == 0:
                return 'Today'
            elif to_date > 0:
                return 'late'
            else:
                return None
        else:
            if to_date == 0:
                return 'Today'
            elif to_date == 1:
                return 'Yesterday'
            else:
                return time_date.strftime('%Y-%m-%d')

    @memoize
    def was_locked(self, obj):
        lockable = getattr(obj.aq_explicit, 'wl_isLocked', None) is not None
        locked = lockable and obj.wl_isLocked()

        if not locked:
            return ""

        return locked

