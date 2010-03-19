// window scroll when dragging.
// copy from
// http://henrik.nyh.se/2006/12/scroll-window-when-dragging-scriptaculous-sortables-to-edges

function sortTodoItems(){

  if(document.getElementById('canmoveitems').value == '0'){
     return
  }

  // Sortable.destroy('fulllists');

  lists = cssQuery('#fulllists .activetodos');
  for(var i=0; i<lists.length; i++){
      id = lists[i].id;

    Sortable.create(id,
            { tag:'div',
              only:'kssDeletionRegion',
              dropOnEmpty:true,
              handle:'handle',
              scroll:window,
              containment: lists,
              overlap: 'vertical',
              constraint: 'vertical',
              onUpdate:function(draggable, event){
                  oid = draggable.id.split('_')[1]
                  kssServerAction('', 
                                 oid + '/@@reorderTodoItems', 
                                 {orderstring: Sortable.serialize(draggable.id, 
                                      {name:'id',tag:'div'})}
                                 )
                  }
            })
  }
}

function sortTodoLists(){

  lists = cssQuery('#fulllists .activetodos');
  //for(var i=0; i<lists.length; i++){
  //  Sortable.destroy( lists[i].id )
  //};

  Sortable.create('fulllists',
           {tag:'div',
            only:['todolist','opageitem'],
            dropOnEmpty:true,
            handle:'handle',
            scroll:window,
            containment: ['fulllists'],
            overlap: 'vertical',
            constraint: 'vertical',
            onUpdate:function(draggable, event){
                 kssServerAction('',
                     '@@reorderTodoLists',
                     {orderstring: Sortable.serialize('fulllists', {name:'id',tag:'div'})})
                }
            });
}

function delete_todoitem(node){
        if ( confirm('确信删除吗？这个操作是不可恢复的。') == false) { return false; }

        wrapper= kukit.selectorTypesGlobalRegistry.get('parentnode')('.wrapper', node,node)
        wrapper[0].style.display='none'
        checkbox = kukit.selectorTypesGlobalRegistry.get('parentnodecss')('.kssDeletionRegion|.EVcomplete', node, node)
        spinner = kukit.selectorTypesGlobalRegistry.get('parentnodecss')('.kssDeletionRegion|.spinner', node, node)
       // checkbox[0].style.display='none'
        spinner[0].style.display='inline'

        url = kukit.dom.getRecursiveAttribute(node, 'listid', true, kukit.dom.getKssAttribute) +'/'+ kukit.dom.getRecursiveAttribute(node, 'itemid', true, kukit.dom.getKssAttribute)

        kssServerAction(node, url + "/kss_obj_delete", {selector:'.kssDeletionRegion'});
        return false;
}
