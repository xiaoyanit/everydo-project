Test if setup is OK:

    >>> 'Chat' in self.portal.portal_types.objectIds()
    True
    >>> 'Chat' in self.portal.portal_factory.getFactoryTypes().keys()
    True

Create a chatroom:

    >>> self.setRoles(('Manager',))
    >>> id = self.portal.invokeFactory('Chat', 'chatroom')
    >>> portal.chatroom.getId()
    'chatroom'
