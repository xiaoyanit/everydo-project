# -*- encoding: UTF-8 -*-
"""
project create event handler
"""

from zope.component import getUtility
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IURLTool

from Acquisition import aq_inner, aq_parent, aq_base
from Products.membrane.interfaces import IGroup

from Products.CMFPlone.utils import _createObjectByType

structure = (

# id ,          type ,     title, description, default page,
('messages','Folder', '消息板',   '', '@@messages', (
    ('designs','Large Plone Folder', '设计', '', '', ()),
    ('transcripts','Large Plone Folder', '记录', '', '', ()),
    ('management','Large Plone Folder', '项目管理', '' ,'' ,()),
    )),

('todos','TodoFolder', '任务列表', '', '', ()),
('milestones','MilestoneFolder', '里程碑', '', '', ()),
('writeboards','Folder', '写字板', '', '@@writeboards', ()),
('time','TimeTracker', '工作日志', '', '', ()),
('chatroom','Chat', '讨论区', '', '',(
    # ('firstchatlog','ChatLog', 'first chat log','','',()),
    )),

('files','Folder', '文件', '', '@@filerepos_listing',(
    ('uncategoried','Large Plone Folder', '未分类','','',()),
    ('documents','Large Plone Folder', '文档','','',()),
    ('pictures','Large Plone Folder', '图片','','',()),
    ('sounds','Large Plone Folder','音频','','',()),
    )),

('teams','TeamFolder', '', '', '', (
    ('projectmanagers','Team',
        '项目管理员','项目管理员在项目中拥有最大的权限，包括调整项目设置的权限','',()),
    ('projectseniors','Team',
        '内部人员','内部人员一般是公司内部的人员，能够查看保密的文件、消息等内容','', ()),
    ('projectmembers','Team',
        '外部人员','外部人员是参与项目的人员，只能查看非保密内容','',()),
    )),
)

def createContent(context, structure):
    for (id, type_name, title, description, view, objects) in structure:
        _createObjectByType(type_name, context, id, title=title)
        ob = getattr(context, id)
        if view: ob.setLayout(view)
        if objects: createContent(ob, objects)

def initProject(ob, event):
    project = ob
    portal = getToolByName(project, 'portal_url').getPortalObject()

    # 设置初始的项目组角色

    # 设置项目管理员的权限
    project.manage_setLocalRoles('projectmanagers-' + project.getId(), ['Administrator'])
    # 单独设置项目的查看权限，所有项目成员都恩那个查看
    project.manage_setLocalRoles('teams-' + project.getId(), ['Member'])

    #av = getMultiAdapter( (portal, portal.REQUEST), name=u'account_view')
    #if not av.canCustomPermission():
    #    project.manage_setLocalRoles('projectseniors-' + project.getId(), ['Reader', 'Contributor'])
    #    project.manage_setLocalRoles('projectmembers-' + project.getId(), ['Contributor', ])

    p = portal.templates.project.default
    ids = p.objectIds()
    project.manage_pasteObjects(p.manage_copyObjects(ids))

    roles = ['Administrator', 'Contributor', 'Editor', 'Member', 'Reader', 'Reviewer']
    containner = p

    #if av.canCustomPermission():
    if 1:
        for item in ['', 'messages', 'files', 'todos', 'milestones',\
                     'writeboards', 'chatroom', 'time']:
            if item:
                objTemplate = containner.unrestrictedTraverse(item)
                objNew = project.unrestrictedTraverse(item)
            else:
                objTemplate = containner
                objNew = project
                
            for role in roles:
                for member in objTemplate.users_with_local_role(role):
                    member = member.rsplit('-', 1)[0] + '-' + project.getId()
                    objNew.manage_addLocalRoles(member, [role])
            objNew.__ac_local_roles_block__ = getattr(aq_base(objTemplate), '__ac_local_roles_block__', None)
            objNew.reindexObjectSecurity()

            if item in ['messages', 'files']:
                for itemp, inew in zip(objTemplate.contentValues(), objNew.contentValues()):
                    for role in roles:
                        for member in itemp.users_with_local_role(role):
                            member = member.rsplit('-', 1)[0] + '-' + project.getId()
                            inew.manage_addLocalRoles(member, [role])
                    inew.__ac_local_roles_block__ = getattr(aq_base(itemp), '__ac_local_roles_block__', None)
                    inew.reindexObjectSecurity()

    wftool = getToolByName(project, 'portal_workflow')
    # wftool.doActionFor(project.chatroom, 'hide')
    wftool.doActionFor(project.time, 'hide')

    #project.reindexObjectSecurity()

    # 将全局项目特权人加入到新项目的内部人员中

    seniormembers = portal.teams.siteseniors.getRawMembers()
    managers = project.teams.projectmanagers.getRawMembers()
    seniormembers = [m for m in seniormembers if m not in managers]
    project.teams.projectseniors.setMembers(seniormembers)

    # 将客户的用户全部加入到外部人员中
    company = project.getCompany()
    if company.getId() != 'owner_company':
        project.teams.projectmembers.setMembers(company.contentValues())

