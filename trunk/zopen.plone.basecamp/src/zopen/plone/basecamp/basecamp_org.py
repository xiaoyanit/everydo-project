from zope.interface import implements
from zope.component import adapts

from Products.CMFPlone.utils import _createObjectByType, getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot

from zopen.plone.org.interfaces import IOrgInstance

import random

from config import OWNER_COMPANY_ID

class BasecampOrg(object):

    adapts(IPloneSiteRoot)
    implements(IOrgInstance)

    def __init__(self, context):
        self.context = context

    def createCompany(self, name):
        #portal = getToolByName(context,'portal_url').getPortalObject()
        portal = self.context

        id = self.randomId()
        while id in portal.companies.objectIds():
            id = self.randomId()

        _createObjectByType('OrganizationUnit', portal.companies, id, title=name)
        c = self.getCompany(id)

        return c

    def getAvailableCompanies(self):
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        companies = portal_catalog(portal_type="OrganizationUnit",
                review_state="active")

        results = []
        for brain in companies:
            if brain.getId != OWNER_COMPANY_ID:
                results.append((brain.getId, brain.Title))

        return results

    def getAvailableTeams(self):
        portal = self.context
        return portal.teams.contentValues({'portal_type': 'Team'})

    def randomId(self):
        return str(random.randrange(100000, 999999))

    def getCompany(self, id):
        portal = self.context
        return getattr(portal.companies, id)

    def getOwnerCompany(self):
        return self.getCompany(OWNER_COMPANY_ID)

    def get_team_of_person(self, person):
        # 找到person所在的系统teams
        # 找不到则返回None

        portal = self.context
        teams = portal.teams.contentValues()
        for team in teams:
            if person in team.getMembers():
                return team

