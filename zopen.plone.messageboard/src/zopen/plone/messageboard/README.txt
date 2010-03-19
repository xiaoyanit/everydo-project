Test if setup is OK:

    >>> 'Message' in self.portal.portal_types.objectIds()
    True
    >>> 'Comment' in self.portal.portal_types.objectIds()
    True
    >>> 'Message' in self.portal.portal_factory.getFactoryTypes().keys()
    True

Create a chatroom:

    >>> self.setRoles(('Manager',))
    >>> id = self.portal.invokeFactory('Message', 'message')
    >>> message = portal.message
    >>> id = self.portal.messageinvokeFactory('Comment', 'comment')
    >>> comment = portal.message.comment

