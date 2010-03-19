# -*- encoding: UTF-8 -*-
"""
project create event handler
"""

from zope.component import getUtility
from Products.CMFCore.utils import getToolByName

from Products.membrane.interfaces import IGroup

def setSharing(ob, event):
    if not hasattr(ob, 'getProject'):
        return

    project = ob.getProject()

    # 设置初始的项目组角色
    ob.manage_setLocalRoles(IGroup(project.teams.projectseniors).getGroupId(), ['Editor', 'Contributor'])
