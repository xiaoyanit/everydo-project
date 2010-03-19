# -*- coding: UTF-8 -*-
import random, cStringIO
import calendar
import copy
from ZTUtils import make_query

from DateTime import DateTime
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

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('zopen.milestone')
from zope.i18n import translate

import logging; info = logging.getLogger('zopen.plone.milestones').info

class ProgressTable(BrowserView):

    def getProjectsProgress(self, projectids):
        ctool = getToolByName(self.context, 'portal_catalog')
        path = ['projects/'+id for id in projectids]
        brains = ctool(path=path, portal_type='Milestone')

        progress = {}
        for milestone in brains:
            projectid = milestone.getPath().split('/')[-3]
            p = (milestone.review_state == 'completed') and 100 or milestone.getHours or 0
            progress.setdefault(projectid, []).append(p)

        for projectid in progress:
            s = float(sum(progress[projectid]))/len(progress[projectid])
            progress[projectid] = round(s*2)/2
        return progress

    def getProgressInfo(self):
        portal = self.context.aq_inner
        ctool = getToolByName(portal, 'portal_catalog')
        brains = ctool(review_state='active', portal_type='Project', sort_on='created')

        paths = [brain.getPath() for brain in brains]

        milestones = ctool(path=paths, portal_type='Milestone', sort_on='end')

        pi = {}
        for milestone in milestones:
            projectid = milestone.getPath().split('/')[-3]
            pi.setdefault(projectid, []).append(milestone)

        for projectid in pi:
            project = getattr(portal.projects, projectid)
            company = project.getCompany()
            project_title = project.Title()
            company_title = company and company.Title() or 'No Company!!!'
            project_name = '%s － %s' %(company_title, project_title)

            progress = 0.0
            for m in pi[projectid]:
                if m.review_state == 'completed':
                    progress += 100
                else:
                    progress += m.getHours or 0

            progress = progress/len(pi[projectid])
            progress = round(progress*2)/2

            pi[projectid].insert(0, 
                    {'name':'%s － %s' %(company_title, project_title),
                     'end':pi[projectid][-1].end,
                     'progress':progress,
                     'responsibles':[m.Title() for m in project.teams.projectmanagers.getMembers()]
                    }
                    )

        return pi

    def csvURL(self):
        q_str = make_query(self.request.form)
        return self.context.absolute_url() + '/progress-export.csv?' + q_str

    def csv(self):

        out = cStringIO.StringIO()
        portal = self.context.aq_inner
        ctool = getToolByName(portal, 'portal_catalog')
        projects = ctool(review_state='active', portal_type='Project', sort_on='created')
        out_title = translate(_(u'out_title',
                                default='TITLE,COMPLETE-TIME,RESPONSIBLE,STATE,PROGRESS,DISCRIPTION'),
                                context=self.request)
        #print >> out, "名称,完成时间,负责人,状态,进度,说明"
        print >> out, out_title
        for project in projects:
            project_ob = project.getObject()
            company = project_ob.getCompany()
            projectid = project_ob.getId()
            if projectid == 'default':
                continue
            project_title = project_ob.Title()
            company_title = company and company.Title() or 'No Company!!!'
            project_name = '%s - %s' %(company_title, project_title)
            path = project.getPath()
            brains = ctool(path=path, portal_type='Milestone', sort_on='end')
                
            try:
                projectinfo = self.getProgressInfo()[projectid][0]
                tot_progress = str(projectinfo['progress']) + '%'
                tot_end = projectinfo['end'] 
                tot_responsor = '、'.join(projectinfo['responsibles'])
                print >> out, '"%s","%s","%s","%s","%s","%s"' % (project_name,tot_end,tot_responsor,'',tot_progress,'')
            except:
                pass 

            for b in brains:
                responsor = self.getMemberGroupName(b.getResponsibleParty)
                progress = b.review_state == 'active' and b.getHours and str(b.getHours) + '%' or '' 
                print >> out, '"%s","%s","%s","%s","%s","%s"' % (b.Title,b.end,responsor,self.getMilestoneInfo(b)[0],progress,self.getMilestoneInfo(b)[1])

        outenc = "gb2312"
        response = self.request.response
        response.setHeader('Content-Type','text/csv;charset=%s' % outenc)
        response.setHeader('Content-Disposition', 'attachment; filename=progress-export.csv')

        return unicode(out.getvalue(), 'utf-8').encode(outenc)

    def getMilestoneInfo(self, m):
        now = DateTime()
        today = DateTime(now.year(),now.month(),now.day())
        delaytime = today - m.end -1
        delaydays = int(delaytime) + 1
        description = m.Description
        state = ''
        if m.review_state == 'active' and delaytime < 0:
            #state = '待办'
            state = translate(_(u'state_active',default='Active'),context=self.request)
        elif m.review_state == 'completed':
            #state = '完成'
            state = translate(_(u'state_completed',default='Completed'),context=self.request)
        else:
            #state = '滞后'
            state = translate(_(u'state_late',default='Late'),context=self.request)
            #description = '(滞后' + str(delaydays) + '天)' + description
            description = translate(_(u'milestone_description',
                                      default='(Late ${delaydays} days) ${description}',
                                      mapping={u'delaydays':str(delaydays), u'description':description}),
                                      context=self.request)

        return (state, description)
                
    def getMemberGroupName(self, responsor):
        mtool = getToolByName(self.context, 'portal_membership')
        gtool = getToolByName(self.context, 'portal_groups')
        if responsor:
            mi = mtool.getMemberInfo(responsor)
            group = gtool.getGroupInfo(responsor)
            if mi:
                return mi['fullname'] or responsor
            elif group:
                return group['title'] or responsor
        else:
            return ''

