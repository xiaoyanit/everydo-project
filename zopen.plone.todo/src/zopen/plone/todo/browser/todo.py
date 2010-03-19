import random, cStringIO
import posixpath
from ZTUtils import make_query
from AccessControl import getSecurityManager
from Products.Five import BrowserView
from zope.interface import implements
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.intelligenttext.transforms import convertWebIntelligentPlainTextToHtml
from utils import TodoAclBaseView
from zopen.plone.todo.utils import transformToRichTitle
from DateTime import DateTime
from DocumentTemplate import sequence as Sequence 

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('zopen.todo')
from zope.i18n import translate

import logging; info = logging.getLogger('zopen.todo').info

class TodoListView(BrowserView, TodoAclBaseView):

    def getFullLists(self):

        # 先添加的在最上面！
        path = '/'.join(self.context.getPhysicalPath())
        ctool = getToolByName(self.context, 'portal_catalog')
        todolists = ctool.searchResults(
                          path = path, 
                          portal_type = 'TodoList',
                          sort_on = 'getObjPositionInParent',
                          sort_order = 'reverse',)

        _dict = {}
        for todolist in todolists:
            _dict[todolist.getPath()] = ([], [])

        activeitems = ctool.searchResults(
               path = path,
               portal_type = 'TodoItem',
               review_state = 'active',
               sort_on = 'getObjPositionInParent',
               )

        for item in activeitems:
            todopath = posixpath.dirname(item.getPath())
            if todopath in _dict:
                _dict[todopath][0].append(item)

        activepaths = _dict.keys()

        # 按照修改时间反序排序
        completeditems = ctool.searchResults(
               # path = activepaths,
               path = path,
               portal_type = 'TodoItem',
               review_state = 'completed',
               sort_on = 'modified',
               sort_order = 'reverse')

        for item in completeditems:
            todopath = posixpath.dirname(item.getPath())
            if todopath in _dict:
                _dict[todopath][1].append(item)

        active_l, completed_l = [], []
        responsibleparty = self.request.get('getResponsibleParty', '')

        # 加一个判断，当传过来的responsibleparty值为ALL时，显示所有的任务
        if responsibleparty == 'ALL':
            responsibleparty = ''

        isStandalone = self.isStandaloneTodo()
        for todolist in todolists:
            active_i, completed_i = _dict[todolist.getPath()]

            # 如果isStandalone, 就全部显示
            # 如果没有completed的，也显示出来的
            if completed_i and not active_i and not isStandalone:
                completed_l.append(todolist)
            else:
                if responsibleparty:
                    active_i = [item for item in active_i if item.getResponsibleParty == responsibleparty]

                    length = len(completed_i)
                    completed_i = [item for item in completed_i if item.getResponsibleParty == responsibleparty]
                    # 补充None, 保持总体数量相同
                    completed_i += [None] * (length - len(completed_i))

                # filter之后，只显示还active的条目
                active_l.append((todolist, active_i, completed_i))

        return active_l, completed_l

class TodoView(BrowserView, TodoAclBaseView):

    def getActiveItems(self):
        responsibleparty = self.request.get('getResponsibleParty', '')

        path = '/'.join(self.context.getPhysicalPath())
        ctool = getToolByName(self.context, 'portal_catalog')

        if responsibleparty:
            return ctool.searchResults(
               path = path,
               portal_type = 'TodoItem',
               review_state='active',
               getResponsibleParty = responsibleparty,
               sort_on = 'getObjPositionInParent')
        else:
            return ctool.searchResults(
               path = path,
               portal_type = 'TodoItem',
               review_state='active',
               sort_on = 'getObjPositionInParent')

    def getCompletedItems(self):
        responsibleparty = self.request.get('getResponsibleParty', '')

        path = '/'.join(self.context.getPhysicalPath())
        ctool = getToolByName(self.context, 'portal_catalog')

        if responsibleparty:
            return ctool.searchResults(
               path=path,
               portal_type = 'TodoItem',
               review_state='completed',
               sort_on = 'modified',
               getResponsibleParty = responsibleparty,
               sort_order = 'reverse')
        else: 
            return ctool.searchResults(
               path=path,
               portal_type = 'TodoItem',
               review_state='completed',
               sort_on = 'modified',
               sort_order = 'reverse')

    def review_state(self):
        ctool = getToolByName(self.context, 'portal_workflow')
        return ctool.getInfoFor(self.context, 'review_state')

class TodoItemView(BrowserView, TodoAclBaseView):
    """"""
    def richDesTitle(self):
        return convertWebIntelligentPlainTextToHtml(self.context.title)


class ReportView(BrowserView):

    def getAllItems(self, getResponsibleParty=''):

        # 先添加的在最上面！
        ctool = getToolByName(self.context, 'portal_catalog')
        active_projects = ctool(portal_type='Project', review_state='active')
        paths = [p.getPath() for p in active_projects]

        results = ctool.searchResults(
               path = paths,
               portal_type = 'TodoItem',
               review_state = 'active',
               sort_on = 'getObjPositionInParent',
               getResponsibleParty=[getResponsibleParty],
               )

        allitems = {}
        for item in results:
            path = item.getPath().split('/')
            projectid = path[-4]
            listid = path[-2]

            if projectid not in allitems:
                allitems[projectid] = {listid:[item]}
            else:
                projectitems = allitems[projectid]
                if listid not in projectitems:
                    projectitems[listid] = [item]
                else:
                    projectitems[listid].append(item)
        return allitems

    def getAllItemsByDue(self, getResponsibleParty=''):

        now = DateTime()
        today = DateTime(now.year(), now.month(), now.day())

        ctool = getToolByName(self.context, 'portal_catalog')

        #在站点首页显示所有项目的活动任务，在项目中仅显示当前项目（或任务列表）的活动任务
        if self.context.getPortalTypeName()=='Plone Site':
            active_projects = ctool(portal_type='Project', review_state='active')
            paths = [p.getPath() for p in active_projects]
        else:
            paths = '/'.join(self.context.getPhysicalPath())

        # 加一个判断，可让按时间分组的任务显示所有的任务
        if getResponsibleParty=='ALL':
            results = ctool.searchResults( path = paths, portal_type = 'TodoItem', review_state = 'active',)
        else:
            results = ctool.searchResults(
               path = paths,
               portal_type = 'TodoItem',
               review_state = 'active',
               getResponsibleParty=[getResponsibleParty],
               )

        last_items, today_items, tomorrow_items, this_week_items, next_week_items, other_items, no_end_items = [], [], [], [], [], [], [] 
        for item in results:
            path = item.getPath().split('/')
            projectid = path[-4]
            listid = path[-2]
            item_info = (item, projectid, listid)

            if not item.end:
                no_end_items.append(item_info)

            else:
                item_end = item.end
                end_time = DateTime(item_end.year(), item_end.month(), item_end.day())

                dow = today.dow()
                to_date = end_time - today

                if to_date < 0:
                    last_items.append(item_info)
                elif to_date == 0:
                    today_items.append(item_info)
                elif to_date == 1:
                    tomorrow_items.append(item_info)
                elif to_date in range(2, 8):
                    this_week_items.append(item_info) 
                elif to_date in range(9, 15):
                    next_week_items.append(item_info)
                else:
                    other_items.append(item_info)

        last_items.sort(lambda x,y:cmp(x[0].end, y[0].end))
        this_week_items.sort(lambda x,y:cmp(x[0].end, y[0].end))
        next_week_items.sort(lambda x,y:cmp(x[0].end, y[0].end))
        other_items.sort(lambda x,y:cmp(x[0].end, y[0].end))
        
        return last_items, today_items, tomorrow_items, this_week_items, next_week_items, other_items, no_end_items     

    def getRichTitle(self, title):
        return transformToRichTitle(title)

    def getProjectInfo(self, projectid):
        project = getattr(self.context.projects, projectid)
        return {'title':project.Title(), 'company':project.getCompany().Title(), 'url':project.absolute_url() + '/todos'}

    def getListInfo(self, projectid, listid):
        project = getattr(self.context.projects, projectid)
        todolist = getattr(project.todos, listid)
        return {'title':todolist.Title(), 'url':todolist.absolute_url()}

    def getResponsibleInfo(self):
        if not self.request.has_key('getResponsibleParty'):
            mtool = getToolByName(self.context, 'portal_membership')
            id = mtool.getAuthenticatedMember().getId()
        else: 
            id = self.request.get('getResponsibleParty')
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
        ctool = getToolByName(self.context, 'portal_catalog')
        r = ctool(portal_type='TodoItem', review_state='active')
        for rp in set([b.getResponsibleParty for b in r]):
            if rp in persons:
                responsibles.append( (rp, persons[rp]))

        return responsibles

    def csv_url(self):
        q_str = make_query(self.request.form)

        return self.context.absolute_url() + '/todo-export.csv?' + q_str


    def csv(self):
        path = '/'.join(self.context.getPhysicalPath())

        portal_cat = getToolByName(self.context, 'portal_catalog')
        brains = portal_cat.searchResults(
                path=path,
                portal_type = 'TodoItem',
                sort_on = 'created',
                sort_order = 'reverse',
                )

        out = cStringIO.StringIO()
        out_title = translate(_(u'out_title', default='TODO LIST,TODO,RESPONSIBLE,CREATE-TIME,DEADLINE,COMPLETE-TIME,STATE'),context=self.request)
        #print >> out, "任务列表,任务,负责人,创建人,创建时间,截止时间,完成时间,状态"
        print >> out, out_title
        now = DateTime()
        today = DateTime(now.year(),now.month(),now.day())

        mtool = getToolByName(self.context,'portal_membership')
        for b in brains:
            if b.end:
                item_end = b.end
            else:
                item_end = ''

            if b.review_state == 'completed':
                #state = '完成'
                state = translate(_(u'todo_completed',default="Completed"),context=self.request)
                completed_time = b.ModificationDate
            else:
                completed_time = '' 
                if b.end and b.end<today:
                    state = translate(_(u'todo_late',default="Late"),context=self.request)
                   # state = '迟办'
                else:
                    state = translate(_(u'todo_active',default="Active"),context=self.request)
                    #state = '待办'
            print >> out, '"%s","%s","%s","%s","%s","%s","%s","%s"' % (b.getObject().aq_inner.aq_parent.Title(),b.Title,self.getMemberGroupName(b.getResponsibleParty),self.getMemberGroupName(b.Creator),b.CreationDate,item_end,completed_time,state)
        outenc = "gb18030"
        response = self.request.response
        response.setHeader('Content-Type','text/csv;charset=%s' % outenc)
        response.setHeader('Content-Disposition', 'attachment; filename=todo-export.csv')

        return unicode(out.getvalue(), 'utf-8').encode(outenc)
                
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

