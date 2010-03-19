# -*- coding: UTF-8 -*-

from zope import event

from Products.Five import BrowserView

from zope.component import adapts
from zopen.plone.org.interfaces import IOrgInstance
from zope.i18nmessageid import MessageFactory
from zope.i18n import translate

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import checkEmailAddress
from Products.CMFDefault.exceptions import EmailAddressInvalid
from Products.Archetypes.event import ObjectEditedEvent

from zopen.plone.widgets.validation import errorEmail
from zopen.plone.org.events import PersonTeamChangedEvent

# import logging; info = logging.getLogger('zopen.plone.org').info

from plone.app.kss.plonekssview import PloneKSSView
from kss.core import force_unicode
import re

_ = MessageFactory('zopen.org')
valid_id = re.compile(r'^[a-zA-Z0-9][a-z0-9_-]{1,14}$').match
from zope.i18nmessageid import MessageFactory
from zope.i18n import translate

class OrganizationUnitView(BrowserView):

    def get_companies_and_people(self):
        companies = self.context.contentValues()

        # build a list of lists
        result = []
        for company in companies:
            result.append([company,] + company.contentValues())

        #info("%r" % (result,))
        return result

    def getAvailableTeams(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        basecamp_org = IOrgInstance(portal)
        return basecamp_org.getAvailableTeams()

    def get_team_of_person(self, person):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        basecamp_org = IOrgInstance(portal)
        return basecamp_org.get_team_of_person(person)

class KSSView(PloneKSSView, OrganizationUnitView):

    def site_add_new_company(self, company_name):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        basecamp_org = IOrgInstance(portal)
        company = basecamp_org.createCompany(company_name)

        content = self.macroContent(
                'context/@@organizationunit_view/macros/company',
                company_and_people = [company,]
                )

        ksscore = self.getCommandSet('core')
        ksscore.insertHTMLAsFirstChild('div#company_list', content)

        return self.render()

    def site_set_team(self, person_id, team_id, old_team_id):
        # info("%r" % person_id)
        # info("%r" % team_id)

        portal_url = getToolByName(self.context, 'portal_url')
        portalObj = portal_url.getPortalObject()
        team = getattr(portalObj.teams, team_id, None)
        old_team = getattr(portalObj.teams, old_team_id, None)
        if old_team is not None:
            members = old_team.getMembers()
            result = []
            for m in members:
                if m.getId() != person_id:
                    result.append(m)
            old_team.setMembers(result)


        portal_cat = getToolByName(self.context, 'portal_catalog')
        brains = portal_cat.searchResults({
                    'portal_type': 'Person',
                    'getId': person_id,
                })

        # assert len(brains) == 1
        person = brains[0].getObject()
        if team is not None:
            team.setMembers(
                    team.getMembers() + [person]
                    )

        wf_tool = getToolByName(self.context, 'portal_workflow')
        if wf_tool.getInfoFor(person, 'review_state') == 'inactive':
            old_team_id = '-'

        if team_id == '-':
            if wf_tool.getInfoFor(person, 'review_state') == 'active':
                wf_tool.doActionFor(person, 'deactivate')
        elif old_team_id == '-':
            wf_tool.doActionFor(person, 'activate')

        content = self.macroContent(
                'context/@@organizationunit_view/macros/person-sheet',
                obj = person,
                old_team = team,
                )

        # here follows the kss output
        ksscore = self.getCommandSet('core')
        selector = ksscore.getSelector('parentnode', '.person_info') 
        ksscore.replaceHTML(selector, content)

        event.notify(PersonTeamChangedEvent(person, team_id, old_team_id))

        return self.render()

    def addNewPerson(self, username='', fullname='', disable=False,
            email='', password='', notify=''):
        # person_name, team_id,
        #    email, full_name, password):
        # create a user from the input

        notify = not disable and notify

        company = self.context.aq_inner

        result = company.check_id(id = username, contained_by=company)
        if result:
            self.getCommandSet('plone').issuePortalMessage(
                    result, 'error')
            return self.render()

        if valid_id(username) is None:
            self.getCommandSet('plone').issuePortalMessage(
                    translate(_(u'illegal_member_id'), context=self.request), 
                    translate(_(u'error'), context=self.request))
            return self.render()

        if errorEmail(email):
            self.getCommandSet('plone').issuePortalMessage(
                    errorEmail(email), 
                    translate(_(u'error'), context=self.request))
            return self.render()


        membership = getToolByName(self.context, 'portal_membership')
        if membership.getMemberById(username) is not None:
            self.getCommandSet('plone').issuePortalMessage(
                    translate(_(u'exisits_in_portal'), context=self.request),
                    translate(_(u'error'), context=self.request))
            return self.render()

        company.invokeFactory(type_name='Person', id=username,
                title=fullname)
        person = getattr(company, username)
        person.setEmail(email)
        person.setPassword(password)
        #person.reindexObject()

        # 手动调用，以便设置权限
        person.unmarkCreationFlag()

        event.notify(ObjectEditedEvent(person))
        person.at_post_create_script()

        if disable:
            wf_tool = getToolByName(person, 'portal_workflow')
            wf_tool.doActionFor(person, 'deactivate')

        content = self.macroContent(
                'context/@@organizationunit_view/macros/company',
                company_and_people = [self.context] +  self.context.contentValues()
                )

        ksscore = self.getCommandSet('core')
        ksscore.replaceHTML(
                ksscore.getSelector('parentnode', '.kssDeletionRegion'), 
                content)

        if notify:
            person.sendAccountInfoEmail(password)
        return self.render()

    def setProjectCreator(self, person_id):

        mtool = getToolByName(self.context, 'portal_membership')
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        member = mtool.getMemberById(person_id)
        member_roles = member.getRolesInContext(portal)

        if 'ProjectCreator' in member_roles: 
            portal.manage_delLocalRoles([person_id])
        else:
            portal.manage_setLocalRoles(person_id,['ProjectCreator'])

        self.getCommandSet('plone').issuePortalMessage(translate(_(u'modified success.'),
                              default="Modified success", context=self.request), 
                              translate(_(u'Info'), default='Info', context=self.request))


        return self.render()

    def unlockPerson(self):
        obj = self.context.aq_inner
        try:
            from plone.locking.interfaces import ILockable
            HAS_LOCKING = True
        except ImportError:
            HAS_LOCKING = False
        if HAS_LOCKING:
            lockable = ILockable(obj)
            if lockable.locked():
                lockable.unlock()
        return self.render()

