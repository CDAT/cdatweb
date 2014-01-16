
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
    url = "ws://localhost:8080/ws";
  }
  m_meta.connection = {sessionURL: url};

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Return session object
   *
   * @returns {*}
   */
  /////////////////////////////////////////////////////////////////////////////
  this.getSession = function() {
    return m_meta.connection.session;
  }

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

      typeof callback === 'function' && callback();
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
  var m_name = "default",
      m_nodeId = nodeId,
      m_connection = null,
      m_viewport = null,
      m_remote = true,
      m_type = null,
      m_data = null,
      m_this = this;

  if (m_remote) {
    // Remote rendered plots expect a remote connection in the argument
    if (args.hasOwnProperty("connection")) {
      m_connection = args.connection;
    } else {
      console.log("[ERROR] Remote render plots require remote connection");
    }
  }

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Check if the plot has valid remote connection (for remote render plots)
   *
   * @returns {null|*}
   */
  /////////////////////////////////////////////////////////////////////////////
  this.hasValidConnection = function() {
    return (m_connection && m_connection.getSession());
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Get current plot type
   */
  /////////////////////////////////////////////////////////////////////////////
  this.getType = function() {
    return m_type;
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Set current plot type
   *
   * @param type
   */
  /////////////////////////////////////////////////////////////////////////////
  this.setType = function(type, callback) {
    if (this.hasValidConnection()) {
      m_connection.getSession().call("vtk:setPlotType", type).then(
        function(res){
          m_type = type;

          typeof callback === 'function' && callback();
        });
    }
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Get plot data
   */
  /////////////////////////////////////////////////////////////////////////////
  this.getData = function() {
    return m_data;
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Set data (input) for the plot.
   */
  /////////////////////////////////////////////////////////////////////////////
  this.setData = function(data, callback) {
    if (this.hasValidConnection()) {
      m_connection.getSession().call("vtk:setFileName",data).then(function(res){
        m_data = data;

        typeof callback === 'function' && callback();
      });
    }
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Initialize the context
   */
  /////////////////////////////////////////////////////////////////////////////
  this.contextInit = function() {
    if (m_connection === null) {
      console.log("[plot:info] Connection cannot be null");
      return;
    }
    m_viewport = vtkWeb.createViewport({session: m_connection.getSession()});
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
    m_viewport.render();
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
    var i;
    for(i = 0; i < m_plots.length; ++i) {
      m_plots[i].contextInit();
    }
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Clean up on context close
   */
  /////////////////////////////////////////////////////////////////////////////
  this.contextClose = function() {
    var i;
    for(i = 0; i < m_plots.length; ++i) {
      m_plots[i].contextClose();
    }
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Add new plot to the view.
   *
   * @param {uvis.plot} plot
   */
  /////////////////////////////////////////////////////////////////////////////
  this.addPlot = function(plot) {
    // @todo check if the plot already exists
    m_plots.push(plot);
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
    var i;
    for(i = 0; i < m_plots.length; ++i) {
      m_plots[i].render();
    }
  };
};