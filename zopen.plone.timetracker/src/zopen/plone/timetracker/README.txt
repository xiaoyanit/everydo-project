Test if setup is OK:

    >>> 'TimeTracker' in self.portal.portal_types.objectIds()
    True
    >>> 'TimeLog' in self.portal.portal_types.objectIds()
    True
    >>> 'TimeLog' in self.portal.portal_factory.getFactoryTypes().keys()
    True

Create a tracker and add a log:

    >>> self.setRoles(('Manager',))
    >>> id = self.portal.invokeFactory('TimeTracker', 'tt')
    >>> id = self.portal.tt.invokeFactory('TimeLog', 'tl')
