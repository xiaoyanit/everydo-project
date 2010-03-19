from zope.interface import Interface
from zope.interface import implements

from kss.core.kssview import CommandSet
from kss.core.plugins.core.interfaces import IKSSCoreCommands

class ITodoCommands(Interface):

    def sortTodoItems(ids):
        pass

class TodoCommands(CommandSet):
    implements(ITodoCommands)

    def sortTodoItems(self):
        command = self.commands.addCommand('sortTodoItems')
