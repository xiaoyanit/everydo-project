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
AddChat = "zopen.plone.chat: Add Chat"

setDefaultRoles(AddChat, ('Manager',))

DEFAULT_ADD_CONTENT_PERMISSION = AddPortalContent
ADD_CONTENT_PERMISSIONS = {
    'Chat' : AddChat,
}
