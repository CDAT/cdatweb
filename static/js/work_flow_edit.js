current_file = "";
whole = document.URL;
parts = whole.split("=");
path_parts = parts[1].split("/");
path = parts[1];
dir = path_parts[path_parts.length - 1];

$(document).ready( function() {
  title = "";
  for(var i = 3; i < path_parts.length; i++){
    if(i == 3){
      title = path_parts[i];
    }
    else{
      title = title + "/" + path_parts[i];
    }
  }
  $('#title').html(title);
  get_children_edit(path);
  get_resources(path);
});

function upload(){
  $('#uploadbutton').toggle();
  $('#uploadform').toggle();
}

function uploadsave(){
  $('#uploadbutton').toggle();
  $('#uploadform').toggle();
}


