/*
 * some deletion related functions
 *
 */

function delete_confirm(node, message, delBaseUrl, other, viewaction) {
        if ((message == '') || (typeof(message) == 'undefined')) {
              message = '您确定要删除这个条目吗？删除操作是不可恢复的。';
        }

	if ( confirm(message) == false) { return false; }
        try {
           delSelector = kukit.dom.getRecursiveAttribute(node, 'delSelector', true, kukit.dom.getKssAttribute);
        } catch (e) { delSelector = null }

        if (delSelector == null) {
             delSelector = '.kssDeletionRegion';
        }

        if (typeof(delBaseUrl) == 'undefined'){
            try {
                delBaseUrl = kukit.dom.getRecursiveAttribute(node, 'delBaseUrl', true, kukit.dom.getKssAttribute);
            } catch (e) { delBaseUrl = null }
        }

        if (delBaseUrl == null) {
            delBaseUrl = '';
        }else{
            delBaseUrl = delBaseUrl + '/';
        }

		if (viewaction == null) {
			viewaction = "@@kss_obj_delete";
		}

        node.src = '/++resource++indicator.gif';
        kssServerAction(node, delBaseUrl + viewaction, {selector:delSelector, other:other});
	return false;
}
