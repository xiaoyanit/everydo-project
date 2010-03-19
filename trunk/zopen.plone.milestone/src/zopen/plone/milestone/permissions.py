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
AddMilestone                 = "zopen.milestone: Add milestone"
AddMilestoneFolder           = "zopen.milestone: Add milestone folder"
ReportState                  = "zopen.milestone: Report state"

setDefaultRoles(AddMilestone, ('Manager', 'Administrator', 'Owner', 'Contributor'))
setDefaultRoles(AddMilestoneFolder, ('Manager',))
setDefaultRoles(ReportState, ('Manager', 'Administrator', 'Editor', 'Owner', 'Responsor' ))

DEFAULT_ADD_CONTENT_PERMISSION = AddPortalContent
ADD_CONTENT_PERMISSIONS = {
    'Milestone' : AddMilestone,
    'MilestoneFolder' : AddMilestoneFolder,
}
