
var uvis = {};

//////////////////////////////////////////////////////////////////////////////
/**
 * Remote connection object
 *
 * @param url (Default is ws://localhost:8080/ws)
 */
//////////////////////////////////////////////////////////////////////////////
uvis.remoteConnection = function (url) {
  var m_meta = {},
      m_isConnected = false;

  // Use localhost by default
  if (typeof url === 'undefined') {
    url = ws://localhost:8080/ws;
  }
  m_meta.connection = {sessionURL: url};

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Check if connection is active
   *
   * @returns {boolean}
   */
  /////////////////////////////////////////////////////////////////////////////
  this.isConnected = function() {
    return m_isConnected;
  }

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Make a connection request.
   *
   * This is async call. Check using isConnected() call if the
   * connection was successful.
   *
   * @param callback function
   */
  /////////////////////////////////////////////////////////////////////////////
  this.connect = function(callback) {
    if(location.protocol == "http:") {
      m_meta.connection.sessionURL = m_meta.connection.sessionURL.replace("wss:","ws:");
    }

    vtkWeb.connect(m_meta.connection, function(connectionData) {
      m_meta.connection = connectionData;
      m_isConnected = true;
      callback();
    });
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Get websocket connection handler
   */
  /////////////////////////////////////////////////////////////////////////////
  this.getMeta = function() {
    return m_meta;
  }
};

//////////////////////////////////////////////////////////////////////////////
/**
 * Plot object
 *
 * @param id (For example "#viewport-1")
 */
//////////////////////////////////////////////////////////////////////////////
uvis.plot = function(nodeId, args) {
  var m_nodeId = nodeId,
      m_connection = null,
      m_viewport = null,
      m_remoteRendering = true,
      m_this = this;

  if (m_remoteRendering) {
    // Remote rendered plots expect a remote connection in the argument
    if (args.hasOwnProperty(remoteConn)) {
      m_connection = args.remoteConn;
    } else {
      console.log("[ERROR] Remote render plots require remote connection");
    }
  }

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Get current plot type
   */
  /////////////////////////////////////////////////////////////////////////////
  this.getType = function() {
    // @todo: Implement this
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Set current plot type
   *
   * @param type
   */
  /////////////////////////////////////////////////////////////////////////////
  this.setType = function(type) {
    if (m_connection && m_connection.getMeta().session) {
	    m_connection.getMeta().session.call("vtk:is_initRender").then(
        function(res) {
          if (res) {
            m_connection.getMeta().session.call("vtk:setPlotType",selected).then(
              function(res){
                console.log("setPlotType: ready to run stillRender");
              });
          }
          else {
            m_connection.getMeta().session.call("vtk:setPlotType",selected).then(
              function(res) {
                m_connection.getMeta().session.call("vtk:initRender").then(
                  function(res) {
                  });
              });
          }
        }
      );
    }
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Initialize the context
   */
  /////////////////////////////////////////////////////////////////////////////
  this.contextInit = function() {
    if (m_connection === null) {
      console.log("[uvis:plot] Connection cannot be null");
      return;
    }
    m_viewport = vtkWeb.createViewport({session: m_connection.getMeta().session});
    m_viewport.bind(m_nodeId);
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Close the context
   */
  /////////////////////////////////////////////////////////////////////////////
  this.contextClose = function() {
    m_viewport.unbind();
    vtkweb.stop(m_connection.getMeta());
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Render plot
   */
  /////////////////////////////////////////////////////////////////////////////
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

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Initialize context specific data
   */
  /////////////////////////////////////////////////////////////////////////////
  this.contextInit = function() {
    var plot;
    for(plot in m_plots) {
      plot.contextInit();
    }
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Clean up on context close
   */
  /////////////////////////////////////////////////////////////////////////////
  this.contextClose = function() {
    var plot;
    for(plot in m_plots) {
      plot.contextClose();
    }
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Add new plot to the view.
   *
   * @param {uvis.plot} vp
   */
  /////////////////////////////////////////////////////////////////////////////
  this.addPlot = function(vp) {
    //@todo add check if the viewport already exists
    m_plots.concat(vp);
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Remove a plot from the view
   *
   * @param {uvis.plot} vp
   */
  /////////////////////////////////////////////////////////////////////////////
  this.removePlot = function(vp) {
    // @todo Implement this
  };

  this.render = function() {
    // @todo Implement this
    var plot;
    for(plot in m_plots) {
      plot.render();
    }
  };
};