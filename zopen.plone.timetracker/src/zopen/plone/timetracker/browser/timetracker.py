import random, cStringIO
from DateTime import DateTime
from Products.Five import BrowserView
from zope.component import getUtility

from ZTUtils import make_query

from Products.CMFCore.utils import getToolByName

from zopen.plone.timetracker.utils import parseHour
from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
# import logging; info = logging.getLogger('zopen.plone.timetracker').info

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('zopen.timetracker')
from zope.i18n import translate

class TimeTrackerView(BrowserView):

    def getRelatedItemTitle(self):
        rawRelated = self.request.get('relateTo', '')
        portal_cat = getToolByName(self.context, 'portal_catalog')
        brains = portal_cat.searchResults(UID = rawRelated) 
        return brains and brains[0].Title

    def gotoRelated(self):
        timelog = self.context.aq_inner
        todoitems = timelog.getBRefs()
        if todoitems:
            todoitem = todoitems[0]
            self.request.response.redirect(todoitem.absolute_url() +
                    '/' + todoitem.getId())
        else:
            return 'None!'

    def _getBasicQuery(self):
        form = self.request.form

        query = {'portal_type' : 'TimeLog'}
        if form.get("responsibleParty", ''):
            query["getResponsibleParty"] = form["responsibleParty"]

        rawRelated = form.get('relateTo', '')
        if rawRelated:
            query['getRawRelatedItems'] = rawRelated

        if form.has_key('date') and isinstance(form['date'], DateTime):
            query["Date"] = form["date"]
        elif form.has_key("begin") and form.has_key("end"):
            begin_date = form['begin']
            begin_date = DateTime(begin_date.year, begin_date.month, begin_date.day)
            end_date   = form['end']
            end_date   = DateTime(end_date.year, end_date.month, end_date.day)

            query["Date"] = { "query": [begin_date, end_date],
                              "range": "minmax",
                            }
        return query

    def calculateResults(self):
        query = self._getBasicQuery()

        path = '/'.join(self.context.getPhysicalPath())
        query['path'] = path

        portal_cat = getToolByName(self.context, 'portal_catalog')
        brains = portal_cat.searchResults(
                query,
                sort_on = 'created',
                sort_order = 'reverse',
                )

        hours = map(lambda b:b.getHours, brains)
        hours = sum(hours)

        # objects = map(lambda b:b.getObject(), brains)

        q_str = make_query(self.request.form)

        return { "brains": brains, "hours": hours,
                 'csv_url':self.context.absolute_url() + '/time-export.csv?' + q_str}

    def calcReport(self):
        form = self.request.form
        query = self._getBasicQuery()

        if 'Date' not in query:
            query['Date'] = {"query":DateTime() - 8, 'range':'min'}

        ctool = getToolByName(self.context, 'portal_catalog')
        active_projects = ctool(portal_type='Project', review_state='active')
        paths = [p.getPath() for p in active_projects]

        query['path'] = paths
        brains = ctool.searchResults(query)

        allitems = {}
        hours = 0
        for item in brains:
            path = item.getPath().split('/')
            projectid = path[-3]

            if projectid not in allitems:
                allitems[projectid] = [item]
            else:
                allitems[projectid].append(item)
            hours += item.getHours

        q_str = make_query(form)

        return { "brains": allitems, "hours": hours,
                 'csv_url':self.context.absolute_url() + '/time-report.csv?' + q_str}

    def getProjectInfo(self, projectid):
        project = getattr(self.context.projects, projectid)
        company = project.getCompany()
        return {'title':project.Title(),
                'company':company and company.Title() or 'No Company!!',
                'url':project.absolute_url() + '/time'}

    def getAvaResponsibles(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()

        company = portal.companies.owner_company
        persons = {}
        for p in company.contentValues():
            persons[p.getId()] = p.title_or_id()

        return persons.items()

    def csv(self):
        out = cStringIO.StringIO()
        out_title = translate(_(u'out_title', default='DATE,PERSON,HOURS,DESCRIPTION'),context=self.request)
        # print >> out, "DATE,PERSON,HOURS,DESCRIPTION"
        print >> out, out_title

        result = self.calculateResults()
        for b in result["brains"]:
            print >> out, '"%s","%s","%s","%s"' % (b.Date, self.getMemberGroupName(b.getResponsibleParty), b.getHours, b.Title)
        #print >> out, ",TOTAL,%f," % result["hours"]
        out_total = translate(_(u'out_total', default=',TOTAL,${hours}', mapping={u'hours':result["hours"]}), context=self.request)
        print >> out, out_total 

        outenc = "gb2312"
        response = self.request.response
        response.setHeader('Content-Type', 'text/csv; charset=%s' % outenc)
        response.setHeader('Content-Disposition', 'attachment; filename=time-export.csv')

        return unicode(out.getvalue(), 'utf-8').encode('gb18030')

    def csvreport(self):
        out = cStringIO.StringIO()
        out_title = translate(_(u'out_title', default='DATE,PERSON,HOURS,DESCRIPTION'),context=self.request)
        #print >> out, "DATE,PERSON,HOURS,DESCRIPTION"
        print >> out, out_title

        result = self.calculateResults()
        for b in result["brains"]:
            print >> out, '"%s","%s","%s","%s"' % (
                    b.Date, self.getMemberGroupName(b.getResponsibleParty), b.getHours, b.Title)
        #print >> out, ",TOTAL,%f," % result["hours"]
        out_total = translate(_(u'out_total', default=',TOTAL,${hours}', mapping={u'hours':result["hours"]}), context=self.request)
        print >> out, out_total 

        outenc = "gb2312"
        response = self.request.response
        response.setHeader('Content-Type', 'text/csv; charset=%s' % outenc)
        response.setHeader('Content-Disposition', 'attachment; filename=time-export.csv')

        return unicode(out.getvalue(), 'utf-8').encode('gb18030')

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


from plone.app.kss.plonekssview import PloneKSSView
from kss.core import force_unicode
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zopen.plone.widgets.deletion.kssview import KssView

class TimeTrackerKssView(KssView):

    timetracker_template = ZopeTwoPageTemplateFile("timetracker.pt")
    edit_timelog_template = ZopeTwoPageTemplateFile("edit_timelog.pt")

    def add_time_log(self, year, month, day, responsibleParty, hours, title, sum_hours):
        ksscore = self.getCommandSet("core")

        error = ''
        try:
            deadline = DateTime(year, month, day)
        except:
            error = translate(_(u'va_time_error', default='The date ${time} is invalib, please correct.', mapping={u'time':str(year)+'/'+str(month)+'/'+str(day)}), context=self.request)
        if hours == '':
            error += translate(_(u'va_time_need', default="Need Time;"), context=self.request)
        else:
            try:
                parseHour(hours)
            except:
                error += translate(_(u'va_time_invalib', default='Time is invalib, please correct;'), context=self.request)
        if title == '':
            error += translate(_(u'va_description_need', default='Need description;'), context=self.request)
        if error:
            error = error.decode('utf', 'replace')
#            core = self.getCommandSet('core')
#            core.replaceInnerHTML(core.getSelector('parentnodecss', '.documentContent|.errmsg'), error)
#            core.addClass(core.getSelector('parentnodecss', '.documentContent|.errmsg'), 'error')
            ksscore.toggleClass(ksscore.getSelector('parentnodecss','.AddTimeTrack|.submit'),'hideme')
            self.getCommandSet('plone').issuePortalMessage(error,translate(_(u'error'), context=self.request))
            return self.render()

 
        obj = self._createTimelog(year, month, day, responsibleParty, hours, title, sum_hours)

        the_macro = self.timetracker_template.macros["item"]

        content = self.header_macros(the_macro=the_macro,
                item=obj,
                )

        selector = ksscore.getParentNodeSelector("#AddTimeTrack")

        #if self.request.get('HTTP_USER_AGENT', '').find('MSIE') != -1:
        #    content = content.strip().replace('<', '&lt;').replace('>', '&gt;')
        ksscore.insertHTMLAfter("#AddTimeTrack", content)

        ksszopen=self.getCommandSet('zopen')
        ksszopen.clear(ksscore.getSelector('parentnodecss', \
                '.AddTimeTrack|.hours input'))
        ksszopen.clear(ksscore.getSelector('parentnodecss', \
                '.AddTimeTrack|.desc input'))

        sum_hours = float(sum_hours) + obj.getHours()
        ksscore.setAttribute('#sum_hours', name="value", value=str(sum_hours))
        ksscore.toggleClass(ksscore.getSelector('parentnodecss','.AddTimeTrack|.submit'),'hideme')
        return self.render()

    def edit_time_log(self):
        # this only replace a block in the user interface
        itemid = self.context.getId()
        macros = self.edit_timelog_template.macros

        content = self.header_macros(the_macro=macros["item"],
                item=self.context,
                )
        #if self.request.get('HTTP_USER_AGENT', '').find('MSIE') != -1:
        #    content = content.strip().replace('<', '&lt;').replace('>', '&gt;')

        ksscore = self.getCommandSet("core")
        selector = ksscore.getParentNodeSelector(".kssDeletionRegion")
        ksscore.insertHTMLBefore(selector, content)

        content = self.header_macros(the_macro=macros["datecell"], item=self.context)
        #if self.request.get('HTTP_USER_AGENT', '').find('MSIE') != -1:
        #    content = content.strip().replace('<', '&lt;').replace('>', '&gt;')
        ksscore.replaceInnerHTML('#edit-datecell-'+itemid, content)

        content = self.header_macros(the_macro=macros["personcell"], item=self.context)
        #if self.request.get('HTTP_USER_AGENT', '').find('MSIE') != -1:
        #    content = content.strip().replace('<', '&lt;').replace('>', '&gt;')
        ksscore.replaceInnerHTML('#edit-personcell-'+itemid, content)

        # ksscore.insertHTMLBefore('.SectionHeader', '<table>%s</table>' % content)
        ksscore.setStyle(selector, name="display", value="none")

        return self.render()

    def save_time_log(self, year, month, day, responsibleParty, hours, title, sum_hours):

        obj = self.context
        old_hours = obj.getHours()
        
        ksscore = self.getCommandSet("core")

        error = ''
        try:
            deadline = DateTime(year[1], month[1], day[1])
        except:
            error = translate(_(u'va_time_error', default='The date ${time} is invalib, please correct.', mapping={u'time':str(year[1])+'/'+str(month[1])+'/'+str(day[1])}), context=self.request)
        if hours[1] == '':
            error += translate(_(u'va_time_need', default="Need Time;"), context=self.request)
        else:
            try:
                parseHour(hours[1])
            except:
                error += translate(_(u'va_time_invalib', default='Time is invalib, please correct;'), context=self.request)
        if title[1] == '':
            error += translate(_(u'va_description_need', default='Need description;'), context=self.request)
        if error:
            error = error.decode('utf', 'replace')
            ksscore.toggleClass(ksscore.getSelector('parentnodecss','.kssDeletionRegion|.submit'),'hideme')
            self.getCommandSet('plone').issuePortalMessage(error,translate(_(u'error'), context=self.request))
            return self.render()


        obj.setTitle(title[1])
        obj.setDate(deadline)
        obj.setResponsibleParty(responsibleParty[1])
        obj.setHours(parseHour(hours[1]))
        obj.reindexObject()

        the_macro = self.timetracker_template.macros["item"]
        content = self.header_macros(the_macro=the_macro,
                item=obj,
                )

        #if self.request.get('HTTP_USER_AGENT', '').find('MSIE') != -1:
        #    content = content.strip().replace('<', '&lt;').replace('>', '&gt;')

        ksscore = self.getCommandSet("core")
        selector = ksscore.getParentNodeSelector(".kssDeletionRegion")
        ksscore.insertHTMLBefore(selector, content)
        ksscore.deleteNodeAfter(selector)
        ksscore.deleteNode(selector)

        sum_hours = float(sum_hours) - old_hours + obj.getHours()
        ksscore.setAttribute('#sum_hours', name="value", value=str(sum_hours))
        return self.render()

    def delete_time_log(self, selector='.kssDeletionRegion', other=0):
        sum_hours = float(other) - self.context.getHours()
        ksscore = self.getCommandSet("core")
        ksscore.setAttribute('#sum_hours', name="value", value=str(sum_hours))
        return self.kss_obj_delete(selector)

    def _createTimelog(self, year, month, day, responsibleParty, hours, title, sum_hours):
        if not title:
            return

        deadline = DateTime(year, month, day)

        random_id = str(random.randrange(100000, 999999))
        while random_id in self.context:
            random_id = str(random.randrange(100000, 999999))

        self.context.invokeFactory('TimeLog', random_id)
        o = getattr(self.context, random_id)

        o.setTitle(title)
        o.setDate(deadline)
        o.setResponsibleParty(responsibleParty)
        o.setHours(parseHour(hours))
        o.reindexObject()

        return o
