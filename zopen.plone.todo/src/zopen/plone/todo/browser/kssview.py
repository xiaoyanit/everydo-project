import random
from DateTime import DateTime
from zope import lifecycleevent, event
from zope.component import getUtility

from Products.CMFCore.utils import getToolByName

from Products.Five import BrowserView

from kss.core import force_unicode
from plone.app.kss.plonekssview import PloneKSSView

from archetypes.kss.fields import FieldsView 
from Products.Archetypes.event import ObjectEditedEvent
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
 
from zopen.plone.filerepos.interfaces import IFileManager
from zopen.plone.widgets.category.interfaces import ICategoryManager
from zopen.plone.subscription.interfaces import ISubscriptionManager
from zopen.plone.filerepos.browser.filerepos import isNullFileField

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('zopen.todo')
from zope.i18n import translate

try:
    from zopen.plone.timetracker.utils import parseHour
except ImportError:
    pass

from todo import TodoView

from utils import reorderFolderContents, TodoAclBaseView

macros_todo = ZopeTwoPageTemplateFile('macros_todo.pt')
macros_todo_more = ZopeTwoPageTemplateFile('todoitem_view.pt')

def sendNotification(self, todoitem):
        rp = todoitem.getResponsibleParty()
        if not rp:
            return

        mtool = getToolByName(todoitem, 'portal_membership')
        member_rp = mtool.getMemberById(rp)
        rp_email = member_rp and member_rp.getProperty('email')
        if not rp_email:
            return

        project = todoitem.getProject()
        company = project.getCompany()
        todolist = todoitem.aq_parent
        project_title = project.Title()
        subject = translate(_(u'mail_subject', default='[${project_title}] To-do item assigned to you', mapping={u'project_title':project_title}), context=self.request)

        member = mtool.getAuthenticatedMember()
        fullname = member.getProperty('fullname')
        email = member.getProperty('email')

        end = todoitem.end()
        if end:
            deadline_info = translate(_(u'deadline_info',
                                        default='.\nTo complete this to-do no later than ${end}',
                                        mapping={u'end':str(end)}),
                                        context=self.request)
                                        
        else:
            deadline_info = ''

        body = translate(_(u'mail_body', 
                           default='---------------------------------------------------------------\nCompany: ${company_name}\nProject: ${project_name}\n---------------------------------------------------------------\n\nYou have just been assigned the following to-do item\nby ${user_name} <${user_email}>${deadline_info}:\n\n${todoitem_title}\n\n${todoitem_description}\n\n--\nTo view this to-do list, visit:\n${todolist_url}', mapping={u'todolist_url':todolist.absolute_url(),
                                   u'user_name':fullname or member.getId(),
                                   u'user_email':email,
                                   u'company_name':company.Title(),
                                   u'project_name':project_title,
                                   u'todoitem_title':todoitem.Title(),
                                   u'deadline_info':deadline_info,
                                   u'todoitem_description':todoitem.Description()}),
                          context=self.request)

        portal = getToolByName(todolist, 'portal_url').getPortalObject()
        mfrom = '"%s" <%s>' % (portal.email_from_name, portal.email_from_address)

        mh = getToolByName(todolist, 'MailHost')
        mh.secureSend(body, mto=rp_email,
                mfrom=mfrom,subject=subject, charset='UTF-8')

def createMilestone(folder, title, deadline, responsibleParty='', notify=False):
        id = str(random.randrange(100000, 999999))
        mf = folder.aq_parent.milestones
        while id in mf:
            id = str(random.randrange(100000, 999999))

        mf.invokeFactory('Milestone', id)
        o = getattr(mf, id)

        o.setTitle(title)
        o.setDeadline(deadline)
        o.setResponsibleParty(responsibleParty)
        o.setNotify(notify)
        o.reindexObject()

class KssView(PloneKSSView, TodoAclBaseView):

    def reorderLists(self, orderstring):
        reorderFolderContents(self.context, orderstring, reverse=True)

        ksscore = self.getCommandSet('core')
        ksscore.replaceHTML("#list-info", 'done')
        return self.render()

    def reorderItems(self, orderstring):
        reorderFolderContents(self.context, orderstring)

        ksscore = self.getCommandSet('core')
        ksscore.replaceHTML("#list-info", 'done')
        return self.render()

    def completeTodoItem(self):
        wftool = getToolByName(self.context, 'portal_workflow')
        wftool.doActionFor(self.context, 'complete')

        # 这里仅仅用于调整修改时间
        self.context.setModificationDate()
        self.context.reindexObject(['modified'])

        ksscore = self.getCommandSet('core')
        ksscore.deleteNode(ksscore.getParentNodeSelector(".kssDeletionRegion"))

        macro = macros_todo.macros['completed']
        content = self.header_macros(the_macro=macro,
                item = self.context)
        content = force_unicode(content, 'utf')
        listid = self.context.aq_inner.aq_parent.getId()
        ksscore.insertHTMLAsFirstChild('#completed_' + listid, content)

        effects = self.getCommandSet('effects')
        selector = '#item_%s' % self.context.getId()
        #effects.effect(selector, 'highlight')

        return self.render()

    def completeTodoItemMore(self):
        wftool = getToolByName(self.context, 'portal_workflow')

        state = wftool.getInfoFor(self.context, 'review_state', '')

        if state == 'active': 
            wftool.doActionFor(self.context, 'complete')

        elif state == 'completed':
            wftool.doActionFor(self.context, 'activate')

        # 这里仅仅用于调整修改时间
        self.context.setModificationDate()
        self.context.reindexObject(['modified'])

        ksscore = self.getCommandSet('core')

        macro =macros_todo_more.macros['todo_more_completed']
        content = self.header_macros(the_macro=macro,
                obj = self.context)
        content = force_unicode(content, 'utf')

        ksscore.replaceHTML('#todo_is_completed', content)

        return self.render()


    def activeTodoItem(self):
        listid = self.context.aq_inner.aq_parent.getId()
        ksscore = self.getCommandSet('core')

        wftool = getToolByName(self.context, 'portal_workflow')
        # self.context.setDescription(self.context.aq_inner.aq_parent.Title())
        wftool.doActionFor(self.context, 'activate') 

        ksscore.deleteNode(ksscore.getParentNodeSelector(".kssDeletionRegion"))

        macro = macros_todo.macros['active']
        content = self.header_macros(the_macro=macro,
                item = self.context)
        content = force_unicode(content, 'utf')
        ksscore.insertHTMLAsLastChild('#active_' + listid, content)

        self.getCommandSet('todo').sortTodoItems()

        effects = self.getCommandSet('effects')
        selector = '#item_%s' % self.context.getId()
        #effects.effect(selector, 'highlight')
        return self.render()

    def _addTodolist(self, id, title, description, tracked=False, private=False, milestone=''):
        """Create Todo List"""

        self.context.invokeFactory('TodoList', id)
        o = getattr(self.context, id)
        o.setTitle(title)
        o.setDescription(description)
        o.setTracked(tracked)
        o.reindexObject()

        wftool = getToolByName(self.context, 'portal_workflow')
        if private:
            wftool.doActionFor(o, 'hide')

        if milestone:
            ctool = getToolByName(self.context, 'portal_catalog')
            brains = ctool(UID = milestone)
            if brains:
                m = brains[0].getObject()
                m.addRelatedItem( o.UID() )
                m.indexObject()

        return o 


    def addTodolist(self, title='', template_id='', description='', tracked=False, private=False, is_template=False, milestone=''):
        activeitems = [] 
        id = str(random.randrange(100000, 999999))
        while id in self.context.objectIds():
            id = str(random.randrange(100000, 999999))

        if not title:
            if not template_id:
                ksscore = self.getCommandSet('core')
                ksscore.toggleClass(ksscore.getSelector('parentnodecss', '.TGnewlist|.submit'), 'hideme')
                return self.render()
            else:
                portal = getToolByName(self.context, 'portal_url').getPortalObject()
                template_folder = portal.templates.todos
                template_todolist = getattr(template_folder, template_id)
                todolist_title = template_todolist.Title()
                if not description:
                   description = template_todolist.Description() 

                todolist = self._addTodolist(id, todolist_title, description, tracked, private, milestone)

                folder_path = '/'.join(template_todolist.getPhysicalPath())
                ctool = getToolByName(self.context, 'portal_catalog')
                all_items = ctool.searchResults(path=folder_path, portal_type = 'TodoItem')
                
                for todo in all_items:
                    title = todo.getObject().richTitle() 
                    item_id = str(random.randrange(100000, 999999))
                    all_ids = [b.getId for b in all_items]
                    while item_id in all_ids:
                        item_id = str(random.randrange(100000, 999999))
                    self._addTodoItem(todolist, item_id, title, notify=False, responsibleParty='', subject='', endDate='', year='', month='', day='', createmilestone=False)

                activeitems = todolist.objectValues() 

        else:
            self._addTodolist(id, title, description, tracked, private, milestone)

        o = getattr(self.context, id)
        wftool = getToolByName(self.context, 'portal_workflow')
        review_state = wftool.getInfoFor(o,'review_state')

        macro = macros_todo.macros['todolist']

        content = self.header_macros(the_macro=macro,
                todolist = o,
                review_state = review_state,
                isAdding = 1,
                activeitems = activeitems,
                completeditems = [],
                is_template = is_template=='True')

        #if self.request.get('HTTP_USER_AGENT', '').find('MSIE') != -1:
        #    content = content.strip().replace('<', '&lt;').replace('>', '&gt;')
        content = force_unicode(content, 'utf')

        listid = self.context.getId()
        ksscore = self.getCommandSet('core')
        ksszopen=self.getCommandSet('zopen')

        ksscore.deleteNode('#blank-sample')

        ksszopen.clear(ksscore.getSelector('parentnodecss', '.TGnewlist|.TGclear'))
        ksscore.toggleClass('.TGnewlist', 'hideme')
        ksscore.toggleClass(ksscore.getSelector('parentnodecss',
            '.TGnewlist|.submit'), 'hideme')

        ksscore.insertHTMLAsFirstChild('#fulllists', content)
        ksscore.focus( '#list_%s .new_item_title' % id )

        self.getCommandSet('todo').sortTodoItems()

        return self.render()

    def _addTodoItem(self, folder, id, title='', notify=False, responsibleParty='',\
            subject='', endDate='', year='', month='', day='', createmilestone=False):
        """Create Todo Item"""

        ksscore = self.getCommandSet('core')



        folder.invokeFactory('TodoItem', id)
        o = getattr(folder, id)
        o.setTitle(title)
        # o.setDescription(self.context.Title())
        if subject:
            o.setSubject([subject])
        if endDate is not None:
            o.setEndDate(endDate)
        if responsibleParty:
            o.setResponsibleParty(responsibleParty)

        o.reindexObject()

        if notify:
            sendNotification(self, o)

        # 将创建人和负责人做为任务的订阅人
        p = [o.getResponsibleParty(), o.Creator()]
        sm = ISubscriptionManager(o)
        sm.setSubscribedMembers(p)
        
        if createmilestone and endDate:
             folder_aq = folder.aq_inner.aq_parent
             createMilestone(folder_aq, title, endDate, responsibleParty, notify=False)
             
        return o


    def addTodoItem(self, title='', notify=False, responsibleParty='',\
            subject='', endDate='', year='', month='', day='',
            createmilestone=False, is_template=False):

        ksscore = self.getCommandSet('core')
        if not title:
            ksscore.toggleClass(ksscore.getSelector('parentnodecss', '.TGadditem|.submit'), 'hideme')
            return self.render()

        endDate = self.getDate(endDate, year, month, day)

        if endDate == 'Error':
            error = translate(_(u'va_deadline_error',default='Deadline is invalid, please correct.'), context=self.request)
            error = error.decode('utf', 'replace')
            ksscore.replaceInnerHTML(ksscore.getSelector('parentnodecss', '.TGadditem|.errmsg'), error)
            ksscore.addClass(ksscore.getSelector('parentnodecss', '.TGadditem|.errmsg'), 'error')
            ksscore.toggleClass(ksscore.getSelector('parentnodecss', '.TGadditem|.submit'), 'hideme')
            return self.render()
        else:
            ksscore.replaceInnerHTML(ksscore.getSelector('parentnodecss', '.TGadditem|.errmsg'), '')
            ksscore.removeClass(ksscore.getSelector('parentnodecss', '.TGadditem|.errmsg'), 'error')

        folder = self.context.aq_inner.aq_parent
        folder_path = '/'.join(folder.getPhysicalPath())
        ctool = getToolByName(self.context, 'portal_catalog')
        all_items = ctool.searchResults( path=folder_path, portal_type = 'TodoItem')
        all_ids = [b.getId for b in all_items]

        id = str(random.randrange(100000, 999999))
        while id in all_ids:
            id = str(random.randrange(100000, 999999))

        self._addTodoItem(self.context, id, title, notify, responsibleParty, subject, endDate, year, month, day, createmilestone)

        o = getattr(self.context, id)

        macro = macros_todo.macros['active']
        content = self.header_macros(the_macro=macro,
                item = o,
                is_template = is_template=='True')
        content = force_unicode(content, 'utf')
        listid = self.context.getId()
        ksscore = self.getCommandSet('core')
        ksscore.insertHTMLAsLastChild('#active_' + listid, content)

        ksszopen=self.getCommandSet('zopen')
        self.getCommandSet('todo').sortTodoItems()

        ksscore.toggleClass(ksscore.getSelector('parentnodecss', '.TGadditem|.submit'), 'hideme')
        ksszopen.clear(ksscore.getSelector('parentnodecss', '.TGadditem|.new_item_title'))
        # ksscore.focus(ksscore.getSelector('parentnodecss','.TGadditem|.new_item_title'))
        return self.render()

    def editItem(self, is_template=False):
        macro = macros_todo.macros['edititem']
        content= self.header_macros(the_macro=macro,
                                    item = self.context.aq_inner,
                                    is_template = is_template=='True')
        #if self.request.get('HTTP_USER_AGENT', '').find('MSIE') != -1:
        #    content = content.strip().replace('<', '&lt;').replace('>', '&gt;')
        content = force_unicode(content, 'utf')

        ksscore = self.getCommandSet('core')
        # hide
        itemtext = ksscore.getSelector('parentnodecss','div.kssDeletionRegion|.itemtext')
        ksscore.addClass(itemtext, 'hideme')

        wrapper = ksscore.getSelector('parentnodecss','div.kssDeletionRegion|.TGcomplete')
        ksscore.toggleClass(wrapper, 'hideme')

        formwrapper = ksscore.getSelector('parentnodecss','div.kssDeletionRegion|div.edititemwrapper')
        ksscore.replaceInnerHTML(formwrapper, content)

        ksscore.focus(ksscore.getSelector('parentnodecss','div.kssDeletionRegion|.edit_item_title') )
        return self.render()


    def editList(self, is_template=False):
        macro = macros_todo.macros['editlist']
        context = self.context.aq_inner

        wrapperid = "editlist-%s" % context.getId()
        wftool = getToolByName(self.context, 'portal_workflow')
        review_state = wftool.getInfoFor(context, 'review_state')

        content= self.header_macros(the_macro=macro,
                                    todolist = context,
                                    review_state=review_state,
                                    is_template = is_template=='True')
        #if self.request.get('HTTP_USER_AGENT', '').find('MSIE') != -1:
        #    content = content.strip().replace('<', '&lt;').replace('>', '&gt;')
        content = force_unicode(content, 'utf')
        ksscore = self.getCommandSet('core')
        
        # show
        ksscore.toggleClass(ksscore.getSelector('parentnodecss','.todolist|.TGeditlist'),
                'hideme')

        # hide
        itemtext = ksscore.getSelector('parentnode','div.todolist')
        ksscore.toggleClass(itemtext, 'hideme')

        wrapper = """<div id="%s" class="editlistformwrapper"></div>""" % wrapperid

        ksscore.insertHTMLBefore(itemtext, wrapper)
        ksscore.replaceInnerHTML('#' + wrapperid, content)
        ksscore.focus('#editlist_%s .list_title' % context.getId() )
        return self.render()

    def saveList(self, title, description, tracked=False, private=False, is_template=False, milestone=''):
        context = self.context.aq_inner

        context.setTitle(title)
        context.setDescription(description)
        context.setTracked(tracked)
        wftool = getToolByName(self.context, 'portal_workflow')
        review_state = wftool.getInfoFor(context, 'review_state')
        context.reindexObject()

        if(private != False and review_state != 'private'): 
            wftool.doActionFor(context, 'hide')
            review_state= wftool.getInfoFor(context, 'review_state')
        elif(review_state == 'private' and private == False):
            wftool.doActionFor(context, 'show')
            review_state= wftool.getInfoFor(context, 'review_state')

        ctool = getToolByName(context, 'portal_catalog')
        if context.getRelatedMilestones():
            for uid in context.getRelatedMilestoneUIDs():
                brains = ctool(UID = uid)
                m = brains[0].getObject()
                m.removeRelatedItem(context.UID())
                m.indexObject()

        if milestone:
            brains = ctool(UID = milestone)
            if brains:
                m = brains[0].getObject()
                m.addRelatedItem(context.UID())
                m.indexObject()

        ksscore = self.getCommandSet('core')
        ksscore.deleteNode(ksscore.getSelector('parentnode', '.editlistformwrapper'))

        listid = "#list_%s" % context.getId()

        macro = macros_todo.macros['todolist']
        todoview = TodoView(context, self.request)
        content = self.header_macros(the_macro=macro,
                todolist = context,
                review_state = review_state,
                isAdding = 0,
                activeitems = todoview.getActiveItems(),
                completeditems = todoview.getCompletedItems(),
                is_template = is_template=='True')
        ksscore.replaceHTML(listid, content)

        self.getCommandSet('todo').sortTodoItems()

        return self.render()

    def _saveItem(self, title='', responsibleParty='', notify=False,\
            subject='', endDate='', year='', month='', day='', createmilestone=False, is_template=False):
        context = self.context.aq_inner
        ksscore = self.getCommandSet('core')
        context.setTitle(title)
        context.setResponsibleParty(responsibleParty)
        subject = subject and [subject] or []
        context.setSubject(subject)
        context.setEndDate(endDate)
        context.reindexObject()


        if notify:
            sendNotification(self, context)

        folder = context.aq_parent.aq_parent
        if createmilestone and endDate:
             createMilestone(folder, title, endDate, responsibleParty, notify=False)

        return context

    def saveItem(self, title='', responsibleParty='', notify=False,\
           subject='', endDate='', year='', month='', day='', createmilestone=False, is_template=False):
        
        ksscore = self.getCommandSet('core')
        endDate = self.getDate(endDate, year, month, day)

        if endDate == 'Error':
            error = translate(_(u'deadline_error',default='Deadline is invalid, please correct.'), context=self.request)
            error = error.decode('utf', 'replace')
            ksscore.replaceInnerHTML(ksscore.getSelector('parentnodecss', '.edititem|.errmsg'), error)
            ksscore.addClass(ksscore.getSelector('parentnodecss', '.edititem|.errmsg'), 'error')
            ksscore.toggleClass(ksscore.getSelector('parentnodecss', '.edititem|.submit'), 'hideme')
            return self.render()
        else:
            ksscore.replaceInnerHTML(ksscore.getSelector('parentnodecss', '.edititem|.errmsg'), '')
            ksscore.removeClass(ksscore.getSelector('parentnodecss', '.edititem|.errmsg'), 'error')


        context = self._saveItem(title, responsibleParty, notify,\
                subject, endDate, year, month, day, createmilestone, is_template) 

        macro = macros_todo.macros['active']
        content = self.header_macros(the_macro=macro,
                item = context,
                is_template = is_template=='True')
        content = force_unicode(content, 'utf')

        ksscore = self.getCommandSet('core')
        ksscore.replaceHTML('#item_' + context.getId(), content)

        self.getCommandSet('todo').sortTodoItems()
        return self.render()

    def saveItemMore(self, title='', responsibleParty='', notify=False,\
           subject='', endDate='', year='', month='', day='', createmilestone=False, is_template=False):
        
        ksscore = self.getCommandSet('core')
        endDate = self.getDate(endDate, year, month, day)

        if endDate == 'Error':
            error = translate(_(u'deadline_error',default='Deadline is invalid, please correct.'), context=self.request)
            error = error.decode('utf', 'replace')
            ksscore.replaceInnerHTML(ksscore.getSelector('parentnodecss', '.edititem|.errmsg'), error)
            ksscore.addClass(ksscore.getSelector('parentnodecss', '.edititem|.errmsg'), 'error')
            ksscore.toggleClass(ksscore.getSelector('parentnodecss', '.edititem|.submit'), 'hideme')
            return self.render()
        else:
            ksscore.replaceInnerHTML(ksscore.getSelector('parentnodecss', '.edititem|.errmsg'), '')
            ksscore.removeClass(ksscore.getSelector('parentnodecss', '.edititem|.errmsg'), 'error')

        context = self._saveItem(title, responsibleParty, notify,\
                subject, endDate, year, month, day, createmilestone, is_template) 

         
        macro = macros_todo_more.macros['todo_more']
        content = self.header_macros(the_macro=macro,
                item = context)
       
        content = force_unicode(content, 'utf')

        ksscore = self.getCommandSet('core')
        ksscore.replaceHTML('#todo_more', content)

        return self.render()

    def trackItem(self, is_todolist=True):
        context = self.context.aq_inner
        hours = 0
        timelogs = [t for t in context.getRelatedItems() if t.portal_type=='TimeLog']
        for timelog in timelogs:
            hours += timelog.getHours()

        if is_todolist==True:
            macro = macros_todo.macros['trackitem']
        else:
            macro = macros_todo.macros['trackitemmore']
        content= self.header_macros(the_macro=macro, 
                item = context,
                hours = hours)
        #if self.request.get('HTTP_USER_AGENT', '').find('MSIE') != -1:
        #    content = content.strip().replace('<', '&lt;').replace('>', '&gt;')
        content = force_unicode(content, 'utf')

        ksscore = self.getCommandSet('core')
        # hide
        itemtext = ksscore.getSelector('parentnodecss','div.kssDeletionRegion|.itemtext')
        ksscore.toggleClass(itemtext, 'hideme')

        wrapper = ksscore.getSelector('parentnodecss','div.kssDeletionRegion|.TGcomplete')
        ksscore.toggleClass(wrapper, 'hideme')

        wrapper = ksscore.getSelector('parentnodecss','div.kssDeletionRegion|.TGactivate')
        ksscore.toggleClass(wrapper, 'hideme')

        if is_todolist==True:
            formwrapper = ksscore.getSelector('parentnodecss','div.kssDeletionRegion|div.edititemwrapper')
        else:
            formwrapper = ksscore.getSelector('parentnodecss','div.kssDeletionRegion|div.edititemwrappertracker')
        ksscore.replaceInnerHTML(formwrapper, content)

        ksscore.focus(ksscore.getSelector('parentnodecss','div.kssDeletionRegion|.hourInput') )
        return self.render()

    def _addTrack(self,year,month,day,responsibleParty,hours,title):
        core = self.getCommandSet('core')
        
        context = self.context.aq_inner
        tracker = context.getProject().time
        random_id = str(random.randrange(100000, 999999))

        ids = tracker.objectIds()
        while random_id in ids:
            random_id = str(random.randrange(100000, 999999))

        deadline = DateTime(year, month, day)

        tracker.invokeFactory('TimeLog', random_id)
        o = getattr(tracker, random_id)

        o.setTitle(title)
        o.setDate(deadline)
        o.setResponsibleParty(responsibleParty)

        o.setHours(parseHour(hours))
        o.setRelatedItems([context])
        o.setDescription(context.Title().decode('utf-8')[:30])
        o.reindexObject()

        return o


    def addTrack(self,year,month,day,responsibleParty,hours,title):
        core = self.getCommandSet('core')
        context = self.context.aq_inner
         
        error_hour, error_date = '',''
        try:
            deadline = DateTime(year, month, day)
            core.replaceInnerHTML(core.getSelector('parentnodecss', '.trackitem|.errmsgDate'), '')
            core.removeClass(core.getSelector('parentnodecss', '.trackitem|.errmsgDate'), 'error')
        except:
            error_date = translate(_(u'va_date_error', default='Date is invalid, please currect.'), context=self.request)


        if hours == '':
            error_date = translate(_(u'va_need_hour', default='Need hour!'), context=self.request)
        else:
            try:
                parseHour(hours)
                core.replaceInnerHTML(core.getSelector('parentnodecss', '.trackitem|.errmsgHour'), '')
                core.removeClass(core.getSelector('parentnodecss', '.trackitem|.errmsgHour'), 'error')
            except:
                error_date = translate(_(u'va_hour_error', default='Hour is invalid, please currect.'), context=self.request)

        if error_date:
            error_date = error_date.decode('utf', 'replace')
            core.replaceInnerHTML(core.getSelector('parentnodecss', '.trackitem|.errmsgDate'), error_date)
            core.addClass(core.getSelector('parentnodecss', '.trackitem|.errmsgDate'), 'error')
            core.toggleClass(core.getSelector('parentnodecss','.trackitem|.submit'),'hideme')
            return self.render()

        if error_hour:
            error_hour = error_hour.decode('utf', 'replace')
            core.replaceInnerHTML(core.getSelector('parentnodecss', '.trackitem|.errmsgHour'), error_hour)
            core.addClass(core.getSelector('parentnodecss', '.trackitem|.errmsgHour'), 'error')
            core.toggleClass(core.getSelector('parentnodecss','.trackitem|.submit'),'hideme')
            return self.render()


        o = self._addTrack(year,month,day,responsibleParty,hours,title)

        timelogs = context.getRawRelatedItems()
        timelogs.append(o.UID())
        context.setRelatedItems(timelogs)

        wftool = getToolByName(self.context, 'portal_workflow')
        state = wftool.getInfoFor(self.context, 'review_state')
        macro = macros_todo.macros[state]

        content = self.header_macros(the_macro=macro,
                item = context)
        content = force_unicode(content, 'utf')

        ksscore = self.getCommandSet('core')
        ksscore.replaceHTML('#item_' + context.getId(), content)

        return self.render()

    def addTrackMore(self,year,month,day,responsibleParty,hours,title):
        core = self.getCommandSet('core')
        context = self.context.aq_inner
         
        error_hour, error_date = '',''
        try:
            deadline = DateTime(year, month, day)
            core.replaceInnerHTML(core.getSelector('parentnodecss', '.trackitemmore|.errmsgDate'), '')
            core.removeClass(core.getSelector('parentnodecss', '.trackitemmore|.errmsgDate'), 'error')
        except:
            error_date = translate(_(u'va_date_error', default='Date is invalid, please currect.'), context=self.request)


        if hours == '':
            error_date = translate(_(u'va_need_hour', default='Need hour!'), context=self.request)
        else:
            try:
                parseHour(hours)
                core.replaceInnerHTML(core.getSelector('parentnodecss', '.trackitemmore|.errmsgHour'), '')
                core.removeClass(core.getSelector('parentnodecss', '.trackitemmore|.errmsgHour'), 'error')
            except:
                error_date = translate(_(u'va_hour_error', default='Hour is invalid, please currect.'), context=self.request)

        if error_date:
            error_date = error_date.decode('utf', 'replace')
            core.replaceInnerHTML(core.getSelector('parentnodecss', '.trackitemmore|.errmsgDate'), error_date)
            core.addClass(core.getSelector('parentnodecss', '.trackitemmore|.errmsgDate'), 'error')
            core.toggleClass(core.getSelector('parentnodecss','.trackitem|.submit'),'hideme')
            return self.render()

        if error_hour:
            error_hour = error_hour.decode('utf', 'replace')
            core.replaceInnerHTML(core.getSelector('parentnodecss', '.trackitemmore|.errmsgHour'), error_hour)
            core.addClass(core.getSelector('parentnodecss', '.trackitemmore|.errmsgHour'), 'error')
            core.toggleClass(core.getSelector('parentnodecss','.trackitem|.submit'),'hideme')
            return self.render()


        o = self._addTrack(year,month,day,responsibleParty,hours,title)

        timelogs = context.getRawRelatedItems()
        timelogs.append(o.UID())
        context.setRelatedItems(timelogs)

        macro = macros_todo_more.macros['todo_more']

        content = self.header_macros(the_macro=macro,
                item = context)
        content = force_unicode(content, 'utf')

        ksscore = self.getCommandSet('core')
        ksscore.replaceHTML('#todo_more', content)

        return self.render()

    def viewMilestones(self, getResponsibleParty):
        ctool = getToolByName(self.context, 'portal_catalog')

        if self.context.getPortalTypeName()=='Plone Site':
            active_projects = ctool(portal_type='Project', review_state='active')
            paths = [p.getPath() for p in active_projects]
        else:
            paths = '/'.join(self.context.getPhysicalPath())

        if getResponsibleParty=='ALL':
            results = ctool.searchResults( path = paths, portal_type = 'Milestone', review_state = 'active',)
        else:
            results = ctool.searchResults(
               path = paths,
               portal_type = 'Milestone',
               review_state = 'active',
               getResponsibleParty=[getResponsibleParty],
               sort_on = 'end',
               sort_order = 'reverse')

 
        macro = macros_todo.macros['milestones']

        content = self.header_macros(the_macro=macro, milestones=results)
        content = force_unicode(content, 'utf')

        ksscore = self.getCommandSet('core')
        ksscore.replaceInnerHTML('.milestone_table_here', content)

        return self.render()

class UploadFile(BrowserView):
    def uploadFile(self):
        context = self.context.aq_inner
        form = self.request.form
        wftool = getToolByName(self.context, 'portal_workflow')
        review_state = wftool.getInfoFor(context.aq_parent, 'review_state')

        if form.has_key("upload"):
            file_manager = getUtility(IFileManager, 'file_manager')
            filerepos = file_manager.getFilerepos(context)
            files = []
            for request_file in form["upload"]:
                if not hasattr(request_file, 'file'):
                    continue
                file_cat = getattr(filerepos, request_file.category)
                the_file = file_manager.addFile(file_cat, request_file.file)

                if the_file is not None:
                    files.append(the_file)
                    if review_state == 'private':
                        wftool.doActionFor(the_file, 'hide')
            if files:
                items = context.getRelatedItems()
                for f in files:
                    items.append(f)
                context.setRelatedItems(items)
            else:
                isNullFileField(self, '')
                return self.request.response.redirect(context.absolute_url()+'/@@todoitem_view')

        return self.request.response.redirect(context.absolute_url()+'/@@todoitem_view')

