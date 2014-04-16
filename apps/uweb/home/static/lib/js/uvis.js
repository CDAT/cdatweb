
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
    url = "ws://" + location.hostname + ":8080/ws";
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
    var config = {
      sessionManagerURL: window.location.origin + "/paraview",
      sessionURL: "ws://" + location.hostname +  ":8080/ws",
      application: "uvis"
    };

    vtkWeb.smartConnect(config, function(connection) {
      m_meta.connection = connection;
      m_isConnected = true;

      typeof callback === 'function' && callback();
    },
    function(code, reason) {
      console.log(reason);
    });
  };


  /////////////////////////////////////////////////////////////////////////////
  /**
   * Disconnect and clean up backend process
   */
  /////////////////////////////////////////////////////////////////////////////
  this.disconnect = function() {

    if (m_isConnected) {
      m_meta.connection.session.call('vtk:exit');
      m_isConnected = false;
    }
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
      m_id = null,
      m_nodeId = nodeId,
      m_connection = null,
      m_viewport = null,
      m_remote = true,
      m_type = null,
      m_data = null,
      m_config = {},
      m_this = this,
      m_actions = {'blur':[], 'focus':[], 'focusin':[], 'focusout':[],
        'load':[], 'resize':[], 'scroll':[], 'unload':[], 'click':[],
        'dblclick':[], 'mousedown':[], 'mouseup':[],
        'mousemove':[], 'mouseover':[], 'mouseout':[], 'mouseenter':[],
        'mouseleave':[],'change':[], 'select':[], 'submit':[], 'keydown':[],
        'keypress':[], 'keyup':[], 'error':[]};

  if (m_remote) {
    // Remote rendered plots expect a remote connection in the argument
    if (args.hasOwnProperty("connection")) {
      m_connection = args.connection;
    } else {
      console.log("[ERROR] Remote render plots require remote connection");
    }
  }

  for (var action in m_actions) {
    if (m_actions.hasOwnProperty(action)) {
      var i = null;
      for (i = 0; i < m_actions[action].length; ++i) {
        $(m_nodeId).on(action, m_actions[action]);
      }
  }}

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
      m_connection.getSession().call("vtk:plot:setData", m_id,
        data).then(function(res){
          console.log('data is ', data);
          m_data = data;
          typeof callback === 'function' && callback();
        }, function(msg) {console.log(msg);});
    }
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Get plot configuration
   *
   * @returns {{}}
   */
  /////////////////////////////////////////////////////////////////////////////
  this.getConfig = function() {
    return m_config;
  }

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Set plot configuration
   *
   * @param config
   * @param callback
   */
  /////////////////////////////////////////////////////////////////////////////
  this.setConfig = function(config, callback) {
    if (this.hasValidConnection()) {
      m_connection.getSession().call("vtk:plot:setConfig", m_id,
        config).then(function(res){
          m_config = config;
          typeof callback === 'function' && callback();
        }, function(msg) {console.log(msg);});
    }
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Perform initialization code
   */
  /////////////////////////////////////////////////////////////////////////////
  this.init = function(plot, callback) {
    if (this.hasValidConnection()) {
      m_connection.getSession().call("vtk:createPlot", plot).then(function(res){
        m_id = res;
        console.log("M_ID: "+m_id);
        console.log("plotType in init" + plot);
        typeof callback === 'function' && callback();
      });
    } else {
      console.log("[error] Invalid connection");
    }
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Initialize the context
   */
  /////////////////////////////////////////////////////////////////////////////
  this.createContext = function(callback) {
    if (m_connection === null) {
      console.log("[plot:info] Connection cannot be null");
      return;
    }

    if (this.hasValidConnection()) {
      m_connection.getSession().call("vtk:plot:createContext", m_id).then(function(res){
        console.log("CreateContext: "+m_id);
        m_viewport = vtkWeb.createViewport({session: m_connection.getSession(),
                                        view: m_id});
        m_viewport.bind(m_nodeId);
        typeof callback === 'function' && callback();
      });
    } else {
      console.log("[error] Invalid connection");
    }
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Close the context
   */
  /////////////////////////////////////////////////////////////////////////////
  this.closeContext = function() {
    m_viewport.unbind();
    //vtkweb.stop(m_connection.getMeta());
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Render plot
   */
  /////////////////////////////////////////////////////////////////////////////
  this.render = function(options) {
    console.log('Calling m_viewport.render()');
    // @todo Provide right abstraction
    m_viewport.render();
    console.log('Called m_viewport.render()');
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Clear plot to its default background color
   */
  /////////////////////////////////////////////////////////////////////////////
  this.clear = function() {
    var ctxs = $(m_nodeId + " > .renderers > canvas");
    var i = null;

    // Find all of the canvas used by the container and clear them now
    for (i = 0 ; i < ctxs.length; ++i) {
      ctxs[i].getContext('2d').clearRect(0, 0, ctxs[i].width, ctxs[i].height);
    }
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Push current state onto stack
   */
  /////////////////////////////////////////////////////////////////////////////
  this.save = function() {
    var ctxs = $(m_nodeId + " > .renderers > canvas"),
        i = null;

    // Find all of the canvas used by the container and clear them now
    for (i = 0 ; i < ctxs.length; ++i) {
      ctxs[i].getContext('2d').save();
    }
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Restore to last state from stack
   */
  /////////////////////////////////////////////////////////////////////////////
  this.restore = function() {
    var ctxs = $(m_nodeId + " > .renderers > canvas"),
        i = null;

    // Find all of the canvas used by the container and clear them now
    for (i = 0 ; i < ctxs.length; ++i) {
      ctxs[i].getContext('2d').restore();
    }
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Bind callback to an action
   *
   * @param action {string}
   * @param callback {function}
   */
  /////////////////////////////////////////////////////////////////////////////
  this.on = function(action, callback) {
    if (!m_actions.hasOwnProperty(action)) {
      console.log('Action %s not supported', action);
      return;
    }
    $(m_nodeId).on(action, callback);
    m_actions[action].push(callback);
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Get data at given x and y position
   *
   * @param x
   * @param y
   * @param callback
   */
  /////////////////////////////////////////////////////////////////////////////
  this.getValueAt = function(evt, callback) {
    m_connection.getSession().call("vtk:plot:getValueAt", m_id, evt).then(function(data){
      typeof callback === 'function' && callback(data);
    }, function(msg){ console.log('[error] ', msg)});
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
  this.createContext = function() {
    var i;
    for(i = 0; i < m_plots.length; ++i) {
      m_plots[i].createContext();
    }
  };

  /////////////////////////////////////////////////////////////////////////////
  /**
   * Clean up on context close
   */
  /////////////////////////////////////////////////////////////////////////////
  this.closeContext = function() {
    var i;
    for(i = 0; i < m_plots.length; ++i) {
      m_plots[i].closeContext();
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

  /////////////////////////////////////////////////////////////////////////////
  /**
   *  Render view and all of its plots
   */
  /////////////////////////////////////////////////////////////////////////////
  this.render = function() {
    // @todo Implement this
    var i;
    for(i = 0; i < m_plots.length; ++i) {
      m_plots[i].render();
    }
  };
};
