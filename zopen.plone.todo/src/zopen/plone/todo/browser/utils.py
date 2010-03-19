from Products.CMFCore.utils import getToolByName
from Products.Five.security import checkPermission
from plone.memoize.instance import memoize
from zopen.plone.todo.interfaces import IStandaloneTodo
from AccessControl import SecurityManagement, User
from DateTime import DateTime

def reorderFolderContents(folder, encodedlist, reverse=False):
    # id[]=313128&id[]=800959&id[]=304611&id[]=947600&id[]=588736&id[]=274764
    folder = folder.aq_inner
    encodedlist = encodedlist.strip()
    if not encodedlist:
        return

    ids = [id.split('=')[1] for id in encodedlist.split('&')]
    if reverse:
        ids.reverse()
    ctool = getToolByName(folder, 'portal_catalog')

    existing_ids = folder.objectIds()
    moved_ids = [id for id in ids if id not in existing_ids]
    # print moved_ids, ids, existing_ids
    if moved_ids:
        parent_path = '/'.join(folder.aq_inner.aq_parent.getPhysicalPath())
        brains = ctool(path=parent_path, 
                       portal_type='TodoItem', 
                       getId=moved_ids)
        for b in brains:
            o = b.getObject()
            cutted = o.aq_parent.manage_cutObjects([o.getId()])

            # 解决粘贴的时候权限的问题
            originalSecurityManager = SecurityManagement.getSecurityManager()
            username = originalSecurityManager.getUser().getUserName()
            deliverUser = User.SimpleUser(username,'', ['Manager', 'Owner'], '')
            acl_users = folder.acl_users.aq_inner
            deliverUser = deliverUser.__of__(acl_users)
            SecurityManagement.newSecurityManager(None, deliverUser)

            folder.manage_pasteObjects(cutted) 

            SecurityManagement.setSecurityManager(originalSecurityManager)

    _dict = {}
    unchanged = []
    for obj in folder._objects:
        if obj['id'] not in ids:
            unchanged.append(obj)
        else:
            _dict[obj['id']] = obj

    # 注意，可能传过来了不存在的id, 在对象被删除后会发生!
    ordered = [_dict[id] for id in ids if id in _dict]
    ordered.extend(unchanged)
    folder._objects = tuple(ordered)
    
    # 更新索引
    for id in _dict:
        obj = getattr(folder, id)
        ctool.reindexObject(obj, idxs=['getObjPositionInParent'], update_metadata=1)


class TodoAclBaseView:

    @memoize
    def isStandaloneTodo(self):
        return IStandaloneTodo.providedBy(self.context)

    @memoize
    def canTrack(self):
        if self.isStandaloneTodo():
            return False
        timetracker = self.context.getProject().time
        # 能够查看的人，就能够track
        return checkPermission('zope2.View', timetracker)

    @memoize
    def canAddList(self):
        return checkPermission('zopen.todo.AddList', self.context) 

    @memoize
    def canMoveItems(self):
        return checkPermission('zopen.todo.MoveItems', self.context)

    @memoize
    def canMoveLists(self):
        return checkPermission('zopen.todo.MoveLists', self.context)

    def canAddItem(self, todolist):
        return checkPermission('zopen.todo.AddItem', self.context)

    def canModifyItem(self, obj):
        pass

    def canModifyList(self, obj):
        pass

    def canRemoveItem(self, obj):
        pass

    def canRemoveList(self, obj):
        pass

    @memoize
    def getTodoCategories(self):
        return {
    '':'-',
    'task':'任务',
    'call':'回电',
    'issue':'问题',
    'email':'回邮件',
    'follow-up':'跟进',
    'meeting':'会议',
    }

    def getDate(self, globdate='', new_year='', new_month='', new_day=''):
        today = DateTime()
        year,month,day = today.year(), today.month(), today.day()
        today_start = DateTime(year, month, day)

        if globdate == 'today':
            return today_start
        elif globdate == 'tomorrow':
            return today_start + 1
        elif globdate == 'thisweek':
            dow = today.dow()
            return today_start + 5 - dow
        elif globdate == 'nextweek':
            dow = today.dow()
            return today_start + 12 - dow
        elif globdate == 'later':
            return None
        else:
            if not new_year or not new_month or not new_day:
                return None
            try:
                return DateTime(int(new_year), int(new_month), int(new_day))
            except:
                return 'Error'


