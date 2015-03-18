/*   Function for getting data in and out of AKUNA   */

m_folder = "<img src=\"/acme/static/filetree/images/directory.png\"/> &nbsp; ";
m_file = "<img src=\"/acme/static/filetree/images/file.png\"/> &nbsp; ";
m_refresh = "<span class=\"glyphicon glyphicon-retweet\"></span> &nbsp; ";
m_current_path = ""

function get_templates(){
  var user_account = getinfo();
  if(user_account['aun'] == ""){
    $('#avaiabletree').html('<b>please add AKUNA user info, then refresh page</b>');
  }
  else{
    var html = "<table class=\"table\">";
    var url = "/acme/gettemplates"
    var jsonObj = new Object;
    jsonObj.username = user_account['aun'];
    jsonObj.password = user_account['apw'];
    var jsonStr = JSON.stringify(jsonObj);

    $.ajax({
      type: "POST",
      url: url,
      data: {user:jsonStr},
      dataType: 'json',
      success: function(data){
        templates = data.key;
        if(templates.substring(0,4) != "fail"){
          obj = JSON.parse(templates)
          for(var i = 0; i < obj.length; i++){
            for (var property in obj[i].properties) {
              if (obj[i].properties.hasOwnProperty(property)) {
                if (hasOwnProperty) {
                  if (property.substr(-5) == "}name") {
                    name = obj[i].properties[property];
                    html = html + "<tr><td>" + m_folder + name + "</td><td>";
                    html = html + "<a onclick=\"clone_template('" + name + "')\" href=\"javascript:void(0);\"><button class=\"btn btn-success\">clone</button></a>";
                    html = html + "</td></tr>"
                  }
                }
              }
            }  
          }

          if (obj.length == 0){
            html = html + "<tr><td>no templates found</td></tr>";
          }
          html = html + "</table>" 
          $('#avaiabletree').html(html);
        }
        else{
          // alert(templates);
          $('#avaiabletree').html("Have you added your user info?");
        }
      },
      error: function(request, status, error){
        alert(request + " | " +  status + " | " +  error);  
      }
    });
  }
}

function get_user_cases(){
  var path = get_user_path();
  get_children_home(path);
}

function get_user_path(){
  var user_info = getinfo();
  var username = user_info['aun'];
  var path = "company_home/User%20Documents/" + username;
  return path; 
}

function clone_template(name){
  var user_account = getinfo();
  var url = "/acme/clonetemplates"
  var jsonObj = new Object;
  jsonObj.username = user_account['aun'];
  jsonObj.password = user_account['apw'];
  jsonObj.template = name;
  var jsonStr = JSON.stringify(jsonObj);

  $.ajax({
    type: "POST",
    url: url,
    data: {user:jsonStr},
    dataType: 'json',
    success: function(data){
      var message = data.key;
      if( message == "success"){
        location.reload();
      }
      else{
        $('#message').html("completed");
      }  
    },
    error: function(request, status, error){
      alert(request + " | " +  status + " | " +  error);  
    }
  });
}

function get_children_home(path_in){
  var html = "<table class=\"table\">";
  var url = "/acme/getchildren"
  var path = path_in
  var user_account = getinfo();

  var jsonObj = new Object;
  jsonObj.username = user_account['aun'];
  jsonObj.password = user_account['apw'];
  jsonObj.path = path;
  var jsonStr = JSON.stringify(jsonObj);
  $.ajax({
    type: "POST",
    url: url,
    data: {user:jsonStr},
    dataType: 'json',
    success: function(data){
      temp = data.key;
      if(temp.substring(0,4) != "fail"){
        obj = JSON.parse(temp);
        case_name = "";
        case_type = "";

        for(var i = 0; i < obj.length; i++){
          if(obj[i].type.substr(-7) == "}folder"){
            for (var property in obj[i].properties) {
              if (obj[i].properties.hasOwnProperty(property)) {
                if (hasOwnProperty) {
                  if (property.substr(-5) == "}name") {
                    case_name = obj[i].properties[property];
                    pass_path =  path + "/" + case_name
                    html = html + "<tr><td>" + m_folder;
                    html = html + "<a href=\"code?path=" + pass_path + "\">" + case_name + "</a>";
                    html = html + "</td></tr>"
                  }
                }
              }
            }  
          }
        }  
        if(obj.length == 0){
          html = html + "<tr><td>No cases found</td></tr>";
        }
        html = html + "</table>" 
        $('#getchildren').html(html);
      }
      else{
        //alert(temp);
        $('#getchildren').html("No workflows found");
      }
    },
    error: function(request, status, error){
      var error_log = request + " | " +  status + " | " +  error;
    }
  });
}

function get_children_edit(path_in){
  var url = "/acme/getchildren"
  var user_account = getinfo();
  var path = path_in;
  var path_parts = path.split("/");
  var html = "";
  if(path_parts.length > 4){
    var back_path = "";
    for(var i = 0; i < path_parts.length - 1; i++){
      if(i == 0){
        back_path = path_parts[i];
      }
      else{
        back_path = back_path + "/" + path_parts[i];
      }
    }
    html = html + "<a href=\"code?path=" + back_path + "\">" + m_refresh + "back</a><br/>";
  }
  html = html + "<table id=\"filetree\" class=\"table\">";

  var jsonObj = new Object;
  jsonObj.username = user_account['aun'];
  jsonObj.password = user_account['apw'];
  jsonObj.path = path;
  var jsonStr = JSON.stringify(jsonObj);
  $.ajax({
    type: "POST",
    url: url,
    data: {user:jsonStr},
    dataType: 'json',
    success: function(data){
      temp = data.key;
      if(temp.substring(0,4) != "fail"){
        obj = JSON.parse(temp);
        case_name = "";
        case_type = "";

        for(var i = 0; i < obj.length; i++){
          var type = obj[i].type;
          for (var property in obj[i].properties) {
            if (obj[i].properties.hasOwnProperty(property)) {
              if (hasOwnProperty) {
                if (property.substr(-5) == "}name") {
                  case_name = obj[i].properties[property];
                  pass_path =  path + "/" + case_name
                  case_name = case_name.toString();
                  if (case_name.indexOf('.') !== -1){
                    case_parts = case_name.split(".");
                    case_id = case_parts[0];
                  }
                  else{
                    case_id = case_name;
                  }
                  html = html + "<tr><td id=\"" + case_id + "\">";
                  if(type.substr(-7) == "}folder"){
                    html = html + m_folder;
                    html = html + "<a href=\"code?path=" + pass_path + "\">" + case_name + "</a>";
                  }
                  else{
                    html = html + m_file;
                    html = html + "<a onclick=\"get_file_content('" + pass_path + "')\" href=\"javascript:void(0);\">" + case_name + "</a>";
                  }
                  html = html + "</td><td></td></tr>"
                }
              }
            }
          }
        }  
        if(obj.length == 0){
          html = html + "<tr><td>folder empty</td></tr>";
        }
        html = html + "</table>" 
        $('#usertree').html(html);
      }
      else{
        alert(temp);
      }
    },
    error: function(request, status, error){
      var error_log = request + " | " +  status + " | " +  error;
    }
  });
}

function get_file_content(path_in){
  var url = "/acme/getfile"
  var user_account = getinfo();
  var path = path_in;
  var jsonObj = new Object;
  jsonObj.username = user_account['aun'];
  jsonObj.password = user_account['apw'];
  jsonObj.path = path;
  var jsonStr = JSON.stringify(jsonObj);
  $.ajax({
    type: "POST",
    url: url,
    data: {user:jsonStr},
    dataType: 'json',
    success: function(data){
      file_content = data.key;
      if(file_content.substring(0,4) != "fail"){
        var old_path = m_current_path;
        var parts = old_path.split('/');
        var unselected_whole = parts[parts.length - 1];
        var unselected_parts = unselected_whole.split(".");
        var unselected = unselected_parts[0]; 

        m_current_path = path;
        var parts = path.split('/');
        var selected_whole = parts[parts.length - 1];
        var selected_parts = selected_whole.split(".");
        var selected = selected_parts[0];

        $('#' + unselected).css('backgroundColor', '#FFF');
        $('#' + selected).css('backgroundColor', '#FFFFCC');
        $('#textarea').val(file_content);
      }
      else{
        alert(file_content);
      }
    },
    error: function(request, status, error){
      var error_log = request + " | " +  status + " | " +  error;
    }
  });
}

function save_file_content(){
  var path = m_current_path;
  if(path == ""){
    alert("no file selected")
  }
  else{
    var url = "/acme/savefile"
    var user_account = getinfo();
    var file_content = $('#textarea').val();

    var jsonObj = new Object;
    jsonObj.username = user_account['aun'];
    jsonObj.password = user_account['apw'];
    jsonObj.path = path;
    jsonObj.content = file_content;
    var jsonStr = JSON.stringify(jsonObj);
    $.ajax({
      type: "POST",
      url: url,
      data: {user:jsonStr},
      dataType: 'json',
      success: function(data){
        file_content = data.key;
        if(file_content.substring(0,4) != "fail"){
          alert("success");
        }
        else{
          alert("fail");
        }
      },
      error: function(request, status, error){
        var error_log = request + " | " +  status + " | " +  error;
      }
    });
  }
}

function get_resources(path){
  var url = "/acme/getresource"
  var user_account = getinfo();
  var path = path;

  var jsonObj = new Object;
  jsonObj.username = user_account['aun'];
  jsonObj.password = user_account['apw'];
  jsonObj.path = path;
  var jsonStr = JSON.stringify(jsonObj);
  $.ajax({
    type: "POST",
    url: url,
    data: {user:jsonStr},
    dataType: 'json',
    success: function(data){
      temp = data.key;
      messages = JSON.stringify(temp, null, 4);
           
      $('#display-messages').html(messages);
    },
    error: function(request, status, error){
      var error_log = request + " | " +  status + " | " +  error;
    }
  });
}

function run_workflow(){
  //alert("run");
  $('.nav-tabs a[href="#output"]').tab('show');
}
