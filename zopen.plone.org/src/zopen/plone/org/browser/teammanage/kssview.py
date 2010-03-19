# -*- encoding: UTF-8 -*-

from plone.app.kss.plonekssview import PloneKSSView
from kss.core import force_unicode
from datetime import datetime
from interfaces import ITeamManager
from copy import copy

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from AccessControl import getSecurityManager, User, SecurityManagement


from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
_ = MessageFactory('zopen.org')

list_template = ZopeTwoPageTemplateFile('list.pt')

class SelectionView(PloneKSSView):

    def _createTeam(self, title, description=''):
        title = title.strip()

        title = force_unicode(title, 'utf-8')
        description = force_unicode(description , 'utf-8')
        id = self.context.plone_utils.normalizeString(title)
        if id in self.context.objectIds():
            return None

        tm = ITeamManager(self.context)
        tm.addTeam(id, title, description)
        return id, title, description

    def selectionCreateCategory(self, title):
        if title=='': 
            self.getCommandSet('plone').issuePortalMessage(
                    translate(_(u'please enter category title.'), default="Please enter category title.", context=self.request),
                    translate(_(u'Error'), default="Error", context=self.request))
            return self.render()
        id,title = self._createCategory(title)
        # content = u'<option value="%s" selected="selected">%s</option>' % (id, title)

        content = u'<option value="%s" selected="selected">%s</option>' % (id, title)
        content = content.replace('<', '&lt;').replace('>', '&gt;')
        # KSS specific calls
        core = self.getCommandSet('core')
        zopen = self.getCommandSet('zopen')
        zopen.newSelectOption(core.getSelector('samenode', ''), id, title.decode('utf-8'))
        #core.replaceHTML(core.getSelector('samenode', ''), content)
        return self.render()

    def listCreateTeam(self, title, description='', is_template_setting=False):
        tm = ITeamManager(self.context)
        content_url = tm.getContentInfo()[1]
        content_id = tm.getContentInfo()[0]
        if title=='': 
            self.getCommandSet('plone').issuePortalMessage(
                    translate(_(u'please_enter_team_title.'),
                                default="Please enter team title.", context=self.request),
                    translate(_(u'Error'), default="Error", context=self.request))
            return self.render()
        result = self._createTeam(title, description)
        if result == None:
            msg = _(u'team_${title}_was_existed.', 
                      default='Team ${title} was existed.', mapping={u'title' : title})
            self.getCommandSet('plone').issuePortalMessage(
                    translate(msg, context=self.request),
                    translate(_(u'Error'), default="Error", context=self.request))
            return self.render()
        else:
            id,title, description = result 
        the_macro = list_template.macros['teamitem']
        content = self.header_macros(the_macro=the_macro,
                        here_url = content_url,
                        team_del = 1,
                        team_cur = 0,
                        team_title = title,
                        team_id  = id,
                        team_description = description,
                        is_template_setting = is_template_setting=='True')
        # Always encoded as utf-8
        content = force_unicode(content, 'utf')

        core = self.getCommandSet('core')
        core.insertHTMLBefore('#add_new_team-'+content_id, content)

        msg = _(u'team_${title}_was_added.', default="Team ${title} was added.", mapping={u'title' : title})
        self.getCommandSet('plone').issuePortalMessage(
                translate(msg, context=self.request),
                translate(_(u'Info'), default="Info", context=self.request))
        
        ksszopen=self.getCommandSet('zopen')
        ksszopen.clear(core.getSelector('css', '#new_team_input-'+content_id))
        ksszopen.clear(core.getSelector('css', '#textarea-'+content_id))
        core.addClass(core.getSelector('css', '.submit_add'), 'hideme')

        return self.render()

    def renameTeam(self, id, new_title, new_description='', is_template_setting=False):
        context = self.context.aq_inner
        new_title = new_title.strip()
        new_description = new_description.strip()
        tm = ITeamManager(self.context)
        tm.renameTeam(id, new_title, new_description)
        content_url = tm.getContentInfo()[1]

        core = self.getCommandSet('core')
        selector = core.getParentNodeSelector('.kssDeletionRegion')

        the_macro = list_template.macros['teamitem']
        content = self.header_macros(the_macro=the_macro,
                here_url = content_url,
                team_del = tm.teamDeletable(id),
                team_cur = 0,
                team_title = new_title,
                team_id   = id,
                team_description = new_description,
                is_template_setting=is_template_setting=='True')
        content = force_unicode(content, 'utf-8')
        core.replaceInnerHTML(selector, content)
        teamidstr = "teamitem-" + id + "-" + context.aq_parent.getId()
        teamselector = core.getSelector("css", "." + teamidstr)
        teamcontent = "<span class=\"" + teamidstr + \
                      "\">" + new_title  + "</span>"

        teamcontent = force_unicode(teamcontent, 'utf-8')
        core.replaceHTML(teamselector, teamcontent)


        self.getCommandSet('plone').issuePortalMessage(
                translate(_(u'modified success.'), default="Modified success", context=self.request),
                translate(_(u'Info'), default='Info', context=self.request))

        return self.render()


    def deleteTeam(self, selector):

        obj = self.context.aq_inner
        parent = obj.aq_parent
        team_id = obj.getId()
        originalSecurityManager = SecurityManagement.getSecurityManager()
        SecurityManagement.newSecurityManager(None, User.SimpleUser('admin','',('Manager',), ''))
        parent.manage_delObjects(str(team_id))
        SecurityManagement.setSecurityManager(originalSecurityManager)
        core = self.getCommandSet('core')
        selector = core.getParentNodeSelector(selector)
        core.deleteNode(selector)
        containner = parent.aq_parent

        teamidstr = ".teamitemroot-" + team_id + "-" + \
                    containner.getId()
        teamselector = core.getSelector("css", teamidstr)
        core.deleteNode(teamselector)

        containner.manage_delLocalRoles([team_id + '-' + \
                containner.getId()])
        containner.reindexObjectSecurity()

        for item in ['messages', 'files', 'todos', 'milestones',\
                     'writeboards', 'chatroom', 'time']:
            obj = containner.unrestrictedTraverse(item)
            obj.manage_delLocalRoles([team_id + '-' + \
                    containner.getId()])
            obj.reindexObjectSecurity()

            if item in ['messages', 'files']:
                for i in obj.contentValues():
                    i.manage_delLocalRoles([team_id + '-' + \
                            containner.getId()])
                    i.reindexObjectSecurity()


        self.getCommandSet('plone').issuePortalMessage(
                translate(_(u'Deleted.'), default="Deleted.", context=self.request),
                translate(_(u'Info'), default="Info", context=self.request))
        return self.render()
