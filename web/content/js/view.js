
var uvis = {};

//////////////////////////////////////////////////////////////////////////////
/**
 * Plot object
 *
 * @param id (For example "#viewport-1")
 */
//////////////////////////////////////////////////////////////////////////////
uvis.plot = function(nodeId) {
  var m_nodeId = null,
      m_connection = null,
      m_viewport = null,
      m_this = this;

  /**
   * Get current plot type
   */
  this.getType = function() {
    // @todo: Implement this
  };

  /**
   * Set current plot type
   *
   * @param type
   */
  this.setType = function(type) {
    if (m_connection && m_connection.session) {
	    m_connection.session.call("vtk:is_initRender").then(function(res) {
	    	if (res) {
		      m_connection.session.call("vtk:setPlotType",selected).then(function(res){
            console.log("setPlotType: ready to run stillRender");
          });
        }
        else {
          m_connection.session.call("vtk:setPlotType",selected).then(function(res){
            m_connection.session.call("vtk:initRender").then(function(res) {
            });
          });
        }
	    });
    }
  };

  /**
   * Initialize plot using a valid connection
   * @param args
   */
  this.init = function(args) {
    m_connection = args.connection;
  };

  /**
   * Initialize the context
   */
  this.contextInit = function() {
    if (m_connection === null) {
      console.log("[uvis:plot] Connection cannot be null");
      return;
    }
    m_viewport = vtkWeb.createViewport({session: conn.session});
    m_viewport.bind(m_nodeId);
  };

  /**
   * Close the context
   */
  this.contextClose = function() {
    m_viewport.unbind();
    vtkweb.stop(m_connection);
  };

  /**
   * Render plot
   */
  this.render = function() {
    // @todo Provide right abstraction
    $(m_nodeId).empty();
    pv.viewport.render();
  };
};

//////////////////////////////////////////////////////////////////////////////
/**
 * View object
 */
//////////////////////////////////////////////////////////////////////////////
uvis.view = function() {
  var m_plots = [];

  /**
   * Initialize the view
   */
  this.init = function() {
    // @todo Implement this
  };

  this.contextInit = function() {
    for(plot in m_plots) {
      plot.contextInit();
    }
  };

  this.contextClose = function() {
   for(plot in m_plots) {
      plot.contextClose();
    }
  };

  this.addRenderer = function(vp) {
    //@todo add check if the viewport already exists
    m_plots.concat(vp);
  };

  this.removeRenderer = function(vp) {
    // @todo Implement this
  };

  this.render = function() {
    // @todo Implement this
    for(plot in m_plots) {
      plot.render();
    }
  };
};




