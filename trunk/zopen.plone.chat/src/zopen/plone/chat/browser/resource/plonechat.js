/* -*- java -*-
/* <dtml-var "enableHTTPCompression(request=REQUEST, debug=1, js=1)"> (this is for http compression) */
/*
<dtml-let last_modified="_.DateTime()-14" expires="_.DateTime()+7" >
<dtml-call "REQUEST.RESPONSE.setHeader( 'Content-Type','text/javascript' )">
<dtml-call "REQUEST.RESPONSE.setHeader( 'Last-Modified',last_modified.toZone('GMT').rfc822() )">
<dtml-call "REQUEST.RESPONSE.setHeader( 'Cache-Control','max-age=36000, must-revalidate' )">
<dtml-call "REQUEST.RESPONSE.setHeader( 'Expires',expires.toZone('GMT').rfc822() )" >
</dtml-let>
*/
var $ = function(ID) { 
  var item = document.getElementById(ID); 
  if (arguments == 2)
  	item = item.getElementsByTagName(arguments[1]);
  return item;
}

function sendMessageOnKeyPress(e, url, field) {
  e = e || window.event;
  if (13 == (e.which ? e.which : e.keyCode)) {
  	sendNewMessage(url, field);
  	return false;
  }
}

function clearIEReturn(e, field){
  if (13 == (e.which ? e.which : e.keyCode)) {
      if (field.value && field.value.charAt(field.value.length -1) == '\n') {
          field.value=''
      }
  }
}

function getXmlHttpRequest(ajaxobject) {
  var ajaxobject = null;
  if ( window.XMLHttpRequest ) {
    // Objet XmlHttpRequest pour les moteurs GECKO
    ajaxobject = new XMLHttpRequest();
  } else if ( window.ActiveXObject ) {
    // Objet XmlHttpRequest pour Internet Explorer
    ajaxobject = new ActiveXObject('Microsoft.XMLHTTP');
  } else {
    // Navigateur non-compatible
    ajaxobject = null;
  }
  return ajaxobject
}
 
timeout = null;
var refreshChat = function(xhReq) {
    var data = xhReq.responseText.split("\t");

    if (onlyUpdate) {
      	userList.innerHTML = data[0]; 
    		msgList.innerHTML += data[1];
  } else {
    		userList.innerHTML = data[0]; 
      	msgList.innerHTML = data[1];
  }
}
function ajaxStateChange(xhReq) {
  if ((xhReq.readyState != 4) || (xhReq.status > 299 || xhReq.status < 200) || (editing && !onlyUpdate))
        	return false;
  
    	var go_scroll = null;
  	total_height = msgList.scrollTop + chat_height + 50;
    	if ((total_height > msgList.scrollHeight) || !timeout)
        	go_scroll = true;
  
    	refreshChat(xhReq); 	
  
    	// scroll to bottom only if user is not scrolling higher in window
    	if (go_scroll != null) 
    		msgList.scrollTop = msgList.scrollHeight;
}
function updateChat(recursive) {
    if (typeof(recursive) == 'undefined')
        recursive = true;
    var xhReq = getXmlHttpRequest();

    if (msgList.lastChild)
      lastID = msgList.lastChild.id;   
    window.status = ajax_url + (onlyUpdate ? "?lastID=" + lastID : "");
    xhReq.open('GET', ajax_url + (onlyUpdate ? "?lastID=" + lastID : ""), true);    
    xhReq.setRequestHeader("If-Modified-Since", "Sat, 1 Jan 2000 00:00:00 GMT");
    xhReq.onreadystatechange = function() { ajaxStateChange(xhReq); };
    xhReq.send(null);
    if (recursive)
        timeout = setTimeout( function() { updateChat(); }, interval);
}
 
function sendNewMessage(url, field) {
    if (field.value == '')
        return;
    value = field.value;
    try {
        field.value = '';
        field.focus();
    } catch (e) {}
    sendNewMessage1(url, value);
    editing = false;
    updateChat(false);
}

function sendNewMessage1(url, value) {
    var query = 'messageToSend=' + encodeURIComponent(value);

    ajaxobject = getXmlHttpRequest();
    ajaxobject.open('POST', url, false);
    // set request headers
    ajaxobject.setRequestHeader('Content-Type','application/x-www-form-urlencoded');
    ajaxobject.setRequestHeader("If-Modified-Since", "Sat, 1 Jan 2000 00:00:00 GMT");

    // send message
    try {
       ajaxobject.send(query);
    } catch (e) {}
}

editing = false;
 
function simpleAjaxRequest(url) {
    var ajaxobject = getXmlHttpRequest();
    ajaxobject.open('GET', url, false);
    // set request headers
    ajaxobject.setRequestHeader("If-Modified-Since", "Sat, 1 Jan 2000 00:00:00 GMT");
    //
    ajaxobject.send(null);
    editing = false;
    updateChat(false);
}

function simplePostRequest(url, query) {
    var ajaxobject = getXmlHttpRequest();
    ajaxobject.open('POST', url, false);
    // set request headers
    ajaxobject.setRequestHeader('Content-Type','application/x-www-form-urlencoded');
    ajaxobject.setRequestHeader("If-Modified-Since", "Sat, 1 Jan 2000 00:00:00 GMT");
    //
    ajaxobject.send(query);
    editing = false;
    updateChat(false);
}

function logout(url) {
    var xhReq = getXmlHttpRequest();
    xhReq.open('GET', url, true);
    xhReq.send(null);
}
