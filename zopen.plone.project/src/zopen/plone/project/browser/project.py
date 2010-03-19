# -*- coding: UTF-8 -*-

from zope.interface import implements
from zope.component.interfaces import ObjectEvent
from zope.component import adapts, getUtility
from zope.event import notify

from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.SecurityManagement import newSecurityManager

#from Products.CMFPlone.interfaces import IPloneTool
from plone.memoize.instance import memoize

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('zopen.project')

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

from zopen.plone.project.interfaces import IProjectCreatedEvent

from zopen.plone.org.interfaces import IOrgInstance


# import logging; info = logging.getLogger('zopen.plone.org').info

def getAvailableCompanies(context):
    ctool = getToolByName(context, 'portal_catalog')
    companies = ctool(portal_type='OrganizationUnit')

    return [(company.UID, company.Title) for company in companies]

class ProjectView(BrowserView):

    def _getGroupedProjects(self, status, path='/projects'):
        portal_url = getToolByName(self.context, 'portal_url')
        path = portal_url.getPortalPath() + path
        portal_catalog = getToolByName(self.context, 'portal_catalog')

        projects = portal_catalog(portal_type="Project",
               review_state=status, path=path,)

        company_projects={}
        for project in projects:
            obj = project.getObject()
            company = obj.getCompany()
            company_title = company and company.Title() or 'No Company!!!'
            projects = company_projects.get(company_title, [])
            projects.append(obj)
            company_projects[company_title] = projects
        return company_projects

    @memoize
    def getActiveProjects(self):
        ap = self._getGroupedProjects('active')

        def getTitle(o): return o.Title()

        for projects in ap.values():
            projects.sort(key=getTitle)

        return ap

    @memoize
    def getActiveProjectPaths(self):
        projects = []
        for company_projects in self.getActiveProjects().values():
            projects.extend(company_projects)
        return ['/'.join(project.getPhysicalPath()) for project in projects]

    def getOnholdProjects(self):
        return self._getGroupedProjects('onhold')

    def getArchivedProjects(self):
        return self._getGroupedProjects('archived')

    def hasArchivedProject(self):
        return self.context.portal_catalog(portal_type="Project",
                                review_state='archived')

    def gotoMessages(self):
        self.request.response.redirect(self.context.absolute_url() + '/messages')

    def gotoTodos(self):
        self.request.response.redirect(self.context.absolute_url() + '/todos')

    def gotoMilestones(self):
        self.request.response.redirect(self.context.absolute_url() + '/milestones')

class CreateProjectForm(BrowserView):

    create_project_template = ViewPageTemplateFile("create_project_form.pt")

    def __call__(self):
        form = self.request.form
        if form.has_key('form.submitted'):
            # TODO validation
            projectname = form.get('projectname', '')
            
            company_uid = form.get('company', '')
            newcompany = form.get('newcompany','')
            enable = form.get('enable', [])

            portal = getToolByName(self.context, 'portal_url').getPortalObject()
            basecamp_org = IOrgInstance(portal)

            if not (company_uid or newcompany):
                company_uid = basecamp_org.getOwnerCompany().UID()
            elif not company_uid:
                c = basecamp_org.createCompany(newcompany)
                company_uid = c.UID()

            if projectname == '':
                #plone_utils = getUtility(IPloneTool)
                plone_utils = getToolByName(self.context, 'plone_utils')
                msg = _(u'Please input project name.')
                plone_utils.addPortalMessage(msg, 'error')
                return self.request.response.redirect(self.context.absolute_url()+'/create_project_form')
            project = self.createProject(projectname, company_uid, enable)

            return self.request.response.redirect(project.absolute_url())
        else:
            return self.create_project_template()

    def getAvailableCompanies(self):
        return getAvailableCompanies(self.context)

    def createProject(self, title, company_uid, enable):
        # 以admin的身份创建项目
        acl_users = self.context.getPhysicalRoot().acl_users
        admin = acl_users.getUserById('admin')
        if not hasattr(admin, 'aq_base'):
            admin = admin.__of__(acl_users)
        sm = getSecurityManager()
        newSecurityManager(None, admin)

        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        basecamp_org = IOrgInstance(portal)

        id = basecamp_org.randomId()
        while self.context.has_key(id):
            id = basecamp_org.randomId()

        _createObjectByType('Project', self.context, id)
        project = getattr(self.context, id)

        project.setTitle(title)
        project.setCompany(company_uid)

        # notify project creation event
        notify(ProjectCreatedEvent(project))
        # enable project features
       # for id in ['messages', 'todos', 'milestones',\
        #            'writeboards','time','chatroom', 'files']:
         #   exclude = id not in enable
          #  obj = getattr(project.aq_base, id, None)
           # if obj is not None:
            #    obj.setExcludeFromNav(exclude)

        project.reindexObject()
        setSecurityManager(sm)

        # 让当前用户进入admin组
        userid = getToolByName(self.context, 'portal_membership').getAuthenticatedMember().getMemberId()
        results = getToolByName(self.context, 'portal_catalog').unrestrictedSearchResults(portal_type="Person", getId=userid)
        if results:
            person = results[0].getObject()
            project.teams.projectmanagers.setMembers([person.UID()])

        return project

class DeleteProject(BrowserView):
    def __call__(self):
        currentPassword = self.request.get('currentPassword')
        mtool = getToolByName(self.context, 'portal_membership')
        portal_url = getToolByName(self.context, 'portal_url')()

        if not mtool.testCurrentPassword(currentPassword):
            msg = _(u'Password is invalid')
            #plone_utils = getUtility(IPloneTool)
            plone_utils = getToolByName(self.context, 'plone_utils')
            plone_utils.addPortalMessage(msg, 'info')
            return self.request.response.redirect(self.context.absolute_url()+'/prefs_project_settings')

        projectname = self.context.getId()
        parent_folder = self.context.aq_inner.aq_parent
        parent_folder.manage_delObjects(projectname)

        self.request.response.redirect(portal_url)

class ProjectSettings(BrowserView):
    project_settings_template = ViewPageTemplateFile("prefs_project_settings.pt")

    def __call__(self):
        form = self.request.form
        project = self.context.aq_inner

        if not form.has_key('form.submitted'):
            return self.project_settings_template()
        else:
            title = form.get('title')
            if title:
                project.setTitle(title)
            description = form.get('description', '')
            project.setDescription(description, mimetype="text/html")
            company = form.get('company', '')
            if company:
                project.setCompany(company)
            projectState = form.get('projectState', '')
            if projectState:
                project.setNewProjectState(projectState)
            projectSubject = form.get('projectSubject', '')
            if projectSubject:
                subject = projectSubject.split(' ')
                self.context.setSubject(tuple(subject))
            project.reindexObject()

            layout = form.get('startPage', '')
            if layout:
                project.setLayout(layout)
            self.request.response.redirect(project.absolute_url())

            features = form.get('features', [])
            for id in ['messages', 'todos', 'milestones',\
                    'writeboards','time','chatroom', 'files']:
                exclude = id not in features
                obj = getattr(project.aq_base, id, None)
                if obj is not None:
                    obj.setExcludeFromNav(exclude)


    def getCompanyUID(self):
        return self.context.getRawCompany()

    def getAvailableCompanies(self):
        return getAvailableCompanies(self.context)

class ProjectCreatedEvent(ObjectEvent):
    """ repository path changed event """

    implements(IProjectCreatedEvent)

from plone.app.kss.plonekssview import PloneKSSView
from kss.core import force_unicode
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile


from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
_ = MessageFactory('zopen.project')

class ProjectKssSettings(PloneKSSView):

    def addTag(self):
        form = self.request.form
        project = self.context.aq_inner

        portal_url = getToolByName(self.context, 'portal_url')
        path = portal_url.getPortalPath()
        portal_catalog = getToolByName(self.context, 'portal_catalog') 

        projectSubject = form.get('projectSubject', '')
        if projectSubject:
            subject = self.context.Subject()
            subject_new = list(subject) + [projectSubject]
            self.context.setSubject(tuple(subject_new))

        project.reindexObject()

        ## <a class="tag_for">Subject</a>[2]

        tag_html_1 = ''
        tag_html_2 = ''
        for i in self.context.Subject():
            tag_html_1 += "<a href=\"#\" class=\"tag_for\">%s</a> " % (i)
            tag_html_2 += "<span class=\"kssDeleteTag kssattr-tag-%s\" style=\"padding-right: 10px;\"><span>%s</span> <img alt=\"Delete\" src=\"/++resource++trash.gif\" class=\"delimage\"/></span>" % (i, i)

        content_1 = "<span id=\"current_project_tags\" class=\"hideme EVtags TGtags\">%s</span>"%(tag_html_1) 
        content_1 = force_unicode(content_1, 'utf')
        content_2 = force_unicode(tag_html_2, 'utf')

        ksscore = self.getCommandSet('core')
        selector1 = ksscore.getSelector('css', '#current_project_tags') 
        selector2 = ksscore.getSelector('css', '.edit_tags') 
        ksscore.replaceHTML(selector1, content_1)
        ksscore.replaceInnerHTML(selector2, content_2)

        ksscore.toggleClass(ksscore.getSelector('css','.submit'),'hideme')
        ksszopen=self.getCommandSet('zopen')
        ksszopen.clear('#add_tags')
        ksscore.focus('#add_tags')
        return self.render()

    def getAllProjectTags(self):

        portal_url = getToolByName(self.context, 'portal_url')
        path = portal_url.getPortalPath()
        portal_catalog = getToolByName(self.context, 'portal_catalog') 
        projects = portal_catalog(portal_type="Project", path=path)

        all_subjects = [] 
        for i in projects:
            for s in i.Subject:
                if s not in all_subjects:
                   all_subjects.append(s)

        return all_subjects

    def tagForProjects(self, tag):

        portal_url = getToolByName(self.context, 'portal_url')
        path = portal_url.getPortalPath()
        portal_catalog = getToolByName(self.context, 'portal_catalog') 

        projects = portal_catalog(Subject=[tag], path=path, portal_type='Project')

        content_tag_html = ''
        project_name = translate(_(u'Project', default="Project"), context=self.request)
            
        # <span class="event_type"><span>项目</span><a href="project_url">项目标题</a></span>
        if len(projects)==1:
            content = translate(_(u'contain_tag_project_no', default="<div class=\"tag_for_projects\"><p><a href=\"#\" style=\"float:right\" class=\"admin close_tag_for\">Close</a>No project by this tag.</p></div>", mapping={u'tag': tag}),context=self.request) 
        else:
            for p in projects:
                if p.getId != self.context.getId():
                    content_tag_html += "<span class=\"event_type\"><span>%s</span><a target=\"_blank\" href=\"%s\">%s</a></span> "%(project_name, p.getURL(), p.pretty_title_or_id())

                    content_top = translate(_(u'contain_tag_project', default="<a href=\"#\" style=\"float:right\" class=\"admin close_tag_for\">Close</a>Contain \"${tag}\" of the projects: ", mapping={u'tag': tag}),context=self.request) 
                    content = '<div class="tag_for_projects"><p>%s</p>%s</div>'%(content_top, content_tag_html)

        content = force_unicode(content, 'utf')

        ksscore = self.getCommandSet('core')
        selector = ksscore.getSelector('css', '#tag_for_projects') 
        ksscore.replaceInnerHTML(selector, content)

        return self.render()

    def settingTags(self):

        tags = self.context.Subject()
        edit_tags_page = ZopeTwoPageTemplateFile('edit_tags.pt')
        macros = edit_tags_page.macros

        content = self.header_macros(the_macro=macros['edit_tags'] , tags=tags)
        content = force_unicode(content, 'utf')

        ksscore = self.getCommandSet('core')
        selector = ksscore.getSelector('css', '#tag_for_projects') 
        ksscore.replaceInnerHTML(selector, content)
        ksscore.focus('#add_tags')

        return self.render()

    def delTag(self, tag): 

        tags = self.context.Subject()
        tags = list(tags)
        if tag:
            tags.remove(tag)
            self.context.setSubject(tuple(tags))

        tag_html = ''
        for i in self.context.Subject():
            tag_html += "<a href=\"#\" class=\"tag_for\">%s</a> " % (i)

        content = "<span id=\"current_project_tags\" class=\"hideme TGtags EVtags\">%s</span>"%(tag_html) 
        content = force_unicode(content, 'utf')

        ksscore = self.getCommandSet('core')
        selector = ksscore.getSelector('css', '#current_project_tags') 
        ksscore.replaceHTML(selector, content)

        return self.render()
