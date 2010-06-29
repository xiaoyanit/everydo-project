#-*- coding: utf-8 -*-
from kss.core import kssaction
from plone.app.kss.plonekssview import PloneKSSView
from Products.Five import BrowserView
from kss.core import force_unicode
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.component import getUtility
from Products.membrane.interfaces import IGroup
from Acquisition import aq_inner, aq_parent, aq_base
from Products.CMFCore.utils import getToolByName
from zopen.plone.org.interfaces import IOrganizedEmployess
from zope.component import getMultiAdapter

class PermissionSettingView(BrowserView):

    def canCustomPermission(self):
         return True

    def getRoles(self):
        return ['Member', 'Reader', 'Contributor', 'Editor', 'Reviewer']


    def getGroups(self):
        teams = self.context.aq_inner.contentValues()
        return [IGroup(team).getGroupId() for team in teams]

    def getOriginalObject(self, subpath=''):
        containner = self.context.aq_inner.aq_parent
        if subpath:
            return containner.unrestrictedTraverse(subpath)
        else:
            return containner

    def getFileFolds(self):
        results = []
        results.append(['', ''])
        results.append(['messages', 'parent'])
        obj = self.getOriginalObject('messages')
        messagesFold = obj.contentValues()
        for mf in messagesFold:
            results.append(['messages/' + mf.getId(), 'messageschildren'])

        results.append(['todos', ''])
        results.append(['milestones', ''])
        results.append(['time', ''])
        results.append(['chatroom', ''])

        results.append(['files', 'parent'])
        
        obj = self.getOriginalObject('files')
        filesFold = obj.contentValues()
        for ff in filesFold:
            results.append(['files/' + ff.getId(), 'fileschildren'])

            
        return results

    def getInheritStatus(self, obj):
        return getattr(aq_base(obj), '__ac_local_roles_block__', None)
    
    def listPrivilege(self, subpath):

        obj = self.getOriginalObject(subpath)

        results = []

        privilege = []
        
        groups = self.getGroups()

        if not self.getInheritStatus(obj):
            results.append('checked')
        else:
            results.append('')
        

        for roleStr in self.getRoles():
            privilege.append({})
            i = len(privilege) - 1
            privilege[i].setdefault('groups', [])
            privilege[i].setdefault('users', [])

            for member in obj.users_with_local_role(roleStr):
                if member in groups:
                    privilege[i]['groups'].append(member)
                else:
                    privilege[i]['users'].append(member)

        results.append(privilege)
        return results

    def getResponsiblePartyTitle(self, responsor):
        mtool = getToolByName(self.context, 'portal_membership')
        mi = mtool.getMemberInfo(responsor)
        if mi:
            return mi['fullname'] or responsor
        else:
            gtool = getToolByName(self.context.aq_inner.aq_parent, 'portal_groups')
            group = gtool.getGroupInfo(responsor)
            if group:
                return group['title'] or responsor
            else:
                return responsor
    
    def getMembers(self):
        project = self.context.getProject()
        adapter = IOrganizedEmployess(project.teams)
        cp = adapter.get_all_companies_and_people()
        members = []
        for k in cp.keys():
            count = 0
            for i in cp[k]:
                if count == 0:
                    count += 1
                    continue
                else:
                    members.append(i)
                    count += 1
                    
        return members

privilege_template = ZopeTwoPageTemplateFile('permissionsetting.pt')

class PermissionSettingKssView(PloneKSSView, PermissionSettingView):

    @kssaction
    def addPrivilege(self, value, role, subpath=""):
        obj = self.getOriginalObject(subpath)
        addroles = [role]
        roles = self.getRoles()
        obj.manage_addLocalRoles(value, addroles)
        obj.reindexObjectSecurity()
        the_macro = privilege_template.macros['privilegeItem']
        item = self.listPrivilege(subpath)[1][roles.index(role)]
        content = self.header_macros(the_macro=the_macro, \
                                    item=item,
                                    roles=roles,
                                    role=role,
                                    obj_url=subpath,
                                    canCustomPermission=self.canCustomPermission())
        content = force_unicode(content, 'utf-8')
        ksscore = self.getCommandSet('core')
        selector = ksscore.getSelector('parentnode', '.privilegeItem')
        ksscore.replaceHTML(selector, content)

    @kssaction
    def getTeamsOrUsers(self):
        teams = self.context.aq_inner.contentValues({'portal_type':['Team']})
        teamsids = [team.getId() for team in teams]
        ksscore = self.getCommandSet('core')
        selector = ksscore.getSelector('samenode','')
        content = "<select class=\"selectarea\" style=\"display: inline;\">"
        content += "<option value=\"please select a option\">分配权限给...</option>"
        content += "<optgroup label='项目组'>"
        for team in teams:
            if team.getId() != 'projectmanagers':
                content += "<option value=\"" + IGroup(team).getGroupId() + \
                           "\">" + team.pretty_title_or_id() + \
                            "</option>"

        content += "</optgroup>"
        
        project = self.context.getProject()
        adapter = IOrganizedEmployess(project.teams)
        cp = adapter.get_all_companies_and_people()
        for k in cp.keys():
            count = 0
            for i in cp[k]:
                if count == 0:
                    content += "<optgroup label='" + i.pretty_title_or_id() \
                            +"'>"
                    count += 1
                else:
                    content += "<option value=\"" + i.getId() + \
                            "\">" + i.pretty_title_or_id() + \
                             "</option>"
                    count += 1
            content += "</optgroup>"

        content += "</select>"
        content = force_unicode(content, 'utf-8')
        ksscore.insertHTMLAfter(selector, content)
        selectarea = ksscore.getSelector('css', '.selectarea')
        ksscore.focus(selectarea)
        
    @kssaction
    def deletePrivilege(self, value, role, subpath=''):
        obj = self.getOriginalObject(subpath)
        delroles = [role]
        existsroles = obj.get_local_roles_for_userid(value)
        roles = self.getRoles()
        newroles = [r for r in existsroles if r != role]
        if len(newroles) == 0:
            obj.manage_delLocalRoles([value])
        else:
            obj.manage_setLocalRoles(value, newroles)

        obj.reindexObjectSecurity()
            
        the_macro = privilege_template.macros['privilegeItem']
        item = self.listPrivilege(subpath)[1][roles.index(role)]

        content = self.header_macros(the_macro=the_macro, \
                                    item=item,
                                    roles=roles,
                                    role=role,
                                    obj_url=subpath,
                                    canCustomPermission=self.canCustomPermission())
        content = force_unicode(content, 'utf-8')
        ksscore = self.getCommandSet('core')
        selector = ksscore.getSelector('parentnode', '.privilegeItem')
        ksscore.replaceHTML(selector, content)

        
    @kssaction
    def updateInherit(self, status='', subpath=''):
        
        obj = self.getOriginalObject(subpath)
        ksscore = self.getCommandSet('core')
        samenode = ksscore.getSelector('samenode','')
        
        projectmanagers = 'projectmanagers-' + self.context.aq_inner.aq_parent.getId()
        
        if status:
            obj.__ac_local_roles_block__ = None
            existsroles = obj.get_local_roles_for_userid(projectmanagers)
    
            newroles = [r for r in existsroles if r != 'Administrator']
            if len(newroles) == 0:
                obj.manage_delLocalRoles([projectmanagers])
            else:
                obj.manage_setLocalRoles(projectmanagers, newroles)
                 
        else:
            obj.__ac_local_roles_block__ = True
            obj.manage_addLocalRoles(projectmanagers, ['Administrator'])
            
        obj.reindexObjectSecurity()
        selector = ksscore.getSelector('parentnodecss', \
                                '.clickItem|.TGcomplete')
        ksscore.toggleClass(selector, 'hideme')

