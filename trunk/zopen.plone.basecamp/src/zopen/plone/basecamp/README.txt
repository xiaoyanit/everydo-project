You can test via::

 bin/zopectl test -m zopen.plone.basecamp

准备站点
===================
Test if skin setup is OK:

    >>> from Products.membrane.interfaces import ICategoryMapper
    >>> default_skin = self.portal.portal_skins.getDefaultSkin()
    >>> self.portal.portal_skins.getSkinPath(default_skin)
    '...basecamp_site,...plone_templates...'

    >>> portal = self.portal

站点的用户和权限
============================
测试下网站2个初始组的权限:

    >>> portal.get_local_roles_for_userid('sitemanagers')
    ('Editor',)
    >>> portal.get_local_roles_for_userid('siteseniors')
    ('Reader',)

我们测试一下，系统的默认组。先创建2个用户:

    >>> self.setRoles(('Manager',))
    >>> id = portal.companies.owner_company.invokeFactory(type_name='Person', id='emp_1')
    >>> id = portal.companies.owner_company.invokeFactory(type_name='Person', id='emp_2')

这个用户还没有任何权限:

    >>> uf = portal.acl_users
    >>> user = uf.getUserById('emp_1')
    >>> user.getRolesInContext(portal)
    ['Authenticated']

如果把这个用户加入到管理员组，则有管理员的权限:

    >>> portal.companies.teams.sitemanagers.setMembers([portal.companies.owner_company.emp_1.UID()])
    >>> user = uf.getUserById('emp_1')
    >>> user.getRolesInContext(portal)
    ['Authenticated', 'Editor']

如果把这个用户加入到特权用户组，则有读取人的权限:

    >>> portal.companies.teams.siteseniors.setMembers([portal.companies.owner_company.emp_1.UID()])
    >>> user = uf.getUserById('emp_1')
    >>> user.getRolesInContext(portal)
    ['Authenticated', 'Editor', 'Reader']

我们还是清除用户的站点角色，便于后续的测试:

    >>> portal.companies.teams.siteseniors.setMembers([])
    >>> portal.companies.teams.sitemanagers.setMembers([])
    >>> user = uf.getUserById('emp_1')
    >>> user.getRolesInContext(portal)
    ['Authenticated']

项目的用户和权限
=====================
切换使用adminuser来登录系统:

    >>> id = portal.companies.owner_company.invokeFactory(type_name='Person', id='adminuser')
    >>> portal.companies.teams.sitemanagers.setMembers([portal.companies.owner_company.adminuser.UID()])

    >>> from AccessControl import getSecurityManager
    >>> from AccessControl.SecurityManagement import setSecurityManager, newSecurityManager
    >>> user = portal.acl_users.getUserById('adminuser')
    >>> if not hasattr(user, 'aq_base'): user = user.__of__(portal.acl_users)
    >>> sm = getSecurityManager()
    >>> newSecurityManager(None, user)

先创建一个项目:

    >>> from zopen.plone.project.browser.project import CreateProjectForm
    >>> form = CreateProjectForm(portal.projects, '')

    >>> portal.aq_parent.acl_users._doAddUser('admin', 'admin', [], [])
    >>> project = form.createProject('aaaa', portal.companies.owner_company)

adminuser自动成为项目的管理员:

    >>> portal.companies.owner_company.adminuser in project.teams.projectmanagers.getMembers()
    True

设置项目人员:

    >>> project.teams.projectmanagers.setMembers([portal.companies.owner_company.emp_1.UID()])
    >>> user = uf.getUserById('emp_1')
    >>> user.getRolesInContext(project)
    ['Authenticated', 'Editor']
    >>> project.teams.projectseniors.setMembers([portal.companies.owner_company.emp_1.UID()])
    >>> user = uf.getUserById('emp_1')
    >>> user.getRolesInContext(project)
    ['Authenticated', 'Editor', 'Reader']

    >>> project.teams.projectmembers.setMembers([portal.companies.owner_company.emp_2.UID()])
    >>> user2 = uf.getUserById('emp_2')
    >>> roles = user2.getRolesInContext(project)
    >>> roles.sort()
    >>> roles
    ['Authenticated', 'Member']

回到从前的用户:

    >>> setSecurityManager(sm)

当然这些用户在网站根仍然没用权限的:

    >>> user.getRolesInContext(portal)
    ['Authenticated']
    >>> user2.getRolesInContext(portal)
    ['Authenticated']

测试Utility:

    >>> from zopen.plone.org.interfaces import IOrgInstance
    >>> from zope.component import adapts, getUtility
    >>> basecamp_org = getUtility(IOrgInstance, 'basecamp_org')
    >>> basecamp_org
    <zopen.plone.basecamp.basecamp_org.BasecampOrg object at ...>
    >>> IOrgInstance.providedBy(basecamp_org)
    True

  Another interface test, lets do zope verification.

    >>> from zope.interface import verify
    >>> verify.verifyObject(IOrgInstance, basecamp_org)
    True

    >>> ou = basecamp_org.createCompany('CompanyName')
    >>> ou
    <OrganizationUnit at /plone/companies/...>
    >>> import re
    >>> re.match('^[0-9]{6}$', ou.getId()) is not None
    True
    >>> ou.Title()
    'CompanyName'
    >>> basecamp_org.getAvailableCompanies()
    [('...', 'CompanyName')]
    >>> basecamp_org.getCompany(ou.getId())
    <OrganizationUnit at /plone/companies/...>
    >>> basecamp_org.getOwnerCompany()
    <OrganizationUnit at /plone/companies/owner_company>
