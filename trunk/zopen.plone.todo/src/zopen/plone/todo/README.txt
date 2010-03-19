drag and drop:

http://wiki.script.aculo.us/scriptaculous/show/SortableListsDemo

http://wiki.script.aculo.us/scriptaculous/show/Sortables

http://wiki.script.aculo.us/scriptaculous/show/DragAndDrop

    >>> 'TodoList' in self.portal.portal_types.objectIds()
    True
    >>> 'TodoItem' in self.portal.portal_types.objectIds()
    True
    >>> 'TodoFolder' in self.portal.portal_types.objectIds()
    True

Create a OU and 2 users at first:

    >>> self.setRoles(('Manager',))
    >>> id = self.portal.invokeFactory('TodoFolder', 'todofolder')
    >>> id = self.portal.todofolder.invokeFactory('TodoList', 'todolist')
    >>> id = self.portal.todofolder.todolist.invokeFactory('TodoItem', 'item1')
    >>> id = self.portal.todofolder.todolist.invokeFactory('TodoItem', 'item2')
