kukit.actionsGlobalRegistry.register("sortTodoItems", function (oper) {
  sortTodoItems()
  });

kukit.commandsGlobalRegistry.registerFromAction('sortTodoItems', kukit.cr.makeGlobalCommand);

kukit.actionsGlobalRegistry.register('sortTodoLists', function (oper) {
  sortTodoLists();
});
kukit.commandsGlobalRegistry.registerFromAction('sortTodoLists', kukit.cr.makeGlobalCommand);

