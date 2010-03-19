Test if setup is OK:

    >>> 'Project' in self.portal.portal_types.objectIds()
    True
    >>> 'Project' in self.portal.portal_factory.getFactoryTypes().keys()
    True
    >>> 'zopen_project_workflow' in self.portal.portal_workflow.objectIds()
    True
    >>> self.portal.portal_workflow.getChainForPortalType('Project')
    ('zopen_project_workflow',)

Create a OU and 2 users at first:

    >>> self.setRoles(('Manager',))
    >>> id = self.portal.invokeFactory('OrganizationUnit', 'dept')
    >>> id = self.portal.dept.invokeFactory('Person', 'emp1')
    >>> id = self.portal.dept.invokeFactory('Person', 'emp2')

创建一个项目:

    >>> id = self.portal.invokeFactory('Project', 'project')
    >>> project = portal.project
    >>> project.getId()
    'project'

项目包括三种状态: active, onhold, archived。项目的初始状态为active:

   >>> from zope.component import getUtility
   >>> from Products.CMFCore.interfaces import IWorkflowTool
   >>> wftool = getUtility(IWorkflowTool)
   >>> wftool.getInfoFor(project, 'review_state')
   'active'

可让项目进入onhold的状态，onhold状态的项目和active类似，只是不在显眼的界面上显示而已:

   >>> project.setNewProjectState('hold')
   >>> wftool.getInfoFor(project, 'review_state')
   'onhold'
   >>> project.setNewProjectState('activate')
   >>> wftool.getInfoFor(project, 'review_state')
   'active'

或者进入archived的状态:

   >>> project.setNewProjectState('archive')
   >>> wftool.getInfoFor(project, 'review_state')
   'archived'

此时任何人都不能添加内容，也不能修改内容:

   TODO ...

创建一个项目，自动

