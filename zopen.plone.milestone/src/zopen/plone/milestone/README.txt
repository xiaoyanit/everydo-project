Test if setup is OK:

    >>> 'Milestone' in self.portal.portal_types.objectIds()
    True
    >>> 'MilestoneFolder' in self.portal.portal_types.objectIds()
    True
    >>> 'Milestone' in self.portal.portal_factory.getFactoryTypes().keys()
    True
    >>> 'zopen_milestone_workflow' in self.portal.portal_workflow.objectIds()
    True
    >>> self.portal.portal_workflow.getChainForPortalType('Milestone')
    ('zopen_milestone_workflow',)

Create a OU and 2 users at first:

    >>> self.setRoles(('Manager',))
    >>> id = self.portal.invokeFactory('MilestoneFolder', 'msf')
    >>> id = self.portal.msf.invokeFactory('Milestone', 'ms')
    >>> milestone = self.portal.msf.ms

milestone包括2种状态: active, completed。项目的初始状态为active:

   >>> from zope.component import getUtility
   >>> from Products.CMFCore.interfaces import IWorkflowTool
   >>> wftool = getUtility(IWorkflowTool)
   >>> wftool.getInfoFor(milestone, 'review_state')
   'active'

