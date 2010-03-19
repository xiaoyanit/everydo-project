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
AddTimeTracker                 = "zopen.timetracker: Add Time Tracker"
AddTimeLog                     = "zopen.timetracker: Add Time Log"
TimeReport                     = "zopen.timetracker: Time Report"

setDefaultRoles(AddTimeTracker, ('Manager',))
setDefaultRoles(AddTimeLog, ('Manager', 'Administrator', 'Contributor', ))
setDefaultRoles(TimeReport, ('Manager', 'Administrator', 'Editor', 'Reader', 'Member', 'Authenticated'))

DEFAULT_ADD_CONTENT_PERMISSION = AddPortalContent
ADD_CONTENT_PERMISSIONS = {
    'TimeTracker' : AddTimeTracker,
    'TimeLog'     : AddTimeLog,
}
