from zope.interface import Interface
from zope import schema

class ITodoFolderContent(Interface):
    pass

class ITodoListContent(Interface):
    pass

class ITodoItemContent(Interface):
    pass

class IStandaloneTodo(Interface):
    pass
