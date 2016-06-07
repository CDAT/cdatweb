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
            //make_draggable(link); Variables are now click to select
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

      //title = "Search Results";
      //newPanel(title, element);
      $('#esgf_results').empty();
      $('#esgf_results').append(element);
    },
    error: function(request, status, error) {
      $("div .error").html(request + " | " + status + " | " + error);
      $("div .error").show();
    }
  });
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
  cdat.get_variables("/var/www/Data/ne120_monthly_ens3/gridded/1979/gridded_ne120_v0.3_00003.cam.h0.1979-01.nc").then(
  //testing above
  //cdat.get_variables(path).then(
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


function make_draggable(node, ondrag) {
  /**
  * Make the given element draggable.
  * @param {jQuery} node A jquery DOM element
  * @param {function?} ondrag A drag event handler
  */  
  node.draggable({
    appendTo: 'body',
    zIndex: ~(1 << 31), // because jsPanel, sigh...
    containment: 'body',
    helper: "clone",
    addClass: "cdat-grabbing",
    opacity: 0.75,
    cursor: "grabbing",
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
  
  $("#reset").click(function() {
      $('#esgf_results').empty();
  });
  
  /* grid */
  count = 1;

  function resizeWindows() {
    var curWindows = $('.window');
    if (curWindows.length < 3) {
      curWindows.removeClass('window-half');
      curWindows.addClass('window-full');
    } else {
      curWindows.removeClass('window-full');
      curWindows.addClass('window-half');
    }
    if (curWindows.length % 2 === 1) {
      curWindows.last().addClass('full-width');
    } else {
      curWindows.removeClass('full-width');
    }
  }

  $("#container").sortable().disableSelection();


  $("#container").on("sortstart", function(event, ui) {
    if ($('.window').not('.ui-sortable-placeholder').length % 2 === 1) {
      $('.window').removeClass('full-width');
    }
  });

  $("#container").on("sortstop", function(event, ui) {
    if ($('.window').not('.ui-sortable-placeholder').length % 2 === 1) {
      $('.window').last().addClass('full-width');
    }
  });

  $('#new_window_button').on('click', function() {
    var elem = $('<li/>').addClass('window window-half col-xs-4 ui-state-default panel panel-info');
    /* add droppable fields info */
    var button = '<button class="window-close-button btn btn-default pull-right">Close</button>';
    //$(elem).text('Added window ' + count);
    var variableZone = $('<div/>').text('Variable').addClass('drop-zone variable').attr('title', 'Drag and drop a variable here').droppable({
      accept: '.cdat-variable',
      activeClass: 'alert drop-zone-highlight',
      hoverClass: 'alert drop-zone-success',
      tolerance: 'pointer',
      drop: function (event, ui) {
        $(this).text(ui.draggable.text())
          .attr('data-file', ui.draggable.attr('data-file'))
          .attr('data-name', ui.draggable.attr('data-name'));

        var variable = this;
        var method = $(this).siblings(".drop-zone.method");
        var template = $(this).siblings(".drop-zone.template");
        
        if($(template).text() !== 'Template' && $(method).text() !== 'Method'){
          console.log('rendering');
          cdat.show({
            file: $(variable).attr('data-file'),
            variable: $(variable).attr('data-name'),
            type: $(method).attr('data-family'),
            method: $(method).attr('data-type'),
            template: $(template).text(),
            node: $(this).parent()
          });
        }
      }
    });
    var methodZone = $('<div/>').text('Method').addClass('drop-zone method').attr('title', 'Drag and drop a method here').droppable({
      accept: '.cdat-plot-method',
      activeClass: 'alert drop-zone-highlight',
      hoverClass: 'alert drop-zone-success',
      tolerance: 'pointer',
      drop: function (event, ui) {
        //store method data on droppable
        $(this).text(ui.draggable.text())
        .attr('data-type', ui.draggable.attr('data-type'))
        .attr('data-family', ui.draggable.attr('data-family'))
        .attr('data-nvars', ui.draggable.attr('data-nvars'));

        //set up variables
        var variable = $(this).siblings(".drop-zone.variable");
        var method = this;
        var template = $(this).siblings(".drop-zone.template");

        //check if we can render and call cdat show if we can
        if($(template).text() !== 'Template' && $(variable).text() !== 'Variable'){
          console.log('rendering');
          cdat.show({
            file: $(variable).attr('data-name'),
            variable: $(variable).attr('data-file'),
            type: $(method).attr('data-family'),
            method: $(method).attr('data-type'),
            template: $(template).text(),
            node: $(this).parent()
          });
        }
      }

    });
    var templateZone = $('<div/>').text('Template').addClass('drop-zone template').attr('title', 'Drag and drop a template here').droppable({
      accept: '.cdat-template-option',
      activeClass: 'alert drop-zone-highlight',
      hoverClass: 'alert drop-zone-success',
      tolerance: 'pointer',
      drop: function (event, ui) {
        $(this).text(ui.draggable.text());

        //set up variables
        var variable = $(this).siblings(".drop-zone.method");
        var method = $(this).siblings(".drop-zone.method");
        var template = this;

        //check if we can render and call cdat show if we can
        if( method.text() !== 'Method' && variable.text() !== 'Variable'){
          console.log('rendering');
          cdat.show({
            file: variable.attr('data-name'),
            variable: variable.attr('data-file'),
            type: method.attr('data-family'),
            method: method.attr('data-type'),
            template: $(template).text(),
            node: $(this).parent()
          });
        }
      }
    });
    var plotcontainer = $('<div/>').addClass('plot-container')
        .append(variableZone)
        .append(methodZone)
        .append(templateZone);
    $(elem).append(plotcontainer).append(button);
    /* append droppable info */

    count++;
    $('#container').append(elem);
    resizeWindows();
  });

  $(document.body).on("click", ".window-close-button", function() {
    $(this).closest('.window').remove();
    resizeWindows();
  });

  $("#file-browser-add-variables").click(function() {
      var elems = $('.variable-selected');
      elems.each(function() {
        var elem = $('<p/>').text($(this).text())
            .attr('data-file', $(this).attr('data-file'))
            .attr('data-name', $(this).attr('data-name'))
            .addClass('cdat-variable');
        make_draggable(elem);
        $('#variables-output').append(elem);
        $(this).removeClass('variable-selected');
      });
  });

  $("#variable-plus").click(function() {
    $('.variable-selected').removeClass('variable-selected');
  });

  $("#variable-remove").click(function() {
    $('.variable-selected').remove();
  });

  $(document.body).on("click", ".cdat-variable", function() {
      if($(this).hasClass('variable-selected')){
        $(this).removeClass('variable-selected');
      }
      else {
        $(this).addClass('variable-selected');
      }
  });
  

});



