kukit.actionsGlobalRegistry.register('redirect', function (oper) {
  target = oper.parms.target;
  if(target){
     window.frames[target].location = oper.parms.url;
  }else{
     window.location.href=oper.parms.url;
  }
  
});
kukit.commandsGlobalRegistry.registerFromAction('redirect', kukit.cr.makeGlobalCommand);

kukit.actionsGlobalRegistry.register('clear', function (oper) {
    oper.node.value = '';
});
kukit.commandsGlobalRegistry.registerFromAction('clear', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('copyNodesAsLastChild', function (oper) {
    var toNode = document.getElementById(oper.parms.html_id);
    cloned_nodes = kukit.dom.parseHTMLNodes(oper.node.innerHTML);
    kukit.dom.appendChildren(cloned_nodes, toNode);
    kukit.engine.setupEvents(cloned_nodes);
});
kukit.commandsGlobalRegistry.registerFromAction('copyNodesAsLastChild', kukit.cr.makeSelectorCommand);

var _RuleSheetLink = function(href, res_type) {
    this.href = href;
    this.res_type = res_type;
};

kukit.pr.notLoadedKss = function() {};
kukit.pr.notLoadedKss.prototype = {
    check: function(args) {
    },
    eval: function(args, node) {
        results = [];
        args = new String(args).split(' ');
        if(typeof(kukit.engine.stateVariables['loadedKss']) == 'undefined'){
            kukit.engine.stateVariables['loadedKss'] = [];
        }
        loaded_kss = kukit.engine.stateVariables['loadedKss'];
        unloaded_flag = true;
        for(i=0;i<args.length;i++){
            for(j=0;j<loaded_kss.length;j++){
                if(args[i] == loaded_kss[j]){
                    unloaded_flag = false;
                    break;
                }
            }
            if(unloaded_flag){
                results.push(args[i]);
            }
        } 
        return results;
    }
};
kukit.pprovidersGlobalRegistry.register('notloadedKss', kukit.pr.notLoadedKss);

kukit.actionsGlobalRegistry.register('loadKss', function (oper) {
    var ruleprocessor = kukit.engine.createRuleProcessor(new _RuleSheetLink('', 'kss'));
    kukit.engine.stateVariables['loadedKss'] = kukit.engine.stateVariables['loadedKss'].concat(oper.parms.filenames.split(','));
    ruleprocessor.txt = oper.parms.ksstxt;
    ruleprocessor.loaded = true;
    ruleprocessor.parse();
});
kukit.commandsGlobalRegistry.registerFromAction('loadKss', kukit.cr.makeGlobalCommand);

kukit.actionsGlobalRegistry.register('setupKss', function (oper) {
    var node = oper.node;

    kukit.engine.setupEvents([oper.node]);
});

kukit.commandsGlobalRegistry.registerFromAction('setupKss', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('addSelectOption', function (oper) {
    sel = oper.node;
    title = oper.parms.title;
    value = oper.parms.value;

    for(var idx = sel.options.length; idx > 0; idx--) {
            sel.options[idx] = new Option(sel.options[idx-1].text, sel.options[idx-1].value);
    }
    sel.options[0] = new Option(title, value);
    sel.selectedIndex = 0;
});
kukit.commandsGlobalRegistry.registerFromAction('addSelectOption', kukit.cr.makeSelectorCommand);

kukit.pr.KssAttrJoinPP = function() {};
kukit.pr.KssAttrJoinPP.prototype = {
    check: function(args) {
    },
    eval: function(args, node) {
        result = '';
        for(var i= 0; i<args.length; i++){
            arg = args[i];
            if(arg.substring(0,1) == '*'){
               result += kukit.dom.getRecursiveAttribute(node, arg.substring(1), true, kukit.dom.getKssAttribute);
            }else{
               result += arg;
            }
        }
        return result;
    }
};
kukit.pprovidersGlobalRegistry.register('kssAttrJoin', kukit.pr.KssAttrJoinPP);

// a new selector
kukit.selectorTypesGlobalRegistry.register('parentnodecss', function(expr, node, orignode) {

   expr = expr.split("|");
   parentnode_s = expr[0];
   css_s = expr[1];

   if(css_s.substring(0,1) == '*'){
        css_s = kukit.dom.getRecursiveAttribute(node, css_s.substring(1), true, kukit.dom.getKssAttribute);
        css_s = css_s.replace('*', ' ');
   }

   if (parentnode_s != '') {
       parentnodes = kukit.selectorTypesGlobalRegistry.get('parentnode')(parentnode_s, node, orignode);
       if(parentnodes.length == 0){
            return [];
       }
       node = parentnodes[parentnodes.length - 1];
   }

   if (css_s == '') {
        return [node];
   }

   results = base2.DOM.Document.querySelectorAll(node, css_s);

   var nodes = [];
   for(var i = 0; i < results.length; i++) {
         nodes.push(results.item(i));
   }
   return nodes;
});

// a new selector
kukit.selectorTypesGlobalRegistry.register('parentnodenextnode', function(expr, node, orignode) {

   parentnodes = kukit.selectorTypesGlobalRegistry.get('parentnode')(expr, node, orignode);

   if (parentnodes.length > 0) {

       var next = parentnodes[0].nextSibling;
       do {
	   /* element node */
	   if (next && next.nodeType == 1)
	       return [next];
       } while (next = next.nextSibling);
   }

   return [];
});

function kssServerAction(node, actionName, parms){
  oper = new kukit.op.Oper({'kssParms':{},'parms':parms})
  oper.node = node;
  oper.orignode = node;
  new kukit.sa.ServerAction(actionName,oper);
}

// kukit.engine.requestManager.sendingTimeout = 200000;
