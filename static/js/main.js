function submit(){
  var host =    document.getElementById("host").value;
  console.log(host);
  var text =    $("input[id=text]").val();
  var project = $("input[id=project]").val();
  var limit =   document.getElementById("limit").value;
  console.log(limit);
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
          html = "<div><ul>"
          for(var x = 0; x < stacktop.length; x++){
            //console.log(stacktop[x]);
            obj = stacktop[x];
            /*
            obj example
              dap: "http://esgdata1.nccs.nasa.gov/thredds/dodsC/NEX/dataportal/NEX/downscaled/NASA-Ames/BCSD/historical/mon/atmos/pr/r1i1p1/v1.0/CONUS/pr_amon_BCSD_historical_r1i1p1_CONUS_FGOALS-g2_199501-199912.nc.html"
              experiment: "decadal2005"
              http: "http://adm07.cmcc.it/thredds/fileServer/esg_dataroot/cmip5/output1/CMCC/CMCC-CM/decadal2005/mon/atmos/cct/r1i1p1/cct_Amon_CMCC-CM_decadal2005_r1i1p1_200511-201512.nc"
              id: null
              metadata_format: null
              node: null
              project: "CMIP5"
              regridding: null
              size: 56245984
              timestamp: "2012-03-06T23:52:36Z"
              title: "cct_Amon_CMCC-CM_decadal2005_r1i1p1_200511-201512.nc"
              type: null
              urls: Array[1]
              variables: Array[0]
            */
            html = html + "<li>Project: " + obj.project + "<br/>" +
                          "Experiment: " + obj.experiment + "<br/>" +
                          "Title: " + obj.title + "<br/>" +
                          "<a href=\"" + obj.http + "\">Downlaod</a><br/>";

            html = html + "Variables: ";
            for(var v = 0; v < obj.variables.length; v++){
              if (typeof(obj.dap) === "undefined"){
                html = html + " " + obj.variables[v].name + "&nbsp;";
                html = html + "Variables: ";
                for(var v = 0; v < obj.variables.length; v++){
                  if (typeof(obj.dap) === "undefined"){
                    html = html + " " + obj.variables[v].name + "&nbsp;";
                  }
                  else{
                    _dap = obj.dap
                    if(_dap.substring(_dap.length - 5, _dap.length) == ".html"){
                      _dap = _dap.substring(0, _dap.length - 5)
                    }
                    html = html + " <a  onclick=\"cdat.create_plot('" + _dap + "', '" + obj.variables[v].name + "')\"  href=\"javascript:void(0)\">" + obj.variables[v].name + "</a> &nbsp;";
                  }
                }


                html = html + "</li><hr>";
              }
            }
          }

        exampleURL = "http://test.opendap.org/dap/netcdf/examples/cami_0000-09-01_64x128_L26_c030918.nc";
        exampleVAR = "TS"; //rsut - ua - wap
        html = html + "<li><a onclick=\"cdat.create_plot('" + exampleURL + "', '" + exampleVAR + "', 'Isofill')\" href=\"javascript:void(0)\">Isofill iexample</a>";

        exampleURL = "http://test.opendap.org/dap/netcdf/examples/cami_0000-09-01_64x128_L26_c030918.nc";
        exampleVAR = "T"; //rsut - ua - wap
        html = html + "<li><a onclick=\"cdat.create_plot('" + exampleURL + "', '" + exampleVAR + "', 'Volume')\" href=\"javascript:void(0)\">Volume example</a>";

        exampleURL = "http://test.opendap.org/dap/netcdf/examples/cami_0000-09-01_64x128_L26_c030918.nc";
        html = html + "<li><a onclick=\"cdat.create_plot('" + exampleURL + "', ['U', 'V'], 'Vector3D')\" href=\"javascript:void(0)\">Vector3D example</a>";

        html = html + "</ul></div>";
        title = "Search Results";
        newPanel(title, html);
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
      results = []
      results = data.files
      for(var x = 0; x < results.length; x ++){
        var short_name = results[x].split("/")
        var display_name = short_name[short_name.length - 1]
        display_name =display_name.replace("+","_");
        display_name =display_name.replace(".","_");
        var element;

        element = $("<li><a></a><ul></ul></li>");
        element.addClass("mtree-node mtree-closed");
        element.find("a").click(function(e){
          var path = $(this).attr("data-path");
          var ul = $(this).parent().find("ul");
          console.log(path);
          if(path.indexOf(".") > -1){
            //file
            get_variables(path, ul, next_level);
          }
          else{
            //folder
            get_children(path, ul, next_level);
          }
          e.preventDefault();
        }).text(display_name).attr("data-path", results[x]);
        element.find("ul").attr("id", parent_id + "_" + display_name).addClass("mtree-level-" + next_level);
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
    function (variables){
      for(v in variables){
        element = $("<li><a></a></li>");
        element.find("a").click(function(e){
          var path = $(this).attr("data-path");
          var li = $(this).parent().find("li");
          get_plot(path, ul.attr('id'), level + 1);
          e.preventDefault();
        }).text(v).attr("data-path", v);
        parent.append(element);
      }
    }, function(){console.log(arguments)}
  )
}

function get_plot(path, parent, level){
  console.log("get_plot")
}

$("body").ready(function(){

  $(".cdatweb-file-browser  .mtree.bubba > li > a").click(function(e){
    get_children($(this).attr("data-path"), $(this).next("ul"), 1);
    e.preventDefault();
  });
});
