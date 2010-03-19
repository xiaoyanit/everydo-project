function kssServerAction(node, actionName, parms){
  oper = new kukit.op.Oper({'kssParms':{},'parms':parms})
  oper.node = node
  oper.orignode = node
  new kukit.sa.ServerAction(actionName,oper)
}

// for plone 3.0 alpha
function kssServerActionXXX(actionName, parms){
  new kukit.sa.ServerAction(actionName,parms, new kukit.op.Oper())
}

var form_modified_message = "您的表单还没有保存，您做的所有更改都将丢失。";
var external_links_open_new_window = 'true';
