function cdat_esgf_submit(){
  var host =    document.getElementById("host").value;
  console.log(host);
  var text =    $("input[id=text]").val();
  var project = $("input[id=project]").val();
  var limit =   document.getElementById("limit").value;
  //console.log(limit);
  var offset =  $("input[id=offset]").val();

  var jsonObj = new Object;
  jsonObj.host = host;
  jsonObj.text = text;
  jsonObj.project = project;
  jsonObj.limit = limit;
  jsonObj.offset = offset;

  var jsonStr = JSON.stringify(jsonObj);
  var search_url = '/vtk/search';
  $.ajax({
    type: "POST",
    url: search_url,
    async: true,
    cache: false,
    data: {query:jsonStr},
    dataType: 'json',
    success: function(data) {
      results = data.data;
      stacktop = [];
      stacktop = results;
      var element = $("<div></div>");
      if(stacktop.length == 0){
        element.text("No Results");
      }

      for(var x = 0; x < stacktop.length; x++){
        //console.log(stacktop[x]);
        obj = stacktop[x];
        var wrapper =$("<p></p>");
        var eol = "<br/>";
        var split = "<hr>";
        wrapper.append(split);

        var project = "Project: " + obj.project + eol;
        wrapper.append(project);

        var experiment ="Experiment: " + obj.experiment + eol;
        wrapper.append(experiment);

        var title ="Title: " + obj.title + eol;
        wrapper.append(title);

        var download = $("<a></a>");
        download.attr("href", obj.http).text("Download");
        wrapper.append(download);

        wrapper.append(eol + "Variables: " + eol);
        var var_wrap = $("<ul></ul>");
        
        if(obj.variables.length == 0){
          var no_vars = $("<li></li>");
          no_vars.text("No Listed Variables");
          var_wrap.append(no_vars);
        }

        for(var v = 0; v < obj.variables.length; v++){
          var variable = $("<li></li>");
          if (typeof(obj.dap) === "undefined"){
            variable.text(obj.variables[v].name);
          }
          else{
            _dap = obj.dap
            if(_dap.substring(_dap.length - 5, _dap.length) == ".html"){
              _dap = _dap.substring(0, _dap.length - 5)
            }
            var link = $("<a></a>");
            make_draggable(link);
            link.text(obj.variables[v].name)
              .attr("data-name", obj.variables[v].name)
              .attr("data-file", _dap)
              .addClass('cdat-variable');
            variable.append(link);
          }
          var_wrap.append(variable);
        }

        wrapper.append(var_wrap);
        element.append(wrapper);
      }

      title = "Search Results";
      newPanel(title, element);
    },
    error: function(request, status, error) {
      $("div .error").html(request + " | " + status + " | " + error);
      $("div .error").show();
    }
  });
}

function newPanel(title, content){
  if (typeof content === 'string') {
    content = $(content);
  }
  cdat.Panel({
    title: title,
    content: content,
    overflow: 'scroll',
    position: "center",
    size: {width: 400, height: 600}
  });
}

function emptyPanel(){
  return $.jsPanel({});
}

function get_children(path, parent, level){
  if (parent.attr("data-loaded") === "true") {
    return;
  }
  var next_level = parseInt(level) + 1;
  var parent_id = parent.attr('id');

  var jsonObj = new Object;
  jsonObj.path = path;
  var jsonStr = JSON.stringify(jsonObj);
  var search_url = '/vtk/get_children';
  $.ajax({
    type: "POST",
    url: search_url,
    async: true,
    cache: false,
    data: {query:jsonStr},
    dataType: 'json',
    success: function(data) {
      results = data.dirs;
      for(var x = 0; x < results.length; x ++){
        var short_name = results[x].split("/")
        var display_name = short_name[short_name.length - 1]
        display_name =display_name.replace("+","_");
        display_name =display_name.replace(".","_");
        var element;

        element = $("<li><a></a><ul></ul></li>");
        element.find("a").click(function(e){
          if ($(this).attr("data-loaded") === "true") {
            return;
          }
          var path = $(this).attr("data-path");
          var ul = $(this).parent().find("ul");
          get_children(path, ul, next_level);
          $(this).attr('data-loaded', "true");
        }).text(display_name).attr("data-path", results[x]);
        element.find("ul").attr("id", parent_id + "_" + display_name);
        parent.append(element);
      }
      results = data.files;
      for(var x = 0; x < results.length; x ++){
        var short_name = results[x].split("/")
        var display_name = short_name[short_name.length - 1]
        display_name =display_name.replace("+","_");
        display_name =display_name.replace(".","_");
        var element;

        element = $("<li><a></a><ul></ul></li>");
        element.find("a").click(function(e){
          if ($(this).attr("data-loaded") === "true") {
            return;
          }
          var path = $(this).attr("data-path");
          var ul = $(this).parent().find("ul");
          get_variables(path, ul, next_level);
          $(this).attr('data-loaded', "true");
        }).text(display_name).attr("data-path", results[x]);
        element.find("ul").attr("id", parent_id + "_" + display_name);
        parent.append(element);
      }
    },
    error: function(request, status, error) {
      console.log(status + " | " + error)
    }
  });
}

function get_variables(path, parent, level){
  //cdat.get_variables("/var/www/Data/ne120_monthly_ens3/gridded/1979/gridded_ne120_v0.3_00003.cam.h0.1979-01.nc").then(
  //testing above
  cdat.get_variables(path).then(
    function (variables){
    for(v in variables){
      element = $("<li><a></a></li>");
      make_draggable(element);
      element.text(v)
      .attr("data-name", v)
      .attr("data-file", path)
      .addClass('cdat-variable');
      parent.append(element);
    }
  }, function(){console.log(arguments)}
  )
}

function get_plot(path, parent, level){
  console.log("get_plot")
}

/**
 * Make the given element draggable.
 * @param {jQuery} node A jquery DOM element
 * @param {function?} ondrag A drag event handler
 */
function make_draggable(node, ondrag) {
  node.draggable({
    appendTo: '.vtk-view-container',
    zIndex: ~(1 << 31), // because jsPanel, sigh...
    containment: '.vtk-view-container',
    helper: "clone",
    addClass: "cdat-grabbing",
    opacity: 0.75
  }).addClass('cdat-draggable')
  .on('start', function (evt) {
    if (ondrag) {
      ondrag.call(node, evt);
    }
  });

  return node;
}

$("body").ready(function(){

  $(".cdatweb-file-browser > ul > li > a.cdatweb-dir").click(function(e){
    if ($(this).attr("data-loaded") === "true") {
      return;
    }
    get_children($(this).attr("data-path"), $(this).next("ul"), 1);
    $(this).attr('data-loaded', 'true');
    e.preventDefault();
  });

  $(".cdatweb-file-browser > ul > li > a.cdatweb-file").click(function(e){
    if ($(this).attr("data-loaded") === "true") {
      return;
    }
    get_variables($(this).attr("data-path"), $(this).next("ul"), 1);
    $(this).attr('data-loaded', 'true');
    e.preventDefault();
  });

  cdat.get_graphics_methods().then(
    function(plots){
    parent = $(".cdatweb-plot-types");
    var item = $("<li><a></a><ul class='qtree'></ul></li>");
    var child = $("<li><a></a></li>");
    var plot_fam_item, plot_family, plot_item;
    for (plot_family in plots) {
      if (plots.hasOwnProperty(plot_family) === false) {
        continue;
      }

      plot_fam_item = item.clone();

      plot_fam_item.attr('id', plot_family);
      plot_fam_item.find('a').text(plot_family);

      for(plot_type in plots[plot_family]){
        plot_item = child.clone();
        plot_item.attr('id', plot_type);
        plot_item
        .addClass('cdat-plot-method')
        .attr('data-type', plot_type)
        .attr('data-family', plot_family)
        .attr('data-nvars', plots[plot_family][plot_type].nvars)
        .text(plot_type);
        plot_item.hide();
        make_draggable(plot_item);
        plot_fam_item.find("ul").append(plot_item);
      }
      parent.append(plot_fam_item);
      plot_fam_item.hide();
    }
  },
  function(){
    console.log(arguments)
  }
  );

  cdat.get_templates().then(
    function(templates){
    parent = $(".cdatweb-plot-templates");
    var item = $("<li><a></a><ul class='qtree'></ul></li>");
    var temp_fam_item, temp_name;
    for(temp_name = 0; temp_name < templates.length; temp_name++) {
      temp_fam_item = item.clone();
      temp_fam_item.attr('id', templates[temp_name])
      .text(templates[temp_name])
      .addClass('cdat-template-option');
      make_draggable(temp_fam_item);
      parent.append(temp_fam_item);
      temp_fam_item.hide();
    }

  },
  function(){
    console.log(arguments)
  }
  );
  $(".qtree").quicktree();
  
  $(".cdat-search-link").click(function () {
    if ($(".cdat-search-container").get(0)) {
      return;
    }

    $(".cdat-search-container").remove();
    $("<div/>").addClass("cdat-search-container")
    .appendTo(".vtk-view-container");

    $.ajax('/fragments/search')
    .then(function (data) {
      $('.cdat-search-container').html(data);
      cdat.make_panel(
        $('.cdat-search-container').get(0),
        '',
        {
          title: '<span><i class="fa fa-search"></i>ESGF search</span>',
          size: 'auto',
          overflow: 'scroll'
        }
      );
    }, function () {
      console.log('search fragment load failed.');
      $('.cdat-search-container').remove();
    });
  });
});

