# -*- coding: UTF-8 -*-

import random
import calendar
import copy
from Products.Archetypes.event import ObjectEditedEvent
from zope import event

from DateTime import DateTime
from Products.Five import BrowserView
from zope.component import getUtility, adapts
#from Products.CMFPlone.interfaces import IPloneTool
from zope.interface import Interface, implements, directlyProvides
from zope.contentprovider.interfaces import IContentProvider
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserView

from zope.contentprovider.interfaces import ITALNamespaceData
import zope.schema

from Acquisition import Explicit
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('zopen.milestone')
from zope.i18n import translate

import logging; info = logging.getLogger('zopen.plone.milestones').info

def sendNotification(request, milestone, temp_type = 'start'):
        rp = milestone.getResponsibleParty()
        if not rp:
            #print 'no resp, return'
            return

        mtool = getToolByName(milestone, 'portal_membership')
        member_rp = mtool.getMemberById(rp)
        rp_email = member_rp and member_rp.getProperty('email')
        if not rp_email:
            #print 'no mail, return'
            return

        project = milestone.getProject()
        company = project.getCompany()
        milestones = milestone.aq_parent

        subject_id = ''    
        subject_content = ''
        template_id = ''
        template_content = ''
        if temp_type == 'start':

            subject_id = u'mail_subject'    
            subject_content = '[$project_title] Milestone assigned to you'
            template_id = u'mail_body'
            template_content = """
--------------------------------------------------------------
Company:${company_name}
Project:${project_name}
--------------------------------------------------------------

You have just been assigned the following milestone 
by ${user_name}<${user_email}>:

${milestone_title}
Due on ${milestone_end_date}

--To view this milestone, visit:
${milestones_url}'"""
        
        elif temp_type == 'due':
            subject_id = u'mail_subject2'    
            subject_content = '[$project_title] Milestone will due in 48 hours'
            template_id = u'mail_body2'
            template_content ="""
--------------------------------------------------------------
Company: ${company_name}
Project:${project_name}
--------------------------------------------------------------

The following milestone will due in 48 hours
by ${user_name} <${user_email}>: ${milestone_title}
Due on ${milestone_end_date}

--To view this milestone, visit:
${milestones_url}'
"""
        else: raise 'unknown template type.'

        
        subject = translate(_(subject_id, default=subject_content, mapping={u'project_title':project.Title()}),
                context = request)

        creator = milestone.Creator()
        member = mtool.getMemberById(creator)
        fullname = member and member.getProperty('fullname', creator) or creator
        email = member and member.getProperty('email', '') or ''

        body = translate(_(template_id,
            default=template_content,
           mapping={u'milestones_url':milestones.absolute_url(), 
                    u'user_name':fullname,
                    u'user_email':email,
                    u'company_name':company.Title(),
                    u'project_name':project.Title(),
                    u'milestone_title':milestone.Title(),
                    u'milestone_end_date':milestone.end(),}),
                    context=request)

        portal = getToolByName(milestone, 'portal_url').getPortalObject()
        mfrom = '"%s" <%s>' % (portal.email_from_name, portal.email_from_address)

        mh = getToolByName(milestone, 'MailHost')
        mh.secureSend(body, mto=rp_email,
                mfrom=mfrom,subject=subject, charset='UTF-8')
        #print 'finish send...'

class MilestonesView(BrowserView):

    def today(self):
        now = DateTime()
        return DateTime(now.year(), now.month(), now.day())

    def getTimelinedResults(self):
        path = '/'.join(self.context.getPhysicalPath())

        portal_catalog = getToolByName(self.context, 'portal_catalog')
        results = portal_catalog.searchResults(
                {'path'       : path,
                 'portal_type': 'Milestone',
                },
                sort_on = 'end',
                )

        late, upcomming, completed = [], [], []
        now = DateTime()
        today = DateTime(now.year(), now.month(), now.day())

        # { 2001: { 1月份: { 2: [brain, ],
        #                    5: [...]
        #         { 2月份: {
        # { 2004: { ... }
        # 
        _calendar, _past_calendar = {}, {}

        for brain in results:
            end = brain.end
            if brain.review_state == 'completed':
                completed.append(brain.getObject())
                state = 'past'
            elif end < today:
                late.append(brain.getObject())
                state = 'late'
            else:
                upcomming.append(brain.getObject())
                state = 'future'

            _calendar.setdefault(end.year(), {}).setdefault(end.month(), {}).setdefault(end.day(), state)

        def _calculate_calendar():
            # fill the space between the first milestone to the last
            year = min(_calendar.keys())
            month = min(_calendar[year].keys())
            max_year = max(_calendar.keys())
            max_month = max(_calendar[max_year].keys())
            while (year, month) <= (max_year, max_month):
                _calendar.setdefault(year, {}).setdefault(month, None)
                year, month = year + month / 12, month % 12 + 1

            for year in sorted(_calendar.keys()):
                for month in sorted(_calendar[year].keys()):
                    day_items = _calendar[year][month]
                    if not day_items:
                        continue

                    cal = calendar.monthcalendar(year, month)
                    _calendar[year][month] = copy.deepcopy(cal)

                    # these code calculate a matrix month calendar:
                    #
                    # >>> pprint(monthcalendar(2007, 4))
                    # [[0, 0, 0, 0, 0, 0, 1],
                    #  [2, 3, 4, 5, 6, 7, 8],
                    #  [9, 10, 11, 12, 13, 14, 15],
                    #  [16, 17, 18, 19, 20, 21, 22],
                    #  [23, 24, 25, 26, 27, 28, 29],
                    #  [30, 0, 0, 0, 0, 0, 0]]
                    for i in range(len(cal)):
                        for j in range(7):
                            _calendar[year][month][i][j] = {}
                            if cal[i][j]:
                                _calendar[year][month][i][j]['day'] = cal[i][j]
                            # isCurrentDay
                            if year == today.year() and month == today.month() \
                                    and cal[i][j] == today.day():
                                _calendar[year][month][i][j]['istoday'] = 1
                            elif day_items.has_key(cal[i][j]):
                                _calendar[year][month][i][j][ day_items[cal[i][j]] ] = 1
                            else:
                                _calendar[year][month][i][j]['else'] = None

            year = min(_calendar.keys())
            month = min(_calendar[year].keys())
            while (year, month) < (today.year(), today.month()):
                if _calendar.has_key(year) and _calendar[year].has_key(month):
                    _past_calendar.setdefault(year, {}).setdefault(month, _calendar[year][month])
                    del _calendar[year][month]
                    if not _calendar[year]:
                        del _calendar[year]

                year, month = year + month / 12, month % 12 + 1

            # info("%r" % _calendar)

        if _calendar:
            _calculate_calendar()

        def _calculate_a_weeks():
            a_weeks = [None] * 7

            day = today
            for i in range(7):
                a_weeks[i] = day.aDay()
                day += 1
            return a_weeks

        def _calculate_two_weeks():
            two_weeks = [[None] * 7, [None] * 7]

            brains = portal_catalog.searchResults(
                    {'path' : path,
                     'portal_type': 'Milestone',
                     'end': {"query": [today, today+14], "range": "minmax"},
                    },
                    )

            _upcoming = {}
            for b in brains:
                end = b.end
                end = DateTime(end.year(), end.month(), end.day())

                _upcoming.setdefault(end, []).append(b)

            day = today
            for i in range(2):
                for j in range(7):
                    two_weeks[i][j] = {}
                    two_weeks[i][j]["day"] = day.day()
                    if _upcoming.has_key(day):
                        two_weeks[i][j]["its"] = _upcoming[day]
                    day += 1
            nextday = today+1
            two_weeks[0][0]["day"] = "TODAY"
            two_weeks[0][0]["is_today"] = True
            two_weeks[0][1]["day"] = "%s %d" % (nextday.aMonth(), nextday.day())

            return two_weeks

        return { 'late':      late,
                 'upcomming': upcomming,
                 'completed': completed,
                 'two_weeks': _calculate_two_weeks(),
                 'a_weeks':   _calculate_a_weeks(),
                 'calendar':  _calendar,
                 '_past':     _past_calendar,
               }

    def toggleState(self):
        form = self.request.form
        # info("%r" % form)

        obj = self.context.aq_inner

        wftool = getToolByName(self.context, 'portal_workflow')
        state = wftool.getInfoFor(obj, 'review_state')
        if state == 'active':
            wftool.doActionFor(obj, 'complete')
            obj.setDescription('')
            obj.setProgress(100)
        else:
            wftool.doActionFor(obj, 'activate')
            obj.setProgress(90)

        # 这里仅仅用于调整修改时间
        obj.setModificationDate()
        obj.reindexObject(['modified'])
        self.request.response.redirect(obj.aq_parent.absolute_url())

    def save_milestone(self):
        form = self.request.form
        # info("%r" % form)

        obj = self.context.aq_inner
        end = obj.end()
        deadline = form["deadline"]
        try: 
            deadline = DateTime(deadline.dead_line)
        except:
            #plone_utils = getUtility(IPloneTool)
            plone_utils = getToolByName(self.context, 'plone_utils')
            msg = _(u'${deadline} was error, please changed.', mapping={u'deadline' : deadline.dead_line.split(' ')[0]})
            plone_utils.addPortalMessage(msg, 'error')
            return self.request.response.redirect(obj.aq_parent.absolute_url())
        #deadline   = DateTime(deadline.year, deadline.month, deadline.day)

        m = form["milestone"]
        obj.setTitle(m.title)
        obj.setDeadline(deadline)
        notify = m.has_key("notify") and m["notify"]
        obj.setNotify(notify)
        obj.setResponsibleParty(m.responsible_party)
        
        event.notify(ObjectEditedEvent(obj))
        
        obj.reindexObject()
        if notify:
            sendNotification(self.request, obj)

        if form.has_key("move_upcoming_milestones") and \
                form["move_upcoming_milestones"]:
            move_upcoming_milestones_off_weekends = form.get("move_upcoming_milestones_off_weekends", '')
            shift_days = deadline - end

            portal_catalog = getToolByName(obj, 'portal_catalog')
            path = '/'.join(self.context.aq_inner.aq_parent.getPhysicalPath())
            brains = portal_catalog.searchResults(
                    {'path'        : path,
                     'portal_type' : 'Milestone',
                     'end'         : {"query": [end], "range": "min"},
                    },
                    )
            for b in brains:
                # 不平移自身
                if b.getId == obj.getId():
                    continue

                end = b.end
                target_day = end + shift_days
                if move_upcoming_milestones_off_weekends:
                    while target_day.dow() in (6, 0):
                        target_day += 1
                shift_obj = b.getObject()
                shift_obj.setDeadline(target_day)
                shift_obj.reindexObject()

        self.request.response.redirect(obj.aq_parent.absolute_url())


    def getResponsiblePartyTitle(self, responsor):
        mtool = getToolByName(self.context, 'portal_membership')
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

class AddMilestoneForm(BrowserView):
    """ the add form """

    batch_add_template = ViewPageTemplateFile('batch_add.pt')

    def addOne(self):
        """ submit or show the form """
        m = self.request.get('milestone')
        self._createMilestone(m)
        return self.request.response.redirect(self.context.absolute_url())

    def batchAdd(self):
        """ """
        if not self.request.form.has_key('form.submitted'):
            return self.batch_add_template()
        milestones = self.request.get('milestone', [])
        for m in milestones:
            self._createMilestone(m)
        return self.request.response.redirect(self.context.absolute_url())

    def _createMilestone(self,m):
        deadline = m.dead_line

        if not m.title:
            return 

        try: 
            DateTime(deadline)
        except:
            #plone_utils = getUtility(IPloneTool)
            plone_utils = getToolByName(self.context, 'plone_utils')
            msg = _(u'${milestone} did not create. ${deadline} was error, please changed.', mapping={u'milestone':m.title, u'deadline' : deadline.split(' ')[0]})
            plone_utils.addPortalMessage(msg, 'error')

            return self.request.response.redirect(self.context.absolute_url())

        id = str(random.randrange(100000, 999999))
        while id in self.context:
            id = str(random.randrange(100000, 999999))

        self.context.invokeFactory('Milestone', id)
        o = getattr(self.context, id)

        o.setTitle(m.title)
        o.setDeadline(deadline)
        o.setResponsibleParty(m.get('responsibleParty', ''))
        notify = m.get('notify', False)
        o.setNotify(notify)
        o.reindexObject()

        if notify:
            sendNotification(self.request, o)

# -*- coding: UTF-8 -*-

from plone.app.kss.plonekssview import PloneKSSView
from kss.core import force_unicode

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

class KssView(PloneKSSView):

    edit_template = ZopeTwoPageTemplateFile('edit.pt')

    def edit_milestone(self):
        obj = self.context.aq_inner
        macros = self.edit_template.macros

        content = self.header_macros(the_macro=macros['milestoneitem'] , item=obj)
        #if self.request.get('HTTP_USER_AGENT', '').find('MSIE') != -1:
        #    content = content.strip().replace('<', '&lt;').replace('>', '&gt;')
        content = force_unicode(content, 'utf')

        ksscore = self.getCommandSet('core')
        selector = ksscore.getSelector('parentnodecss', '.Milestone|.edititemwrapper')
        ksscore.replaceInnerHTML(selector, content)
        return self.render()

    def add_progress(self):
        obj = self.context.aq_inner
        macros = self.edit_template.macros

        content = self.header_macros(the_macro=macros['progressitem'] , item=obj)
        content = force_unicode(content, 'utf')

        ksscore = self.getCommandSet('core')
        selector = ksscore.getSelector('parentnodecss', '.Milestone|.edititemwrapper')
        ksscore.replaceInnerHTML(selector, content)
        return self.render()

    def submitProgress(self, comment, progress=0):
        obj = self.context.aq_inner

        wftool = getToolByName(obj, 'portal_workflow')
        action_comment = '[%d%%] %s' %(progress, comment)

        action = 'report'
        if progress == 100:
            state = wftool.getInfoFor(obj, 'review_state')
            if state == 'active':
                action = 'complete'

        wftool.doActionFor(obj, action, comment=action_comment)

        if progress > 100 or progress < 0:
            raise 'progress should less than 100'

        obj.setProgress(progress)
        obj.setDescription(comment)

        obj.reindexObject()

        ksscore = self.getCommandSet('core')
        selector = ksscore.getSelector('parentnodecss', '.showhide|.bigInput')
        self.getCommandSet('zopen').clear(selector)

        selector = ksscore.getSelector('parentnodecss', '.kssDeletionRegion|.TGsubmitprogress')
        ksscore.toggleClass(selector, 'hideme')

        history = wftool.getInfoFor(obj, 'review_history', [])
        history = [review for review in history if review.get('action','')]

        newline = translate(_(u'progress_newline', 
            default='${len_history}, Just now, <span style=\"color:blue\">I</span> <span style=\"color: green\">report:</span>: ${action_comment}<br />',
            mapping={'len_history':str(len(history) + 1), 'action_comment':action_comment}),context=self.request)
        ksscore.insertHTMLBefore(ksscore.getSelector('parentnode', 'form'), newline)

        new_progress = translate(_(u'new_progress', 
                                 default='Progress: ${progress}% ${comment}', 
                                 mapping={'progress':str(progress), 'comment':comment}),
                                 context=self.request)
        ksscore.replaceInnerHTML(ksscore.getSelector('parentnodecss', '.kssDeletionRegion|.currentProgress'), new_progress)

        if progress == 100:
            self.getCommandSet('zopen').redirect(url=obj.aq_parent.absolute_url())
        return self.render()

