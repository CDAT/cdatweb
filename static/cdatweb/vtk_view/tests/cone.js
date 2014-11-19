$(function () {
  'use strict';

  function start(connection) {
    var viewport = vtkWeb.createViewport({
      session: connection.session
    });

    viewport.bind('.vtk-view-container');
  }

  var config = {
    sessionURL: 'ws://localhost:8001/ws',
    application: 'cone'
  };

  vtkWeb.smartConnect(config, start, function (code, reason) {
    console.log(reason);
  });
});
