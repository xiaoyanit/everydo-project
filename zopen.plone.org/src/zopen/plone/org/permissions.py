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
AddTeam = "zopen.org: Add Team"
AddOrganizationUnit = "zopen.org: Add Organization Unit"
AddPerson = "zopen.org: Add Person"

setDefaultRoles(AddTeam, ('Manager', 'Administrator'))
setDefaultRoles(AddOrganizationUnit, ('Manager', 'Administrator'))
setDefaultRoles(AddPerson, ('Manager','Administrator'))
setDefaultRoles('Manage users', ('Manager','Administrator'))

DEFAULT_ADD_CONTENT_PERMISSION = AddPortalContent
ADD_CONTENT_PERMISSIONS = {
    'Team'             : AddTeam,
    'OrganizationUnit' : AddOrganizationUnit,
    'Person'           : AddPerson,
}
