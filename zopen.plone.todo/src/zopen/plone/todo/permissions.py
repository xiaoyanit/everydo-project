"""
关于权限：

添加list
  内部人员 + 管理员

添加item
  内部人员 + 管理员

删除list
  管理员, Owner

删除item
  管理员 + Owner

修改list
  Owner, 管理员

修改item
  responsibleParty(分配Editor角色) + Owner, 管理员

移动list
  内部人员 + 管理员

移动item
  内部人员 + 管理员

"""
from AccessControl.Permissions import add_user_folders as AddUserFolders
from Products.CMFCore.permissions import setDefaultRoles

# Basic permissions
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.permissions import ListFolderContents
from Products.CMFCore.permissions import SetOwnPassword as SetPassword
from Products.CMFCore.permissions import ManageUsers

# Add permissions
AddTodoList                  = "zopen.todo: Add list"
AddTodoItem                  = "zopen.todo: Add item"
AddTodoFolder                = "zopen.todo: Add folder"
MoveItems                    = "zopen.todo: Move items"
MoveLists                    = "zopen.todo: Move lists"
ReportState                  = "zopen.todo: Report state"

setDefaultRoles(AddTodoList, ('Manager', 'Administrator', 'Contributor', 'Owner'))
setDefaultRoles(AddTodoItem, ('Manager', 'Administrator', 'Contributor', 'Owner'))
setDefaultRoles(AddTodoFolder, ('Manager', ))
setDefaultRoles(MoveLists, ('Manager', 'Administrator', 'Editor', 'Owner', 'Reader'))
setDefaultRoles(MoveItems, ('Manager', 'Administrator', 'Editor', 'Owner', 'Reader'))
setDefaultRoles(ReportState, ('Manager', 'Administrator', 'Editor', 'Owner', 'Responsor' ))

DEFAULT_ADD_CONTENT_PERMISSION = AddPortalContent
ADD_CONTENT_PERMISSIONS = {
    'TodoList'     : AddTodoList,
    'TodoItem'     : AddTodoItem,
    'TodoFolder'   : AddTodoFolder,
}

