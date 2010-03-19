/*
 * rename function
 *
 */

function rename_category(node, base_url, id) {
    old_title = node.parentNode.nextSibling.innerHTML;
    var new_title = prompt('Rename the category to', old_title);
    if (new_title)
	kssServerAction(node, base_url + "/listRenameCategory", {
	    id:id, new_title:new_title});
    return false;
}


