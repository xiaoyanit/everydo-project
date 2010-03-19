# -*- encoding: UTF-8 -*-

"""
site setup handlers.
"""

from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.app.component.hooks import setSite

from Products.CMFCore.utils import getToolByName
from Products.CMFQuickInstallerTool.interfaces import IQuickInstallerTool
from Products.CMFEditions.interfaces.IRepository import IRepositoryTool
from Products.CMFEditions.setuphandlers import DEFAULT_POLICIES

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY as CONTEXT_PORTLETS
from plone.app.portlets import portlets

from Products.CMFFormController.interfaces import IFormControllerTool
from plone.app.controlpanel.markup import IWikiMarkupSchema

from config import VERSIONED_TYPES

# import logging; warn = logging.getLogger('zopen.plone.basecamp').warn

class BasecampGenerator:

    def installProducts(self, p):
        qi = getToolByName(p, 'portal_quickinstaller')
        qi.installProduct('CMFPlacefulWorkflow')
        #p.portal_setup.setImportContext('profile-membrane:default')
        #p.portal_setup.runAllImportSteps()
        qi.installProducts([
                'membrane',
                'zopen.plone.org',
                'zopen.plone.chat',
                'zopen.plone.project',
                'zopen.plone.writeboard',
                'zopen.plone.messageboard', 
                'zopen.plone.milestone',
                'zopen.plone.todo',
                'zopen.plone.timetracker',
                ],
                forceProfile=True,
                stoponerror=True)

    def setupVersioning(self, p):
        portal_repository = getToolByName(p, 'portal_repository')
        versionable_types = list(portal_repository.getVersionableContentTypes())
        for type_id in VERSIONED_TYPES:
            if type_id not in versionable_types:
                versionable_types.append(type_id)
                portal_repository.setVersionableContentTypes(versionable_types)
            portal_repository.removePolicyFromContentType(type_id, 'at_edit_autoversion')

    def setupWicked(self, p):
        wms = IWikiMarkupSchema(p)
        wms.wiki_enabled_types = ['Page']

    def setupFormController(self, p):
        # 设置Form Controller
        #fc = queryUtility(IFormControllerTool)
        fc = getToolByName(p, 'portal_form_controller')
        if fc is not None:
            fc.addFormAction('validate_integrity',
               'success',
               'Person',
               '',
               'traverse_to',
               'string:go_back',)

            fc.addFormAction('validate_integrity',
               'success',
               'OrganizationUnit',
               '',
               'traverse_to',
               'string:go_back',)

    def setupPaymentAuthPlugin(self, p):
        from zopen.plone.paycenter.pas import manage_addPaymentLockout
        from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin

        acl_users = p.acl_users
        ids = acl_users.plugins.listPluginIds( IAuthenticationPlugin )
        if 'edo_pay_check' in ids:
            return

        manage_addPaymentLockout(acl_users, 'edo_pay_check')
        epc = acl_users.edo_pay_check
        epc.manage_activateInterfaces(['IAuthenticationPlugin'])

        acl_users.plugins.movePluginsDown( IAuthenticationPlugin, ids )

def importContent(context):
    """
    Final Plone content import step.
    """
    if context.readDataFile('basecamp-content.txt') is None:
        return

    site = context.getSite()
    setSite(site)

    for ob in [site.templates, site.companies, site.projects]: #, site.teams]:
        ob.setExcludeFromNav(True)
        ob.reindexObject()

    site.companies.invokeFactory(type_name='OrganizationUnit', id='owner_company')

    # 手动调用，以便设置权限
    site.companies.owner_company.at_post_create_script()

    # 设置系统的本地角色
    site.manage_setLocalRoles('sitemanagers', ['Administrator'])
    site.manage_setLocalRoles('siteseniors', ['Reader', 'Contributor'])

    # 隐藏一些对象
    wftool = getToolByName(site, 'portal_workflow')
    for ob in [site.companies, site.templates,]:
        wftool.doActionFor(ob, 'protect')

    # XXX 此操作很费时
    # site.portal_catalog.refreshCatalog()

    project = site.templates.project.default

    project.messages.setLayout('@@messages')
    project.writeboards.setLayout('@@writeboards')
    project.files.setLayout('@@filerepos_listing')

    # 设置模板项目初始的权限
    project.manage_setLocalRoles('teams-' + project.getId(), ['Member'])
    project.manage_setLocalRoles('projectseniors-' + project.getId(), ['Reader', 'Contributor'])
    project.manage_setLocalRoles('projectmembers-' + project.getId(), ['Contributor', ])

def importFinalSteps(context):
    if context.readDataFile('basecamp-final.txt') is None:
        return

    site = context.getSite()
    setSite(site)
    gen = BasecampGenerator()

    gen.installProducts(site)
    gen.setupVersioning(site)
    # scope限制还不能工作，不知道为何
    # gen.setupWicked(site)
    gen.setupFormController(site)
    #gen.setupPaymentAuthPlugin(site)

def importTestContent(context):
    if context.readDataFile('basecamp-test.txt') is None:
        return

    site = context.getSite()
    setSite(site)

    for company in site.companies.objectValues():
        for emp in company.objectValues():
            emp.at_post_create_script()

    site.companies.owner_company.setTitle('owner company')
    site.companies.owner_company.invokeFactory(type_name='Person',
            id='admin_user')
    site.companies.owner_company.admin_user.setPassword('11111')
    site.companies.owner_company.admin_user.setEmail('panjy@zopen.cn')
    site.companies.owner_company.admin_user.at_post_create_script()

    site.teams.sitemanagers.setMembers(site.companies.owner_company.admin_user.UID())

    # XXX 此操作很费时
    site.portal_catalog.refreshCatalog()

