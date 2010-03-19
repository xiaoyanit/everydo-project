# -*- encoding: UTF-8 -*-

from zope import event

from Products.Five import BrowserView
from kss.core import kssaction

# import logging; info = logging.getLogger('zopen.plone.org').info

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.Archetypes.event import ObjectEditedEvent

from plone.memoize.instance import memoize
from zopen.plone.org.interfaces import IOrganizedEmployess
from zope.i18nmessageid import MessageFactory
from zope.i18n import translate

_ = MessageFactory('zopen.org')

class TeamView(BrowserView):

    @memoize
    def getCompanyPeopleTeamInfo(self):
        members, result = {}, {}
        for team in self.getAvailableTeams():
            for m in team.getMembers():
                members.setdefault(m, [])
                members[m].append(team)

        for member in members:
            company = member.aq_parent.aq_inner
            id = company.getId()
            if not result.has_key(id):
                result[id] = [(company, [])]
            result[id].append( (member, members[member]) )
        return result


    def get_available_companies(self):
        cpti = self.getCompanyPeopleTeamInfo()

        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        all_companies = portal.companies.contentValues()

        result = []
        for c in all_companies:
            if c.getId() not in cpti:
                result.append(c)

        return result

    def get_available_people(self, companyid):
        cpti = self.getCompanyPeopleTeamInfo()
        members = [mt[0] for mt in cpti.get(companyid, [])]

        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        company = getattr(portal.companies, companyid)
        result = []
        for person in company.objectValues():
            if person not in members:
                result.append(person)

        return result

    def getPersonTeam(self, person_id):

        portal_cat = getToolByName(self.context, 'portal_catalog')
        brains = portal_cat.searchResults({
                    'portal_type': 'Person',
                    'getId': person_id,
                })
        
        person = brains[0].getObject()
        puid = person.UID()
        personteams = []
        for team in self.getAvailableTeams():
            member_uids = list(team.getRawMembers())
            if puid in member_uids:
                personteams.append((team.getId(),team.pretty_title_or_id()))

        return personteams
        
        

    @memoize
    def getAvailableTeams(self):
        return self.context.contentValues({'portal_type':['Team']})

from plone.app.kss.plonekssview import PloneKSSView
from kss.core import force_unicode
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from zope.component import getUtility

from zopen.plone.org.interfaces import (
        IOrganizedEmployess, IOrgInstance)

# import logging; info = logging.getLogger('zopen.plone.org').info

import re

valid_id = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_-]{1,14}$').match

class TeamKssView(PloneKSSView, TeamView):

    def macroContent(self, macropath, **kw):
        'Renders a macro and returns its text'
        path = macropath.split('/')
        if len(path) < 2 or path[-2] != 'macros':
            raise RuntimeError, 'Path must end with macros/name_of_macro (%s)' % (repr(macropath), )
        # needs string, do not tolerate unicode (causes but at traverse)
        try:
            the_macro = self.context.unrestrictedTraverse(macropath)
        except AttributeError, IndexError:
            raise RuntimeError, 'Macro not found'
        #
        # put parameters on the request, by saving the original context
        self.request.form, orig_form = kw, self.request.form
        content = self.header_macros(the_macro=the_macro, **kw)
        self.request.form = orig_form
        # Always encoded as utf-8
        content = force_unicode(content, 'utf-8')
        return content

    @kssaction
    def add_new_company(self, company_name):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        basecamp_org = IOrgInstance(portal)
        c = basecamp_org.createCompany(company_name)

        core = self.getCommandSet('core')
        ksszopen=self.getCommandSet('zopen')
        ksszopen.clear(core.getSelector('css', '.add-new-company-name'))
        self._insert_company(c.getId())

        selector = core.getSelector('css', '.selectCompanyArea')
        content = "<select name=\"select-add-company-name\" class=\"selectCompanyArea\">"
        for c in self.get_available_companies():
            content += "<option value='" + c.getId() +"'>" + \
                        c.pretty_title_or_id() + "</option>"
        
        content += "</select>"
        content = force_unicode(content, 'utf-8')

        core.replaceHTML(selector, content)

    @kssaction
    def select_add_company(self, company_name):
        self._insert_company(company_name)

        core = self.getCommandSet('core')
        if len(self.get_available_companies()) == 1:
            selector = core.getSelector('css', '.ChooseCompany')
            core.toggleClass(selector, classname="hideme")
        else:
            selector = core.getSelector('css', '.selectCompanyArea')
            content = "<select name=\"select-add-company-name\"  \
                             class=\"selectCompanyArea\""
            for c in self.get_available_companies():
                if c.getId() == company_name:
                    continue
                content += "<option value='" + c.getId() +"'>" + \
                            c.pretty_title_or_id() + "</option>"
            
            content += "</select>"
            content = force_unicode(content, 'utf-8')
            core.replaceHTML(selector, content)

    def _getDefaultTeam(self, company_name):
        return company_name == 'owner_company' and 'projectseniors' or 'projectmembers'

    @kssaction
    def select_add_person(self, company_name):

        if not self.request.form['persons']:
            return
        
        
        portalObj = getToolByName(self.context, 'portal_url').getPortalObject()

        persons = self.request.form['persons'];
        company = getattr(portalObj.companies, company_name)

        for person_name in persons:
            person = getattr(company, person_name)

            team_id = self.request.form['selectvalue']
            team = getattr(self.context, team_id)
            team.setMembers(team.getMembers() + [person])


        self._update_company(company_name)

    @kssaction
    def updateCompany(self, companyname):
        self._update_company(companyname)

        
    @kssaction
    def add_new_person(self, companyid, username,
            email, fullname, password, selectnewvalue, disable=False, notify=False):
        # create a user from the input

        notify = not disable and notify

        portalObj = getToolByName(self.context, 'portal_url').getPortalObject()
        company = getattr(portalObj.companies, companyid)
        result = company.check_id(id = username, contained_by=company)
        if result:
            self.getCommandSet('plone').issuePortalMessage(
                    result, 'error')
            return

        # portal_registration = getUtility(IRegistrationTool)
        # if not portal_registration.isMemberIdAllowed(username):
        #     self.getCommandSet('portalmessage').issuePortalMessage(
        #             'illegal member id', 'portalWarningMessage')
        #     return self.render()

        if valid_id(username) is None:
            self.getCommandSet('plone').issuePortalMessage(
                    translate(_(u'illegal_member_id', default='Member Id is valid'), context=self.request), 
                    translate(_(u'error'),context=self.request))
            return

        membership = getToolByName(self.context, 'portal_membership')
        if membership.getMemberById(username) is not None:
            self.getCommandSet('plone').issuePortalMessage(
                    translate(_(u'exisits_in_portal', default='Exisits in portal, please change person username.'), context=self.request),
                    translate(_(u'error'),context=self.request))
            return

        # company.invokeFactory(type_name='Person', id=username)
        _createObjectByType('Person', company, username)
        person = getattr(company, username)
        person.setEmail(email)
        person.setTitle(fullname)
        person.setPassword(password)
        person.reindexObject()

        # 手动调用，以便设置权限
        person.unmarkCreationFlag()

        event.notify(ObjectEditedEvent(person))
        person.at_post_create_script()

        if disable:
            wf_tool = getToolByName(person, 'portal_workflow')
            wf_tool.doActionFor(person, 'deactivate')

        team_id = selectnewvalue
        team = getattr(self.context, team_id)
        team.setMembers(team.getMembers() + [person])

        self._update_company(companyid)

        if notify:
            person.sendAccountInfoEmail(password)

    @kssaction
    def remove_company_from_project(self, company_name):
        portal_cat = getToolByName(self.context, 'portal_catalog')
        brains = portal_cat.searchResults({
                    'portal_type': 'OrganizationUnit',
                    'getId': company_name,
                })
        company = brains[0].getObject()
        del_uids = set([obj.UID() for obj in company.contentValues()])

        for team in self.getAvailableTeams():
            member_uids = set(team.getRawMembers())
            left_uids = member_uids - del_uids
            if left_uids != member_uids:
                team.setMembers( tuple(left_uids))

        ksscore = self.getCommandSet('core')
        selector = ksscore.getParentNodeSelector('div.companyRow')
        ksscore.deleteNode(selector)

    
    @kssaction
    def remove_person_from_project(self, person_name):
        person = self._getPerson(person_name)
        company_name = person.aq_parent.getId()
        puid = person.UID()

        for team in self.getAvailableTeams():
            member_uids = list(team.getRawMembers())
            if puid in member_uids:
                members = [uid for uid in member_uids if uid != puid]
                team.setMembers(members)
        
        self._update_company(company_name)
    
    @kssaction
    def remove_person_from_team(self, person_name, team_id):
        person = self._getPerson(person_name)
        puid = person.UID()
        
        for team in self.getAvailableTeams():
            if team.getId() == team_id:
                member_uids = list(team.getRawMembers())
                members = [uid for uid in member_uids if uid != puid]
                team.setMembers(members)


        ksscore = self.getCommandSet('core')
        content = self.macroContent(
                'context/@@teamfolder_view/macros/permisson',
                obj = person
                )

        selector = ksscore.getSelector('parentnodecss',\
                '.person|.permissonOperation')
        ksscore.replaceHTML(selector, content)

    def _insert_company(self, company_name):
        # 内部使用函数，传入company_name参数用于插入一个公司块

        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        basecamp_org = IOrgInstance(portal)
        company = basecamp_org.getCompany(company_name)
        company_and_people = [(company, []), ]

        content = self.macroContent(
                'context/@@teamfolder_view/macros/company_element',
                company_and_people=company_and_people)

        ksscore = self.getCommandSet('core')
        selector = ksscore.getParentNodeSelector('div.insert-company-after-stub')
        ksscore.insertHTMLAfter(selector, content)

    def _update_company(self, company_name):
        # 内部使用函数，传入company_name参数用于更新整个公司块

        cpti = self.getCompanyPeopleTeamInfo()

        if cpti.has_key(company_name):
            company_and_people = cpti[company_name]
        else:
            portalObj = getToolByName(self.context, 'portal_url').getPortalObject()
            company = getattr(portalObj.companies, company_name)
            company_and_people = [(company,[])]

        # info("%r" % available_people)

        content = self.macroContent(
                'context/@@teamfolder_view/macros/company_element',
                company_and_people=company_and_people)

        ksscore = self.getCommandSet('core')
        selector = ksscore.getParentNodeSelector('div.companyRow')
        ksscore.replaceHTML(selector, content)

    def _getPerson(self, person_id):
        portal_cat = getToolByName(self.context, 'portal_catalog')
        brains = portal_cat.searchResults({
                    'portal_type': 'Person',
                    'getId': person_id,
                })
        return brains[0].getObject()
    
    @kssaction
    def getTeamSelect(self, team_id):
        teams = self.getAvailableTeams()
        teamsids = [team.getId() for team in teams] 
        ksscore = self.getCommandSet('core')
        selector = ksscore.getSelector('samenode','')
        content = "<select class=\"selectarea\" style=\"display: inline;\">"
        for team in teams:
            if team.getId() == team_id:
                content += "<option value=\"" + team.getId() + \
                           "\"  selected=\"selected\">" + team.pretty_title_or_id() + \
                            "</option>"
            else:
                content += "<option value=\"" + team.getId() + \
                           "\">" + team.pretty_title_or_id() + \
                            "</option>"
                    
        content += "</select>"
        content = force_unicode(content, 'utf-8')
        ksscore.insertHTMLAfter(selector, content)
        selectarea = ksscore.getSelector('css', '.selectarea')
        ksscore.focus(selectarea)
    
    @kssaction
    def setPersonTeam(self, person_id, team_id, just_change, the_item_id=''):
        person = self._getPerson(person_id)
        puid = person.UID()

        for team in self.getAvailableTeams():

            if team_id == the_item_id:
                continue
                
            member_uids = list(team.getRawMembers())
            if just_change == 'yes':
                if puid in member_uids and team.getId() == the_item_id:
                    members = [uid for uid in member_uids if uid != puid]
                    team.setMembers(members)
                    
            if puid in member_uids:   
                continue 
                
            elif puid not in member_uids and team.getId() == team_id:
                member_uids.append(puid)
                team.setMembers(member_uids)

        content = self.macroContent(
                'context/@@teamfolder_view/macros/permisson',
                obj = person
                )

        # here follows the kss output
        ksscore = self.getCommandSet('core')
        selector = ksscore.getSelector('parentnodecss',\
                '.person|.permissonOperation')
        ksscore.replaceHTML(selector, content)

