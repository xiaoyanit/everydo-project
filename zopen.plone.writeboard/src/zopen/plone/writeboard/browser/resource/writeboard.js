function getSelectedVersions(selected) {
    var boxes = new Array()
    var elements = document.getElementById('compare_form').elements
    boxes.selected_index = -1

    for(var i = 0; i < elements.length; i++)
      if(elements[i].name != "submit" && elements[i].checked) {
        if(elements[i] == selected) boxes.selected_index = boxes.length
        boxes.push(elements[i])
      }

    return boxes
}

function checkVersion(checkbox) {
 if(!checkbox.checked){
    document.getElementById('compare_button').disabled = true
    return
 }

  var selections = getSelectedVersions(checkbox)
  if(selections.length > 2)
      for(var i = 0; i < selections.length; i++)
        if(selections[i] != checkbox) selections[i].checked = false

  var boxes = getSelectedVersions(checkbox)
  document.getElementById('compare_button').disabled = (boxes.length != 2)

}
