from zope.interface import implements
from zope.component import adapts

from Products.ATContentTypes.interface import IATFolder
from Products.CMFCore.utils import getToolByName

from interfaces import IOrganizedEmployess, ITeamFolderContent

import logging; info = logging.getLogger("zopen.plone.org").info

class TeamsEmplyees(object):

    implements(IOrganizedEmployess)
    adapts(ITeamFolderContent) # the teams folder

    def __init__(self, context):
        self.context = context

    def get_teams(self):
        # here context is a Project
        # so we must get the teams folder first
        return self.context.contentValues({'portal_type':['Team']})

    def _getCompaniesAndPeople(self, members):

        result = {}
        for member in members:
            # XXX here call the aq_parent is not a good method

            company = member.aq_parent
            id = company.getId()
            if not result.has_key(id):
                result[id] = [company]
            result[id].append(member)

        # info("%r" % result)
        return result

    def get_companies_and_people(self, team):
        members = team.getMembers()
        return self._getCompaniesAndPeople(members)

    def get_people(self, team):
        return self.get_companies_and_people(team).values()

    def get_all_people(self):
        members = {}
        for team in self.get_teams():
            for m in team.getMembers():
                members[m] = 1
        return members.keys()

    def get_all_companies_and_people(self):
        members = self.get_all_people()
        return self._getCompaniesAndPeople(members)

    def get_available_companies(self, team):
        companies = self.get_companies_and_people(team).keys()

        result = []

        portalObj = getToolByName(self.context, 'portal_url').getPortalObject()
        all_companies = portalObj.companies.contentValues()
        for c in all_companies:
            if c.getId() not in companies:
                result.append(c)

        return result

    def get_available_companies_and_people(self, team):
        # this is a data structure with 
        # { 'zopen': [<OU at ...>, <Person at ...>, <Person ...>],
        #   ... }
        companies_and_people = self.get_companies_and_people(team)

        # so we should changed here.
        companies_and_people = dict(
                (c_k, [p.getId() for p in people[1:]])
                for c_k, people in companies_and_people.items())

        portal = getToolByName(self.context, 'portal_url')
        portalObj = portal.getPortalObject()

        # here we suppose all contents in portal.companies
        # are all OrgnizedUnits
        all_companies = portalObj.companies.contentValues()

        result = {}
        for company in all_companies:
            # we suppose each item in a company is an Employee
            people = company.contentValues()
            company_id = company.getId()
            if company_id not in companies_and_people.keys():
                result[company_id] = people
            else:
                result[company_id] = []
                for p in people:
                    if p.getId() not in companies_and_people[company_id]:
                        result[company_id].append(p)

        # info("%r" % result)
        return result

    def caculateCompanyPeople(self, subscribers):
        # input:
        #   subscribers: [id1, id2, id3, ...]
        # 
        # output:
        #   { 'zopen': [company, person1, person2, ...],
        #     'ibc': [company, person1, person2, ...]
        #   }

        portal_catalog = getToolByName(self.context, 'portal_catalog')
        portal_url = getToolByName(self.context, 'portal_url')
        brains = portal_catalog.searchResults({
                'path': portal_url.getPortalPath() + '/companies',
                'portal_type': 'Person',
                'getId': subscribers,
                })

        result = {}
        for b in brains:
            person = b.getObject()
            company = person.aq_parent
            id = company.getId()
            if not result.has_key(id):
                result[id] = [company]
            result[id].append(person)
        return result

