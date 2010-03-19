# -*- coding: UTF-8 -*-

import random
import calendar
import copy
from zope.component import getMultiAdapter

from DateTime import DateTime
from AccessControl import getSecurityManager
from Products.Five import BrowserView
from zope.component import getUtility, adapts
from zope.interface import Interface, implements, directlyProvides
from zope.contentprovider.interfaces import IContentProvider
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserView
from Products.CMFCore.utils import getToolByName
from zope.contentprovider.interfaces import ITALNamespaceData
import zope.schema

from Acquisition import Explicit
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import logging; info = logging.getLogger('zopen.plone.milestones').info

class MilestoneReport(BrowserView):

    def getMonthCal(self, index=0):
        now = DateTime()
        year, month = now.year(), now.month()
        year = year + (month + index - 1)/12
        month = (month + index -1) % 12 + 1

        return {'name': month, 'month':month, 'days':calendar.monthcalendar(year, month)}

    def getWeekHeader(self):
        return calendar.weekheader(3).split()

    def get3monthsMilestones(self):
        now = DateTime()
        start_year, start_month,today = now.year(), now.month(), now.day()

        end_year = start_year + (start_month + 3 - 1)/12
        end_month = (start_month + 3 -1) % 12 + 1

        start_date = DateTime(start_year, start_month, 1)
        end_date = DateTime(end_year, end_month, 1)

        ctool = getToolByName(self.context, 'portal_catalog')
        #active_projects = ctool(portal_type='Project', review_state='active')
        #paths = [p.getPath() for p in active_projects]
        pv = getMultiAdapter( (self.context, self.request), name=u'projectview')
        paths = pv.getActiveProjectPaths()
        query = { 'path'        : paths,
                  'portal_type' : 'Milestone',
                  'review_state': 'active',
                  'end'         : {"query":[start_date,
                                            end_date], "range":"minmax"},
                }
        responsibleParty = self.request.get('responsibleParty', '')
        if responsibleParty:
            query['getResponsibleParty'] = responsibleParty

        brains = ctool.searchResults( query)

        milestones = {}
        for b in brains:
            end =b.end
            month,day = end.month(), end.day()

            if not milestones.has_key(month):
                milestones[month] = {}
            if not milestones[month].has_key(day):
                milestones[month][day] = {'name':day, 'milestones':[b]}
            else:
                milestones[month][day]['milestones'].append(b)

        if not start_month in milestones:
            milestones[start_month] = {}
        if not today in milestones[start_month]:
            milestones[start_month][today] = {'name':'TODAY', 'milestones':[]}
        else:
            milestones[start_month][today]['name'] = 'TODAY'

        return milestones

    def getAvaResponsibles(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        company = portal.companies.owner_company

        user = getSecurityManager().getUser()
        userid = user.getUserName()
        ctool = getToolByName(portal, 'portal_catalog')
        results = ctool.unrestrictedSearchResults(portal_type="Person", getId=userid)
        if results:
            emp = results[0].getObject()
            company = emp.aq_parent

        persons = {}
        for p in company.contentValues():
            persons[p.getId()] = p.title_or_id()

        responsibles = [(company.getId(), company.Title())]

        now = DateTime()
        start_year, start_month = now.year(), now.month()

        end_year = start_year + (start_month + 3 - 1)/12
        end_month = (start_month + 3 -1) % 12 + 1

        start_date = DateTime(start_year, start_month, 1)
        end_date = DateTime(end_year, end_month, 1)

        ctool = getToolByName(self.context, 'portal_catalog')
        r = ctool.searchResults(
                { 'portal_type' : 'Milestone',
                  'review_state': 'active',
                  'end'         : {"query":[start_date,
                                            end_date], "range":"minmax"},
                },
                )

        for rp in set([b.getResponsibleParty for b in r]):
            if rp in persons:
                responsibles.append( 
                        (rp, persons[rp]))

        return responsibles

    def getResponsibleInfo(self):
        id = self.request.get('responsibleParty')
        if not id:
            return {'id':'', 'title':''}

        ctool = getToolByName(self.context, 'portal_catalog')
        results = ctool.searchResults(
               portal_type = ['OrganizationUnit','Person'],
               getId=[id],
               )

        if results:
            return {'id':id, 'title':results[0].Title}
        else:
            return {'id':id, 'title':id}

